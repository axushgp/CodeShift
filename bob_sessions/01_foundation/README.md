# Session 01 — Foundation + Test Infrastructure

## Objective

Build a clean, extensible project foundation for CodeShift-Final v1.0.

## Acceptance Criteria Satisfied

1. Frontend starts successfully (Vite + React + TypeScript)
2. Backend starts successfully (FastAPI)
3. `GET /health` returns structured response
4. Core typed domain models exist and validate correctly
5. Rehearsal state machine exists and supports full workflow
6. Backend test infrastructure operational (pytest)
7. Frontend test infrastructure operational (Vitest + Testing Library)
8. Smoke tests pass (backend + frontend)
9. No credentials committed
10. Phase 0 files preserved
11. Project structure clean and ready for Session 2
12. No Session 2+ work implemented

## Files Created

### Backend

```
backend/
├── pyproject.toml                          # Python project + dev dependencies
├── app/
│   ├── __init__.py
│   ├── main.py                             # FastAPI app factory
│   ├── config.py                           # Settings / environment
│   ├── logging_config.py                   # Logging setup
│   ├── state_machine.py                    # Rehearsal state machine
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py                       # GET /health
│   └── models/
│       ├── __init__.py
│       ├── rehearsal.py                    # Rehearsal, RehearsalStage, etc.
│       ├── repository_profile.py           # RepositoryProfile
│       ├── baseline.py                     # BaselineResult, CommandResult
│       ├── finding.py                      # MigrationFinding
│       ├── migration_plan.py               # MigrationPlan, PlannedAction
│       └── verification.py                 # VerificationResult
└── tests/
    ├── conftest.py                         # Shared fixtures
    ├── unit/
    │   ├── test_models.py                  # Domain model unit tests
    │   └── test_state_machine.py           # State machine unit tests
    └── integration/
        └── test_endpoints.py               # FastAPI endpoint tests
```

### Frontend

```
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx                             # Application shell
    ├── App.css                             # Global styles
    ├── index.css
    ├── types/
    │   └── index.ts                        # TypeScript domain types
    ├── api/
    │   └── client.ts                       # API client foundation
    ├── components/
    │   ├── Header.tsx
    │   ├── RehearsalForm.tsx
    │   ├── StatusPanel.tsx
    │   └── ResultsArea.tsx
    └── test/
        ├── setup.ts
        ├── App.test.tsx
        ├── Header.test.tsx
        ├── RehearsalForm.test.tsx
        └── StatusPanel.test.tsx
```

## Key Architectural Decisions

- **State machine** (`state_machine.py`): Enforces the locked workflow transitions. Invalid transitions raise `InvalidTransitionError`. Terminal stages (COMPLETE, FAILED, REQUIRES_HUMAN_REVIEW) have no outgoing transitions.
- **Domain models**: All use Pydantic v2 with strong typing. `FindingStatus` includes VERIFIED / PROPOSED / REQUIRES_HUMAN_REVIEW per architecture.md §8.
- **Persistence**: No database server. Filesystem/JSON pattern established in model design (rehearsal_id as primary key, json output filenames noted in docstrings).
- **API client**: Thin `fetch` wrapper in `src/api/client.ts`. Later sessions add rehearsal endpoints.

## What Is NOT Implemented (Explicit Non-Goals)

- Watsonx integration
- Repository cloning / ZIP ingestion
- Repository scanner
- Migration execution
- Twin creation
- Baseline verification
- Any Session 2+ features
