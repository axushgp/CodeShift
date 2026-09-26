"""
Rehearsals API — Repository Intake + Scan + Baseline + Migration Analysis + Twin + Migration + Verification.

POST /api/rehearsals                  — create and run a new rehearsal (URL or ZIP)
GET  /api/rehearsals/{id}             — retrieve rehearsal state + profile + baseline
POST /api/rehearsals/{id}/analyze     — trigger migration analysis, returns MigrationPlan
POST /api/rehearsals/{id}/migrate     — create Twin and execute migration
POST /api/rehearsals/{id}/verify      — run verification → diagnosis → repair inside Twin
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel

from app.models.agent_task import AgentTaskSpec
from app.models.baseline import BaselineResult, BaselineStatus, StepStatus
from app.models.migration_plan import MigrationPlan
from app.models.rehearsal import (
    Rehearsal,
    RehearsalStage,
    RehearsalStatus,
    RepositorySource,
    TargetUpgrade,
)
from app.models.repository_profile import RepositoryProfile
from app.models.twin import TwinResult
from app.models.verification_run import DiagnosisRecord, RepairRecord, VerificationRun
from app.services import agent_pack as agent_pack_svc
from app.services import baseline as baseline_svc
from app.services import diagnosis as diagnosis_svc
from app.services import executor as executor_svc
from app.services import failure_clustering as clustering_svc
from app.services import intake as intake_svc
from app.services import migration as migration_svc
from app.services import repair as repair_svc
from app.services import scanner as scanner_svc
from app.services import store
from app.services import twin as twin_svc
from app.services import verification as verification_svc
from app.services import demos as demos_svc
from app.services.watsonx_client import WatsonxError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rehearsals", tags=["Rehearsals"])


# ── Request / Response schemas ─────────────────────────────────────────────────

class StartRehearsalRequest(BaseModel):
    """JSON body for starting a rehearsal from a public Git URL."""

    repository_url: str
    target_package: str
    target_version: str
    from_version: Optional[str] = None
    is_demo: bool = False


class RehearsalResponse(BaseModel):
    """Full rehearsal state returned from GET or POST."""

    rehearsal: Rehearsal
    repo_profile: Optional[RepositoryProfile] = None
    baseline: Optional[BaselineResult] = None
    migration_plan: Optional[MigrationPlan] = None
    twin_result: Optional[TwinResult] = None
    verification_run: Optional[VerificationRun] = None
    agent_task_spec: Optional[AgentTaskSpec] = None
    has_agent_pack: bool = False


class AgentPackResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/agent-pack."""

    rehearsal_id: str
    spec: AgentTaskSpec
    files: list[str]


class ImplementationPromptResponse(BaseModel):
    """Response from GET /api/rehearsals/{id}/implementation-prompt."""

    rehearsal_id: str
    prompt: str


class AnalyzeResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/analyze."""

    rehearsal_id: str
    migration_plan: MigrationPlan


class MigrateResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/migrate."""

    rehearsal_id: str
    twin_result: TwinResult


class VerifyResponse(BaseModel):
    """Response from POST /api/rehearsals/{id}/verify."""

    rehearsal_id: str
    verification_run: VerificationRun


# ── Background pipelines ───────────────────────────────────────────────────────

