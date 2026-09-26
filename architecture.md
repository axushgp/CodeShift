# CodeShift-Final v1.0

## Product

CodeShift is a repository migration rehearsal system for developers.

A developer provides a repository and a target software upgrade. CodeShift analyzes the repository, establishes a known-working baseline, creates a disposable executable Twin, rehearses the migration, verifies the result, diagnoses migration-caused failures, applies targeted repairs where possible, and produces an agent-ready implementation package.

Core promise:

"Put in a repository and a target upgrade. CodeShift safely rehearses the migration before the real repository is changed."

Core positioning:

Analyze → Rehearse → Verify → Specify → Delegate

---

## Locked End-to-End Workflow

REPOSITORY
→ SCAN
→ BASELINE
→ MIGRATION ANALYSIS
→ CREATE TWIN
→ MIGRATE
→ VERIFY
→ DIAGNOSE / REPAIR
→ VERIFY
→ FINAL FINDINGS
→ AGENT TASK SPEC
→ AGENT PACK

The original repository must never be modified during the rehearsal.

---

## 1. Repository Input

Supported inputs:

- Public Git repository URL
- Repository ZIP

For a public Git repository, clone it locally.

For private or inaccessible repositories, require user-provided access or a ZIP.

Do not pretend to have access to private repositories.

The core demo must not depend on GitHub OAuth or GitHub write access.

---

## 2. Frontend

Technology:

- React
- TypeScript
- Vite

Responsibilities:

- Repository input
- Target upgrade input
- Start rehearsal
- Rehearsal status
- Progress
- Migration findings
- Verification results
- Final findings
- Agent Pack controls
- Copy Implementation Prompt
- Download Agent Pack
- Loading and error states
- Demo Mode

The frontend must remain simple and focused on the end-to-end workflow.

---

## 3. Backend

Technology:

- Python
- FastAPI

The backend is the main application layer.

Do not create microservices.

The backend coordinates:

- Repository intake
- Scanning
- Baseline verification
- Migration analysis
- Twin creation
- Migration execution
- Verification
- Failure clustering
- Watsonx diagnosis
- Repair
- Final reporting
- Agent Pack generation

Use filesystem/JSON persistence initially.

SQLite may be added only if genuinely necessary.

No database server is required.

---

## 4. Repository Scanner

The scanner is deterministic and must not depend on an LLM.

It should detect as applicable:

- Ecosystem
- Runtime
- Package manager
- Framework
- Dependencies
- Development dependencies
- Lockfile
- Build scripts
- Test scripts
- Lint scripts
- Source structure
- Test structure
- Important configuration files

Output:

repo_profile.json

The architecture should initially target JavaScript/TypeScript + Node/npm for the hackathon MVP.

The architecture should remain extensible to additional ecosystems later.

---

## 5. Baseline Verifier

Before modifying anything, CodeShift must establish the repository's current state.

The baseline verifier should run applicable:

- Install
- Build
- Test
- Lint

Output:

baseline.json

The baseline is critical because migration failures must be distinguished from failures that already existed before migration.

Example:

Baseline:
184 / 184 tests passing

Migration:
176 / 184 tests passing

The difference represents failures that need investigation.

---

## 6. Migration Knowledge

Migration Knowledge contains structured, curated migration information.

Example structure:

migration_knowledge/
├── node/
├── react/
└── nextjs/

Knowledge can contain:

- Breaking changes
- Deprecated APIs
- Migration rules
- Known codemods
- Manual migration requirements
- Official references
- Version-specific considerations

Do not create a giant RAG/vector database for the MVP.

Migration Knowledge should be structured and compact.

---

## 7. Watsonx Semantic Analysis

IBM watsonx.ai is the runtime semantic AI layer.

Watsonx receives compact, relevant context rather than the entire repository.

Possible inputs:

- Repository profile
- Target upgrade
- Migration knowledge
- AST/static findings
- Relevant source snippets
- Configuration information

Watsonx produces a structured migration plan.

Primary output:

migration_plan.json

Watsonx must produce structured MigrationFinding objects rather than uncontrolled free-form output.

---

## 8. MigrationFinding

MigrationFinding is a central internal object.

Each finding should contain concepts such as:

