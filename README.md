# CodeShift

## CodeShift-Final v1.0

CodeShift is a repository migration rehearsal system.

A developer provides a repository and a target software upgrade. CodeShift analyzes the repository, establishes a working baseline, rehearses the migration inside a disposable Twin, verifies the result, diagnoses migration-caused failures, and produces an agent-ready implementation package.

### Core Flow

Analyze → Rehearse → Verify → Specify → Delegate

### Core Workflow

```
Repository
→ Scan
→ Baseline
→ Migration Analysis
→ Twin
→ Migrate
→ Verify
→ Diagnose / Repair
→ Verify
→ Final Findings
→ AgentTaskSpec
→ Agent Pack
```

### Main Technologies

- React + TypeScript + Vite (frontend)
- Python + FastAPI (backend)
- Git
- IBM watsonx.ai (Session 3+)

### Architecture

See [`architecture.md`](architecture.md) — the locked architectural source of truth.

---

## Development Status

**CodeShift-Final v1.0 — Completed End-to-End Workflow** ✅

The complete migration rehearsal pipeline is implemented and verified:
- **Repository Intake & Scan**: URL clone or ZIP upload, repository profiling (package manager, primary language, test runner, lockfile detection).
- **Baseline Verification**: Clean isolated install, build, test, and lint check.
- **Migration Intelligence**: IBM watsonx.ai integration with deterministic curated knowledge fallback for React 17 → React 18 migrations.
- **Disposable Twin**: Isolated git worktree workspace ensuring the user's original repository is never modified.
- **Verification & Repair**: Multi-round verification against baseline, failure clustering, semantic diagnosis, and targeted repair.
- **AgentTaskSpec**: Canonical machine-readable task specification preserving `VERIFIED`, `PROPOSED`, and `REQUIRES_HUMAN_REVIEW` statuses.
- **Agent Pack**: Complete handoff package export (`.zip`) containing `agent_task.json`, `implementation-prompt.md`, `AGENTS.md`, `migration-plan.md`, `findings.json`, `verification.md`, `patch.diff`, and `README.md`.
- **UI & Handoff**: Immediate implementation prompt copy and direct Agent Pack download.

---

## Project Structure

```
CodeShift/
├── architecture.md          # Locked architectural source of truth
├── README.md
├── .env.example             # Environment variable template
├── backend/                 # Python / FastAPI backend
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py          # FastAPI app factory
│   │   ├── config.py        # Configuration (env vars with CODESHIFT_ prefix)
│   │   ├── logging_config.py
│   │   ├── state_machine.py # Rehearsal workflow state machine
│   │   ├── api/
│   │   │   └── health.py    # GET /health
│   │   └── models/          # Core domain models
│   │       ├── rehearsal.py
│   │       ├── repository_profile.py
│   │       ├── baseline.py
│   │       ├── finding.py
│   │       ├── migration_plan.py
│   │       └── verification.py
│   └── tests/
│       ├── conftest.py      # Shared fixtures
│       ├── unit/            # Model + state machine tests
│       └── integration/     # FastAPI endpoint tests
├── frontend/                # React + TypeScript + Vite frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   └── src/
│       ├── App.tsx          # Application shell
│       ├── types/           # TypeScript domain types
│       ├── api/             # API client foundation
│       ├── components/      # UI components
│       └── test/            # Vitest tests
└── bob_sessions/            # Bob session artifacts and notes
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node 18+

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS / Linux

# Install dependencies
pip install -e ".[dev]"

# Start development server
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (OpenAPI UI)
# → http://localhost:8000/health
```

### Frontend

```bash
cd frontend

npm install
npm run dev
# → http://localhost:5173
```

### Configuration

Copy `.env.example` to `backend/.env` and set values as needed.
Environment variables use the `CODESHIFT_` prefix.

**Do not commit `.env` to source control.**

---

## Running Tests

### Backend

```bash
cd backend
.venv\Scripts\activate    # (if not already active)

# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd frontend

# Run tests once
npm test

# TypeScript typecheck
npm run typecheck

# Production build
npm run build
```

---

## Bob Sessions

Development work performed through IBM Bob 2.0 is documented under:

`bob_sessions/`

Bobcoin tracking is maintained in:

`BOBCOIN_LEDGER.md`

---

## Important

The original repository must never be modified during migration rehearsal.

The migration takes place inside a disposable executable Twin.

See `architecture.md` for the full locked architectural specification.