def _run_twin_and_migrate(rehearsal_id: str) -> None:
    """
    Synchronous pipeline: TWIN_CREATING → MIGRATING.

    Called from the /migrate endpoint via BackgroundTasks.
    The original workspace (repository.local_path) is read but never modified.
    """
    twin: Optional[TwinResult] = None
    try:
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal is None:
            logger.error("_run_twin_and_migrate: rehearsal %s not found", rehearsal_id)
            return

        local_path = rehearsal.repository.local_path
        if not local_path:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No local workspace path recorded on rehearsal.",
            )
            return

        workspace = Path(local_path)
        if not workspace.exists():
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Workspace path does not exist: {local_path}",
            )
            return

        plan = store.load_migration_plan(rehearsal_id)
        if plan is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No migration plan found. Run /analyze first.",
            )
            return

        # ── TWIN_CREATING ────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.TWIN_CREATING)
        try:
            twin = twin_svc.create_twin(workspace, rehearsal_id)
        except twin_svc.TwinError as exc:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Twin creation failed: {exc}",
            )
            return

        store.save_twin_result(twin)
        logger.info(
            "Twin created for rehearsal %s at %s (method=%s)",
            rehearsal_id,
            twin.twin_path,
            twin.method.value,
        )

        # ── MIGRATING ────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.MIGRATING)
        twin = executor_svc.execute_migration(twin, plan)
        store.save_twin_result(twin)

        from app.models.twin import MigrationStatus
        if twin.migration_status == MigrationStatus.FAILED:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=twin.error_message or "Migration execution failed.",
            )
        else:
            # Leave the rehearsal in MIGRATING / RUNNING so Session 5 can pick it up.
            # Mark status COMPLETE for the MVP (verification is Session 5).
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.MIGRATING,
                status=RehearsalStatus.COMPLETE,
            )
            logger.info(
                "Migration complete for rehearsal %s: status=%s, changed=%d files",
                rehearsal_id,
                twin.migration_status.value,
                len(twin.changed_files),
            )

    except Exception as exc:
        logger.exception("Unexpected error in _run_twin_and_migrate for %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        # Do NOT clean up the twin on unexpected failure — preserve for diagnosis.



def _finalize_and_save_agent_pack(
    rehearsal_id: str,
    final_stage: RehearsalStage,
    final_status: RehearsalStatus,
) -> None:
    """Generate and persist AgentTaskSpec and CodeShift-Agent-Pack/ files."""
    store.update_rehearsal_stage(
        rehearsal_id, RehearsalStage.FINALIZING, status=RehearsalStatus.RUNNING
    )
    rehearsal = store.load_rehearsal(rehearsal_id)
    if not rehearsal:
        return
    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    plan = store.load_migration_plan(rehearsal_id)
    twin = store.load_twin_result(rehearsal_id)
    ver_run = store.load_latest_verification_run(rehearsal_id)

    spec = agent_pack_svc.build_agent_task_spec(
        rehearsal=rehearsal,
        profile=profile,
        baseline=baseline,
        plan=plan,
        twin=twin,
        ver_run=ver_run,
    )
    store.save_agent_task_spec(spec)
    pack_files = agent_pack_svc.generate_agent_pack_files(spec, plan, twin, ver_run)
    agent_pack_svc.save_agent_pack(rehearsal_id, pack_files)

    store.update_rehearsal_stage(rehearsal_id, final_stage, status=final_status)
    logger.info(
        "Agent Pack finalized for rehearsal %s with status %s",
        rehearsal_id,
        final_status.value,
    )


def _run_verify_pipeline(rehearsal_id: str) -> None:
    """
    Synchronous pipeline: VERIFYING → DIAGNOSING → REPAIRING → VERIFYING → FINALIZING.

    Flow:
      1. Run verification (install/build/test/lint) inside the existing Twin.
      2. Extract failure clusters from failed steps.
      3. For migration-relevant failures: call Watsonx diagnosis.
      4. Apply safe targeted repairs inside the Twin.
      5. Re-run verification (round 2).
      6. Finalize: build AgentTaskSpec and generate Agent Pack.
      7. Set final rehearsal status: COMPLETE (VERIFIED) or REQUIRES_HUMAN_REVIEW.

    The original workspace is never modified.
    """
    try:
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal is None:
            logger.error("_run_verify_pipeline: rehearsal %s not found", rehearsal_id)
            return

        twin = store.load_twin_result(rehearsal_id)
        if twin is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No twin result found. Run /migrate first.",
            )
            return

        baseline = store.load_baseline(rehearsal_id)
        if baseline is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No baseline found. Re-run the full rehearsal.",
            )
            return

        profile = store.load_repo_profile(rehearsal_id)
        if profile is None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message="No repository profile found.",
            )
            return

        plan = store.load_migration_plan(rehearsal_id)
        twin_path = Path(twin.twin_path)
        if not twin_path.exists():
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=f"Twin path no longer exists: {twin.twin_path}",
            )
            return

        from app.models.verification import VerificationContext

        # ── Round 1: VERIFYING ───────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver1 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_MIGRATION,
            round_num=1,
        )

        run1 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=1,
            verification=ver1,
        )

        if ver1.passed and ver1.regression_count == 0:
            # Migration passed cleanly — no diagnosis needed
            run1.passed = True
            run1.summary = "All checks passed after migration. No regressions detected."
            store.save_verification_run(run1)
            logger.info("Rehearsal %s: VERIFIED after round 1", rehearsal_id)
            _finalize_and_save_agent_pack(
                rehearsal_id, RehearsalStage.COMPLETE, RehearsalStatus.COMPLETE
            )
            return

        # ── DIAGNOSING ────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.DIAGNOSING)

        findings = plan.findings if plan else []
        clusters = clustering_svc.extract_failure_clusters(ver1, findings)
        logger.info(
            "Rehearsal %s: %d failure cluster(s) extracted", rehearsal_id, len(clusters)
        )

        diagnoses_raw = diagnosis_svc.diagnose_failures(
            clusters=clusters,
            plan=plan if plan else _empty_plan(rehearsal_id),
            verification=ver1,
            git_diff=twin.git_diff,
        )

        # Convert to persisted records
        diagnosis_records: list[DiagnosisRecord] = [
            DiagnosisRecord(
                step=d.step,
                root_cause=d.root_cause,
                migration_relevant=d.migration_relevant,
                affected_files=d.affected_files,
                requires_human_review=d.requires_human_review,
                confidence=d.confidence,
            )
            for d in diagnoses_raw
        ]
        run1.diagnoses = diagnosis_records

        # ── REPAIRING ─────────────────────────────────────────────────────────
        repairable = [d for d in diagnoses_raw if not d.requires_human_review and d.migration_relevant]

        repair_records: list[RepairRecord] = []

        if repairable:
            store.update_rehearsal_stage(rehearsal_id, RehearsalStage.REPAIRING)
            outcomes = repair_svc.apply_repairs(twin_path, repairable)
            for outcome in outcomes:
                repair_records.append(
                    RepairRecord(
                        step=outcome.step,
                        applied=outcome.applied,
                        changed_files=outcome.changed_files,
                        notes=outcome.notes,
                        requires_human_review=outcome.requires_human_review,
                    )
                )
                if outcome.applied:
                    for dr in run1.diagnoses:
                        if dr.step == outcome.step:
                            dr.repair_applied = True
                            dr.repair_notes = outcome.notes
        else:
            logger.info("Rehearsal %s: no repairable diagnoses", rehearsal_id)

        run1.repairs = repair_records
        store.save_verification_run(run1)

        any_repair_applied = any(r.applied for r in repair_records)

        if not any_repair_applied:
            run1.requires_human_review = True
            run1.passed = False
            run1.summary = (
                f"{ver1.regression_count} regression(s). "
                "No safe targeted repairs available — human review required."
            )
            store.save_verification_run(run1)
            logger.info("Rehearsal %s: REQUIRES_HUMAN_REVIEW (no repairs applied)", rehearsal_id)
            _finalize_and_save_agent_pack(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )
            return

        # ── Round 2: VERIFYING (post-repair) ─────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.VERIFYING)
        ver2 = verification_svc.run_verification(
            twin_path=twin_path,
            profile=profile,
            rehearsal_id=rehearsal_id,
            baseline=baseline,
            context=VerificationContext.POST_REPAIR,
            round_num=2,
        )

        run2 = VerificationRun(
            rehearsal_id=rehearsal_id,
            round=2,
            verification=ver2,
            diagnoses=run1.diagnoses,
            repairs=run1.repairs,
        )

        if ver2.passed and ver2.regression_count == 0:
            run2.passed = True
            run2.summary = "All checks passed after targeted repair."
            store.save_verification_run(run2)
            logger.info("Rehearsal %s: VERIFIED after repair (round 2)", rehearsal_id)
            _finalize_and_save_agent_pack(
                rehearsal_id, RehearsalStage.COMPLETE, RehearsalStatus.COMPLETE
            )
        else:
            run2.requires_human_review = True
            remaining = ver2.regression_count
            run2.summary = (
                f"{remaining} regression(s) remain after repair attempt. "
                "Human review required."
            )
            store.save_verification_run(run2)
            logger.info(
                "Rehearsal %s: REQUIRES_HUMAN_REVIEW after repair (%d regressions remain)",
                rehearsal_id,
                remaining,
            )
            _finalize_and_save_agent_pack(
                rehearsal_id,
                RehearsalStage.REQUIRES_HUMAN_REVIEW,
                RehearsalStatus.REQUIRES_HUMAN_REVIEW,
            )

    except Exception as exc:
        logger.exception("Unexpected error in _run_verify_pipeline for %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )


def _empty_plan(rehearsal_id: str):
    """Return a minimal MigrationPlan stub when none exists."""
    from app.models.migration_plan import MigrationPlan
    return MigrationPlan(rehearsal_id=rehearsal_id, package="unknown", to_version="unknown")


def _run_intake_pipeline(
    rehearsal_id: str,
    source_url: Optional[str],
    zip_bytes: Optional[bytes],
) -> None:
    """
    Full synchronous pipeline: intake → scan → baseline.

    Runs in a BackgroundTask. Updates rehearsal state at each step.
    Cleans up the temporary workspace on completion or failure.
    """
    workspace = None
    try:
        # ── Intake ──────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.INTAKE)

        if source_url:
            workspace = intake_svc.clone_repository(source_url)
        else:
            workspace = intake_svc.extract_zip(zip_bytes)  # type: ignore[arg-type]

        # Persist local path on the rehearsal record
        rehearsal = store.load_rehearsal(rehearsal_id)
        if rehearsal:
            rehearsal.repository.local_path = str(workspace)
            store.save_rehearsal(rehearsal)

        # ── Scan ─────────────────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.SCANNING)
        profile = scanner_svc.scan_repository(workspace, rehearsal_id)
        if source_url:
            profile.source_url = source_url
        store.save_repo_profile(profile)

        # ── Baseline ─────────────────────────────────────────────────────────
        def handle_baseline_step(step_name: str, description: str) -> None:
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.BASELINING,
                active_operation=description,
            )

        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.BASELINING,
            active_operation="Initializing baseline environment...",
        )
        baseline = baseline_svc.run_baseline(
            workspace,
            profile,
            rehearsal_id,
            on_step_start=handle_baseline_step,
        )
        store.save_baseline(baseline)

        if baseline.status == BaselineStatus.ENVIRONMENT_UNAVAILABLE:
            error_msg = f"Environment unavailable: {baseline.notes or 'Required package manager is not available'}"
            logger.warning("Rehearsal %s baseline environment unavailable: %s", rehearsal_id, error_msg)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=error_msg,
            )
            return

        if baseline.status == BaselineStatus.TIMEOUT:
            error_msg = f"Baseline execution timed out: {baseline.notes or 'Command exceeded timeout limit'}"
            logger.warning("Rehearsal %s baseline timed out: %s", rehearsal_id, error_msg)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=error_msg,
            )
            return

        if baseline.install and baseline.install.status in (StepStatus.FAILED, StepStatus.TIMEOUT):
            error_msg = f"Baseline dependency install failed: {baseline.install.stderr or 'Package installation failed'}"
            logger.warning("Rehearsal %s baseline install failed: %s", rehearsal_id, error_msg)
            store.update_rehearsal_stage(
                rehearsal_id,
                RehearsalStage.FAILED,
                status=RehearsalStatus.FAILED,
                error_message=error_msg,
            )
            return

        # ── Migration Analysis ───────────────────────────────────────────────
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.ANALYZING,
            active_operation="Analyzing migration changes...",
        )
        rehearsal = store.load_rehearsal(rehearsal_id)
        if not rehearsal:
            return
        plan = migration_svc.analyze(
            rehearsal_id=rehearsal_id,
            profile=profile,
            target=rehearsal.target_upgrade,
            is_demo=rehearsal.repository.is_demo,
        )
        store.save_migration_plan(plan)

        # ── Twin Workspace ───────────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.TWIN_CREATING)
        twin = twin_svc.create_twin(workspace, rehearsal_id)
        store.save_twin_result(twin)

        # ── Migration Execution ──────────────────────────────────────────────
        store.update_rehearsal_stage(rehearsal_id, RehearsalStage.MIGRATING)
        twin = executor_svc.execute_migration(twin, plan)
        store.save_twin_result(twin)

        # ── Verification, Diagnosis, Repair & Finalize ───────────────────────
        _run_verify_pipeline(rehearsal_id)
        logger.info("End-to-end rehearsal pipeline complete for %s", rehearsal_id)

    except intake_svc.IntakeError as exc:
        logger.warning("Intake failed for rehearsal %s: %s", rehearsal_id, exc)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=f"{exc}. {exc.detail}".strip(". "),
        )
    except Exception as exc:
        logger.exception("Unexpected pipeline error for rehearsal %s", rehearsal_id)
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
    finally:
        # NOTE: Do NOT clean up the workspace here — it is needed by /migrate.
        # The workspace is intentionally kept alive after intake completes.
        # Twin creation will read it; Session 5 cleanup will remove it.
        pass


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("", response_model=RehearsalResponse, status_code=202)
async def start_rehearsal_url(
    body: StartRehearsalRequest,
    background_tasks: BackgroundTasks,
) -> RehearsalResponse:
    """
    Start a new rehearsal from a public Git URL.

    The pipeline (intake → scan → baseline) runs in the background.
    Poll GET /api/rehearsals/{id} for results.
    """
    is_demo = body.is_demo or any(
        d.repository_url.rstrip("/").lower() == body.repository_url.rstrip("/").lower()
        for d in demos_svc.get_all_demos()
    )
    rehearsal = Rehearsal(
        repository=RepositorySource(url=body.repository_url, is_demo=is_demo),
        target_upgrade=TargetUpgrade(
            package=body.target_package,
            to_version=body.target_version,
            from_version=body.from_version,
        ),
        status=RehearsalStatus.RUNNING,
        stage=RehearsalStage.INTAKE,
    )
    store.save_rehearsal(rehearsal)

    background_tasks.add_task(
        _run_intake_pipeline,
        rehearsal.id,
        body.repository_url,
        None,
    )

    logger.info("Started rehearsal %s for URL %s", rehearsal.id, body.repository_url)
    return RehearsalResponse(rehearsal=rehearsal)