- id
- type
- severity
- affected files
- reason
- evidence
- required action
- status

The system should preserve traceability:

Evidence
→ Finding
→ Planned Action
→ Changed Files
→ Verification

Findings must clearly distinguish:

- VERIFIED
- PROPOSED
- REQUIRES HUMAN REVIEW

---

## 9. Twin Workspace

The migration must happen inside a disposable Twin.

The Twin may use:

- Git worktree
- Temporary clone
- Equivalent isolated workspace

The original repository must remain untouched.

The Twin is an executable disposable copy where the migration can actually be rehearsed.

Twin means an executable disposable copy, not a visualization.

The system should track:

- Twin location
- Starting revision
- Changed files
- Git diff
- Migration status
- Verification status

For arbitrary repository execution, use appropriate isolation such as containers, restricted filesystem access, controlled networking, and time/resource limits where practical.

For the hackathon demo, use a known-good public repository and controlled scenario for reliability.

---

## 10. Migration Execution

Use deterministic mechanisms for known mechanical changes.

Examples:

- Version changes
- Codemods
- AST transformations
- Structured configuration changes

Use Watsonx for ambiguous semantic changes that require reasoning.

Do not blindly rewrite the entire repository using an LLM.

The objective is a controlled migration rehearsal, not uncontrolled AI code generation.

---

## 11. Verification Engine

After migration, rerun the relevant repository checks inside the Twin.

Run applicable:

- Install
- Build
- Test
- Lint

Compare results against the baseline.

Verification must produce structured results.

Example:

Baseline:
184 / 184 tests passing

After migration:
176 / 184 tests passing

After targeted repair:
184 / 184 tests passing

The system should preserve this history.

---

## 12. Failure Clustering

Migration failures should first be processed deterministically.

The failure system should:

- Parse logs
- Identify failures
- Group related failures
- Map failures to affected files
- Associate failures with MigrationFindings where possible
- Track migration causality

Do not immediately send raw logs to Watsonx without preprocessing.

Failure clusters become structured input for semantic diagnosis.

---

## 13. Watsonx Failure Diagnosis

Watsonx may receive:

- Migration plan
- Migration findings
- Git diff
- Failure clusters
- Relevant source snippets
- Baseline results

The output should identify:

- Likely root cause
- Whether the failure is migration-caused
- Affected files
- Recommended repair
- Confidence/status where appropriate

Watsonx should propose targeted repairs rather than broad uncontrolled rewrites.

---

## 14. Repair

Runtime repair flow:

Watsonx diagnosis
→ targeted patch
→ Twin
→ verification

The system may retry verification after a targeted repair.

Possible final states:

VERIFIED

or

NEEDS HUMAN REVIEW

Bob is not a runtime dependency.

---

## 15. AgentTaskSpec

AgentTaskSpec is the canonical machine-readable handoff artifact.

It is the source of truth for the Agent Pack.

It should contain concepts including:

- task
- repository
- findings
- implementation_plan
- constraints
- files_to_modify
- files_not_to_modify
- verification
- acceptance_criteria

It must preserve the distinction between:

- VERIFIED
- PROPOSED
- REQUIRES HUMAN REVIEW

The AgentTaskSpec should be useful to another coding agent without requiring CodeShift to remain running.

---

## 16. Agent Pack

The final Agent Pack should contain:

CodeShift-Agent-Pack/
├── agent_task.json
├── implementation-prompt.md
├── AGENTS.md
├── migration-plan.md
├── findings.json
├── verification.md
├── patch.diff
└── README.md

Purpose:

Package the migration work into a form that can be directly handed to another coding agent.

The UI should provide:

[ Copy Implementation Prompt ]

[ Download Agent Pack ]

The output should be generic and usable with coding agents such as:

- Claude Code
- Codex
- Cursor
- Gemini CLI
- GitHub Copilot
- Other compatible coding agents

No provider-specific runtime integration is required for the MVP.

---

## 17. Demo Mode

CodeShift must support two conceptual modes.

### Live Mode

Uses:

- User repository
- User-selected target upgrade
- Live analysis
- Watsonx

### Demo Mode

Uses:

- Preloaded known repository
- Controlled migration scenario
- Deterministic setup
- Same end-to-end workflow

