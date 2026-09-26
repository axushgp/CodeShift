# CodeShift

## CodeShift-Final v1.0

CodeShift is a repository migration rehearsal system.

A developer provides a repository and a target software upgrade. CodeShift analyzes the repository, establishes a working baseline, rehearses the migration inside a disposable Twin, verifies the result, diagnoses migration-caused failures, and produces an agent-ready implementation package.

### Core Flow

Analyze → Rehearse → Verify → Specify → Delegate

### Core Workflow

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

### Main Technologies

- React
- TypeScript
- Vite
- Python
- FastAPI
- Git
- Node/npm
- IBM watsonx.ai
- AST/static analysis tools

### Architecture

See `architecture.md`.

### Bob Sessions

Development work performed through IBM Bob 2.0 is documented under:

`bob_sessions/`

Bobcoin tracking is maintained in:

`BOBCOIN_LEDGER.md`

### Important

The original repository must never be modified during migration rehearsal.

The migration takes place inside a disposable executable Twin.