@router.post("/upload", response_model=RehearsalResponse, status_code=202)
async def start_rehearsal_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Repository ZIP archive"),
    target_package: str = Form(...),
    target_version: str = Form(...),
    from_version: Optional[str] = Form(default=None),
) -> RehearsalResponse:
    """
    Start a new rehearsal from a ZIP upload.

    The pipeline (intake → scan → baseline) runs in the background.
    Poll GET /api/rehearsals/{id} for results.
    """
    if file.content_type not in ("application/zip", "application/x-zip-compressed", "application/octet-stream"):
        # Be lenient — browsers sometimes send wrong content types for ZIPs.
        pass

    zip_bytes = await file.read()
    if not zip_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    rehearsal = Rehearsal(
        repository=RepositorySource(zip_path=file.filename),
        target_upgrade=TargetUpgrade(
            package=target_package,
            to_version=target_version,
            from_version=from_version,
        ),
        status=RehearsalStatus.RUNNING,
        stage=RehearsalStage.INTAKE,
    )
    store.save_rehearsal(rehearsal)

    background_tasks.add_task(
        _run_intake_pipeline,
        rehearsal.id,
        None,
        zip_bytes,
    )

    logger.info("Started rehearsal %s for ZIP upload %s", rehearsal.id, file.filename)
    return RehearsalResponse(rehearsal=rehearsal)