Demo Mode exists for reliability and demonstration.

It is not a separate product concept.

The final hackathon demo must remain usable even if a live external API call becomes unavailable.

---

## 18. Security and Isolation

Executing repository code creates security risks.

The system should isolate Twin execution as much as practical.

Preferred controls include:

- Isolated workspace/container
- Restricted filesystem access
- Controlled network access
- Process timeouts
- Resource limits
- No modification of the original repository

Never execute migration commands directly against the user's original working tree.

---

## 19. Persistence

Use simple persistence.

Preferred:

- JSON
- Filesystem artifacts

SQLite may be introduced only if required.

Do not introduce:

- Separate database servers
- Distributed storage
- Unnecessary infrastructure

---

## 20. Runtime AI and External Dependencies

Runtime semantic AI:

IBM watsonx.ai

Runtime deterministic components:

- Git
- Node/npm
- AST/static analysis tools
- Codemods
- Build/test/lint tools
- Python/FastAPI
- React/TypeScript/Vite

No additional LLM should be required.

No OpenAI, Claude, Gemini, Mistral, or other LLM should be added unless a concrete implementation blocker demonstrates that Watsonx is insufficient.

No external vector database is required.

No GitHub API is required for the core demo.

---

## 21. IBM Bob 2.0

IBM Bob 2.0 is a development-time tool used by the team to build CodeShift.

Bob is not a runtime dependency of the final product.

Runtime architecture:

User
→ CodeShift
→ deterministic analysis
→ Watsonx semantic analysis
→ Twin
→ verification
→ findings
→ Agent Pack

Bob is only used to build and iterate on this product.

---

## 22. Testing Philosophy

Testing is first-class throughout the project.

Required categories:

### Unit Tests

Examples:

- Repository scanner
- Parsers
- Failure clustering
- MigrationFinding handling
- AgentTaskSpec generation
- Report generation

### Integration Tests

Examples:

- Scanner → Migration Planner
- Migration → Twin
- Twin → Verification
- Watsonx → Structured Output
- Findings → AgentTaskSpec
- AgentTaskSpec → Agent Pack

### End-to-End Test

The system should support a complete flow:

Repository
→ Baseline
→ Migration analysis
→ Twin
→ Migration
→ Verification
→ Failure diagnosis/repair
→ Final verification
→ Agent Pack

### Watsonx Testing

Most AI tests should use mocked deterministic responses.

Use only limited real Watsonx integration testing to avoid unnecessary token/API consumption.

### Twin Safety Test

A critical test must prove:

Original repository remains unchanged.

Twin changes independently.

### Migration Verification Test

The system should demonstrate a controlled scenario such as:

184 / 184
→ 176 / 184
→ diagnosis
→ targeted repair
→ 184 / 184

---

## 23. Core Product Boundary

CodeShift is not:

- A generic AI coding agent
- A generic code review tool
- A plain codemod runner
- A dependency update bot
- A static analyzer
- A replacement for Git
- A visual digital-twin simulation

Its core value is:

A verified migration rehearsal.

The important outcome is not simply "files were changed."

The important outcome is:

"Here is what the upgrade affects, here is what actually broke in a disposable executable Twin, here is the evidence, here is what was repaired or still needs human attention, and here is an agent-ready implementation specification."

---

## 24. Locked Architecture Principle

Do not change the fundamental architecture during implementation unless a concrete technical blocker requires it.

Implementation details may change, including:

- Exact demo repository
- Exact upgrade scenario
- Exact Watsonx model
- AST/static analysis library
- UI styling
- Deployment mechanism

The following architectural decisions are considered locked:

- React + TypeScript + Vite frontend
- Python + FastAPI backend
- Deterministic repository scanner
- Baseline verification before migration
- Structured migration knowledge
- Watsonx for semantic reasoning
- Disposable executable Twin
- Deterministic migration tools for mechanical changes
- Watsonx for ambiguous semantic changes
- Post-migration verification
- Failure clustering before AI diagnosis
- Targeted repair inside Twin
- AgentTaskSpec
- Agent Pack
- Demo Mode
- Tests throughout the workflow
- No runtime dependency on Bob
- No microservices
- No unnecessary vector database
- No additional LLM

Reference name:

CodeShift-Final v1.0