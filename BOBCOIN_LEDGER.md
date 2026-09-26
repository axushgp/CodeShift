# Bobcoin Ledger

## Budget

Hard ceiling: 40 Bobcoins
Planned envelope: 34 Bobcoins
Reserve: 6 Bobcoins
The project must never exceed 40 Bobcoins.

---

## Planned Sessions

| Session | Objective | Planned | Actual | Remaining |
|---|---|---:|---:|---:|
| Initial | Phase 0 setup | 0 | 0 | 40 |
| 01 | Foundation + Test Infrastructure | 4 | TBD | TBD |
| 02 | Repository Intake + Baseline | 5 | TBD | TBD |
| 03 | Migration Intelligence + Watsonx | 6 | TBD | TBD |
| 04 | Twin + Migration Execution | 5 | TBD | TBD |
| 05 | Verification + Failure Recovery | 6 | TBD | TBD |
| 06 | AgentTaskSpec + Agent Pack | 4 | TBD | TBD |
| 07 | Full Integration + E2E + Demo | 4 | TBD | TBD |
| Reserve | Critical blockers only | 6 | TBD | TBD |

---

## Session Rules

1. One Bob session should have one bounded objective.
2. Stop the session once its acceptance criteria are satisfied.
3. Do not spend the reserve unless a genuinely critical blocker requires it.
4. Do not use Bob for deterministic tasks that can be implemented directly.
5. Persist durable project context in repository files.
6. Export the Bob task history after every session.
7. Capture the required Bobcoin consumption evidence after every session.
8. Do not start the next session inside the current session.
9. Never exceed the 40 Bobcoin hard ceiling.

---

## Session Directory Structure

bob_sessions/

├── 01_foundation/
├── 02_repository_baseline/
├── 03_migration_watsonx/
├── 04_twin/
├── 05_verification_recovery/
├── 06_agent_pack/
└── 07_integration_e2e/

Each session directory should contain, as applicable:

- Bob task history export
- Bobcoin consumption screenshot
- README.md
- Important generated artifacts
- Notes on files changed
- Tests executed
- Actual Bobcoin usage

---

## Running Totals

Starting budget: 40
Consumed: 0
Remaining: 40
Reserve remaining: 6