@router.get("/{rehearsal_id}", response_model=RehearsalResponse)
async def get_rehearsal(rehearsal_id: str) -> RehearsalResponse:
    """
    Retrieve the current state of a rehearsal, including profile, baseline, migration plan,
    and twin result if migration has been run.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    migration_plan = store.load_migration_plan(rehearsal_id)
    twin_result = store.load_twin_result(rehearsal_id)
    verification_run = store.load_latest_verification_run(rehearsal_id)
    agent_task_spec = store.load_agent_task_spec(rehearsal_id)
    has_pack = store.has_agent_pack(rehearsal_id)

    return RehearsalResponse(
        rehearsal=rehearsal,
        repo_profile=profile,
        baseline=baseline,
        migration_plan=migration_plan,
        twin_result=twin_result,
        verification_run=verification_run,
        agent_task_spec=agent_task_spec,
        has_agent_pack=has_pack,
    )


@router.post("/{rehearsal_id}/analyze", response_model=AnalyzeResponse)
async def analyze_rehearsal(rehearsal_id: str) -> AnalyzeResponse:
    """
    Trigger migration analysis for an existing rehearsal.

    Requires that the rehearsal has a RepositoryProfile (i.e. scanning completed).
    Calls Watsonx, produces a MigrationPlan, persists and returns it.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    profile = store.load_repo_profile(rehearsal_id)
    if profile is None:
        raise HTTPException(
            status_code=422,
            detail="Repository profile not available. Run scanning first.",
        )

    store.update_rehearsal_stage(rehearsal_id, RehearsalStage.ANALYZING)

    try:
        plan = migration_svc.analyze(
            rehearsal_id=rehearsal_id,
            profile=profile,
            target=rehearsal.target_upgrade,
            is_demo=rehearsal.repository.is_demo,
        )
    except WatsonxError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=502, detail=f"Watsonx error: {exc}") from exc
    except migration_svc.MigrationAnalysisError as exc:
        store.update_rehearsal_stage(
            rehearsal_id,
            RehearsalStage.FAILED,
            status=RehearsalStatus.FAILED,
            error_message=str(exc),
        )
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    store.save_migration_plan(plan)
    store.update_rehearsal_stage(
        rehearsal_id,
        RehearsalStage.ANALYZING,
        status=RehearsalStatus.COMPLETE,
    )
    logger.info("Migration analysis persisted for rehearsal %s", rehearsal_id)

    return AnalyzeResponse(rehearsal_id=rehearsal_id, migration_plan=plan)


