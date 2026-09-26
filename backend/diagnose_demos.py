"""
Diagnostic script to test the 3 current demo candidates through the real CodeShift pipeline.
Captures exact commands, package manager, exit codes, stdout, stderr, and failure reasons.
"""

import sys
import json
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services import intake, scanner, baseline, migration, twin, verification, store
from app.models.rehearsal import Rehearsal, RepositorySource, TargetUpgrade, RehearsalStage, RehearsalStatus
from app.models.baseline import BaselineStatus, StepStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

CANDIDATES = [
    ("howtotax", "https://github.com/taepras/howtotax"),
    ("cocos-can-i-use-npm", "https://github.com/cocos/cocos-can-i-use-npm"),
    ("observablehq-plot-cra-example", "https://github.com/observablehq/plot-create-react-app-example"),
]

def test_candidate(demo_id: str, repo_url: str):
    print(f"\n=======================================================")
    print(f"TESTING CANDIDATE: {demo_id} ({repo_url})")
    print(f"=======================================================")
    
    rehearsal_id = f"cert-{demo_id}"
    rehearsal = Rehearsal(
        id=rehearsal_id,
        repository=RepositorySource(url=repo_url, is_demo=True),
        target_upgrade=TargetUpgrade(package="react", to_version="18.0.0", from_version="17.0.2"),
        status=RehearsalStatus.RUNNING,
        stage=RehearsalStage.INTAKE,
    )
    store.save_rehearsal(rehearsal)

    # 1. Clone
    print("\n--- 1. CLONE ---")
    try:
        workspace = intake.clone_repository(repo_url)
        print(f"Clone successful: {workspace}")
    except Exception as exc:
        print(f"CLONE FAILED: {exc}")
        return False

    # 2. Scan
    print("\n--- 2. SCAN ---")
    try:
        profile = scanner.scan_repository(workspace, rehearsal_id)
        profile.source_url = repo_url
        store.save_repo_profile(profile)
        print(f"Scan complete: PM={profile.package_manager.value}, scripts={list((profile.raw_manifest or {}).get('scripts', {}).keys())}")
    except Exception as exc:
        print(f"SCAN FAILED: {exc}")
        return False

    # 3. Baseline
    print("\n--- 3. BASELINE ---")
    try:
        base_res = baseline.run_baseline(workspace, profile, rehearsal_id)
        print(f"Baseline finished: status={base_res.status}, passed={base_res.passed}")
        for step in ("install", "build", "test", "lint"):
            res = getattr(base_res, step, None)
            if res:
                print(f"  Step '{step}': status={res.status.value}, exit={res.exit_code}, duration={res.duration_seconds}s")
                if res.exit_code != 0 and res.stderr:
                    print(f"    stderr: {res.stderr[:400]}")
    except Exception as exc:
        print(f"BASELINE EXCEPTION: {exc}")
        return False

    # 4. Migration Analysis
    print("\n--- 4. MIGRATION ANALYSIS ---")
    try:
        plan = migration.analyze(rehearsal_id, profile, rehearsal.target_upgrade, is_demo=True)
        store.save_migration_plan(plan)
        print(f"Plan created: findings={len(plan.findings)}, actions={len(plan.planned_actions)}")
    except Exception as exc:
        print(f"ANALYSIS FAILED: {exc}")
        return False

    # 5. Twin
    print("\n--- 5. TWIN ---")
    try:
        tw = twin.create_twin(workspace, rehearsal_id)
        store.save_twin_result(tw)
        print(f"Twin created: path={tw.twin_path}")
    except Exception as exc:
        print(f"TWIN FAILED: {exc}")
        return False

    # 6. Migrate
    print("\n--- 6. MIGRATE ---")
    from app.services import executor
    try:
        tw = executor.execute_migration(tw, plan)
        store.save_twin_result(tw)
        print(f"Migration executed: status={tw.migration_status.value}, changed_files={len(tw.changed_files)}")
    except Exception as exc:
        print(f"MIGRATION FAILED: {exc}")
        return False

    # 7. Verification
    print("\n--- 7. VERIFICATION ---")
    from app.models.verification import VerificationContext
    try:
        ver = verification.run_verification(
            twin_path=Path(tw.twin_path),
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=base_res,
            context=VerificationContext.POST_MIGRATION,
            round_num=1,
        )
        print(f"Verification round 1: passed={ver.passed}, regressions={ver.regression_count}")
        for step in ("install", "build", "test", "lint"):
            res = getattr(ver, step, None)
            if res:
                print(f"  Twin Step '{step}': status={res.status.value}, exit={res.exit_code}")
    except Exception as exc:
        print(f"VERIFICATION FAILED: {exc}")
        return False

    print(f"\n=> CANDIDATE {demo_id}: CERTIFICATION SUCCESSFUL!")
    return True

if __name__ == "__main__":
    for demo_id, url in CANDIDATES:
        test_candidate(demo_id, url)