@router.post("/{rehearsal_id}/migrate", response_model=MigrateResponse, status_code=202)
async def migrate_rehearsal(
    rehearsal_id: str,
    background_tasks: BackgroundTasks,
) -> MigrateResponse:
    """
    Create a disposable Twin and execute the migration inside it.

    Requires a completed migration analysis (MigrationPlan must exist).
    Requires that the rehearsal workspace (local_path) is still accessible.

    The pipeline (TWIN_CREATING → MIGRATING) runs in the background.
    Poll GET /api/rehearsals/{id} to retrieve the TwinResult.

    The original repository workspace is NEVER modified.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    if store.load_migration_plan(rehearsal_id) is None:
        raise HTTPException(
            status_code=422,
            detail="No migration plan found. Run POST /analyze first.",
        )

    local_path = rehearsal.repository.local_path
    if not local_path:
        raise HTTPException(
            status_code=422,
            detail=(
                "No local workspace path recorded on this rehearsal. "
                "The original repository intake pipeline did not preserve the workspace. "
                "Re-run the rehearsal to create a fresh workspace."
            ),
        )

    if not Path(local_path).exists():
        raise HTTPException(
            status_code=422,
            detail=(
                f"Workspace at {local_path!r} no longer exists. "
                "Re-run the rehearsal to recreate a fresh workspace."
            ),
        )

    # Return immediately with a stub TwinResult; background task fills it in.
    from app.models.twin import MigrationStatus, TwinMethod
    stub = TwinResult(
        rehearsal_id=rehearsal_id,
        method=TwinMethod.TEMP_COPY,
        twin_path="",
        migration_status=MigrationStatus.PENDING,
        execution_log=["Migration queued — background task started"],
    )

    background_tasks.add_task(_run_twin_and_migrate, rehearsal_id)

    logger.info("Queued twin+migrate background task for rehearsal %s", rehearsal_id)
    return MigrateResponse(rehearsal_id=rehearsal_id, twin_result=stub)


@router.post("/{rehearsal_id}/verify", response_model=VerifyResponse, status_code=202)
async def verify_rehearsal(
    rehearsal_id: str,
    background_tasks: BackgroundTasks,
) -> VerifyResponse:
    """
    Run verification → diagnosis → repair inside the existing Twin.

    Requires a migrated Twin (POST /migrate must have completed successfully).

    The pipeline runs in the background:
      VERIFYING → DIAGNOSING → REPAIRING → VERIFYING → COMPLETE / REQUIRES_HUMAN_REVIEW

    Poll GET /api/rehearsals/{id} for results (check rehearsal.stage / status
    and verification_run in the response).

    The original repository is NEVER modified.
    """
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    twin = store.load_twin_result(rehearsal_id)
    if twin is None:
        raise HTTPException(
            status_code=422,
            detail="No twin result found. Run POST /migrate first.",
        )

    if not twin.twin_path:
        raise HTTPException(
            status_code=422,
            detail="Twin path is empty — migration may still be running. Try again shortly.",
        )

    if not Path(twin.twin_path).exists():
        raise HTTPException(
            status_code=422,
            detail=(
                f"Twin workspace at {twin.twin_path!r} no longer exists. "
                "Re-run /migrate to create a fresh Twin."
            ),
        )

    if store.load_baseline(rehearsal_id) is None:
        raise HTTPException(
            status_code=422,
            detail="No baseline found. The rehearsal baseline may not have completed.",
        )

    background_tasks.add_task(_run_verify_pipeline, rehearsal_id)

    logger.info("Queued verify pipeline for rehearsal %s", rehearsal_id)

    # Return a stub VerificationRun immediately; the real result appears after polling.
    from app.models.verification import VerificationContext, VerificationResult
    stub_run = VerificationRun(
        rehearsal_id=rehearsal_id,
        round=0,
        verification=VerificationResult(
            rehearsal_id=rehearsal_id,
            context=VerificationContext.POST_MIGRATION,
            round=0,
        ),
        summary="Verification queued — background task started.",
    )
    return VerifyResponse(rehearsal_id=rehearsal_id, verification_run=stub_run)


def _resolve_pack_files(rehearsal: Rehearsal) -> tuple[AgentTaskSpec, dict[str, str]]:
    rehearsal_id = rehearsal.id
    spec = store.load_agent_task_spec(rehearsal_id)
    profile = store.load_repo_profile(rehearsal_id)
    baseline = store.load_baseline(rehearsal_id)
    plan = store.load_migration_plan(rehearsal_id)
    twin = store.load_twin_result(rehearsal_id)
    ver_run = store.load_latest_verification_run(rehearsal_id)

    if spec is None:
        spec = agent_pack_svc.build_agent_task_spec(
            rehearsal=rehearsal,
            profile=profile,
            baseline=baseline,
            plan=plan,
            twin=twin,
            ver_run=ver_run,
        )
        store.save_agent_task_spec(spec)

    pack_files = agent_pack_svc.generate_agent_pack_files(spec, plan, twin, ver_run)
    agent_pack_svc.save_agent_pack(rehearsal_id, pack_files)
    return spec, pack_files


@router.post("/{rehearsal_id}/agent-pack", response_model=AgentPackResponse)
async def generate_agent_pack_endpoint(rehearsal_id: str) -> AgentPackResponse:
    """Generate the canonical AgentTaskSpec and CodeShift-Agent-Pack/ package."""
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    spec, pack_files = _resolve_pack_files(rehearsal)
    return AgentPackResponse(
        rehearsal_id=rehearsal_id,
        spec=spec,
        files=list(pack_files.keys()),
    )


@router.get("/{rehearsal_id}/agent-pack/download")
async def download_agent_pack(rehearsal_id: str) -> Response:
    """Download the generated Agent Pack as a ZIP archive."""
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    _, pack_files = _resolve_pack_files(rehearsal)
    zip_bytes = agent_pack_svc.create_agent_pack_zip_bytes(pack_files)
    filename = f"CodeShift-Agent-Pack-{rehearsal_id[:8]}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{rehearsal_id}/implementation-prompt", response_model=ImplementationPromptResponse)
async def get_implementation_prompt(rehearsal_id: str) -> ImplementationPromptResponse:
    """Retrieve the generated implementation prompt ready for an AI coding agent."""
    rehearsal = store.load_rehearsal(rehearsal_id)
    if rehearsal is None:
        raise HTTPException(status_code=404, detail=f"Rehearsal '{rehearsal_id}' not found.")

    _, pack_files = _resolve_pack_files(rehearsal)
    prompt = pack_files.get("implementation-prompt.md", "")
    return ImplementationPromptResponse(rehearsal_id=rehearsal_id, prompt=prompt)

