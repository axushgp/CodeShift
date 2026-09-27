/**
 * CodeShift frontend domain types.
 *
 * Mirrors the Python backend models so the API contract is typed end-to-end.
 * Types evolve as sessions add new backend capabilities.
 */

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export type RehearsalStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'PAUSED'
  | 'COMPLETE'
  | 'FAILED'
  | 'REQUIRES_HUMAN_REVIEW'

export type RehearsalStage =
  | 'INTAKE'
  | 'SCANNING'
  | 'BASELINING'
  | 'ANALYZING'
  | 'TWIN_CREATING'
  | 'MIGRATING'
  | 'VERIFYING'
  | 'DIAGNOSING'
  | 'REPAIRING'
  | 'FINALIZING'
  | 'COMPLETE'
  | 'FAILED'
  | 'REQUIRES_HUMAN_REVIEW'

export type FindingStatus =
  | 'OPEN'
  | 'IN_PROGRESS'
  | 'PROPOSED'
  | 'VERIFIED'
  | 'REQUIRES_HUMAN_REVIEW'

export type FindingSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'

export type FindingType =
  | 'BREAKING_CHANGE'
  | 'DEPRECATED_API'
  | 'CONFIGURATION_CHANGE'
  | 'DEPENDENCY_CONFLICT'
  | 'TYPE_ERROR'
  | 'BUILD_FAILURE'
  | 'TEST_FAILURE'
  | 'LINT_FAILURE'
  | 'MANUAL_MIGRATION_REQUIRED'
  | 'INFORMATIONAL'

// ---------------------------------------------------------------------------
// Repository
// ---------------------------------------------------------------------------

export interface RepositorySource {
  url?: string
  zip_path?: string
  local_path?: string
  is_demo: boolean
}

export interface TargetUpgrade {
  package: string
  from_version?: string
  to_version: string
  ecosystem?: string
}

// ---------------------------------------------------------------------------
// Rehearsal
// ---------------------------------------------------------------------------

export interface Rehearsal {
  id: string
  status: RehearsalStatus
  stage: RehearsalStage
  repository: RepositorySource
  target_upgrade: TargetUpgrade
  created_at: string
  updated_at: string
  completed_at?: string
  error_message?: string
  active_operation?: string
}

// ---------------------------------------------------------------------------
// Finding
// ---------------------------------------------------------------------------

export interface MigrationFinding {
  id: string
  type: FindingType
  severity: FindingSeverity
  title: string
  reason: string
  evidence?: string
  required_action: string
  affected_files: string[]
  status: FindingStatus
  planned_action_id?: string
  verification_note?: string
}

// ---------------------------------------------------------------------------
// Repository Profile
// ---------------------------------------------------------------------------

export type Ecosystem = 'node' | 'python' | 'unknown'
export type PackageManager = 'npm' | 'yarn' | 'pnpm' | 'bun' | 'pip' | 'poetry' | 'uv' | 'unknown'

export interface ScriptInfo {
  name: string
  command: string
}

export interface SourceStructure {
  src_dirs: string[]
  test_dirs: string[]
  config_files: string[]
  entry_points: string[]
}

export interface RepositoryProfile {
  rehearsal_id: string
  name?: string
  source_url?: string
  ecosystem: Ecosystem
  runtime?: string
  package_manager: PackageManager
  package_manager_version?: string
  environment_requirements?: Record<string, string>
  relevant_scripts?: Record<string, string>
  framework?: string
  dependencies: Record<string, string>
  dev_dependencies: Record<string, string>
  lockfile?: string
  build_scripts: ScriptInfo[]
  test_scripts: ScriptInfo[]
  lint_scripts: ScriptInfo[]
  structure: SourceStructure
  raw_manifest?: Record<string, unknown>
}

// ---------------------------------------------------------------------------
// Baseline
// ---------------------------------------------------------------------------

export type StepStatus =
  | 'PASSED'
  | 'FAILED'
  | 'TIMEOUT'
  | 'SKIPPED'
  | 'SKIPPED_NOT_APPLICABLE'
  | 'ENVIRONMENT_UNAVAILABLE'
  | 'NOT_RUN'

export type BaselineStatus =
  | 'PASS'
  | 'FAIL'
  | 'TIMEOUT'
  | 'SKIPPED_NOT_APPLICABLE'
  | 'ENVIRONMENT_UNAVAILABLE'

export interface CommandResult {
  step: string
  command: string
  exit_code: number
  stdout: string
  stderr: string
  duration_seconds?: number
  status: StepStatus
}

export interface TestRunSummary {
  total: number
  passed: number
  failed: number
  skipped: number
  duration_seconds?: number
}

export interface BaselineResult {
  rehearsal_id: string
  status?: BaselineStatus
  active_step?: string
  active_operation?: string
  active_timeout?: number
  active_started_at?: number
  install?: CommandResult
  build?: CommandResult
  test?: CommandResult
  lint?: CommandResult
  test_summary?: TestRunSummary
  passed: boolean
  notes?: string
}

// ---------------------------------------------------------------------------
// Migration Plan
// ---------------------------------------------------------------------------

export interface PlannedAction {
  id: string
  finding_ids: string[]
  action_type: string
  description: string
  target_files: string[]
  command?: string
  patch?: string
}

export interface MigrationPlan {
  rehearsal_id: string
  package: string
  from_version?: string
  to_version: string
  framework?: string
  migration_path?: string
  recipe_id?: string
  findings: MigrationFinding[]
  planned_actions: PlannedAction[]
  total_findings: number
  critical_findings: number
  requires_human_review: boolean
  knowledge_sources: string[]
  notes?: string
}

// ---------------------------------------------------------------------------
// Target Discovery & Knowledge Registry
// ---------------------------------------------------------------------------

export interface TargetOption {
  target_version: string
  label: string
  badge?: string
  is_recommended: boolean
  has_certified_recipe: boolean
  recipe?: string | null
  description: string
}

export interface UpgradeTargetInfo {
  current: string
  recommended_target?: string
  has_certified_recipe: boolean
  options: TargetOption[]
}

export interface DetectedFramework {
  id: string
  name: string
  package: string
}

export interface ToolingInfo {
  build_tool: string
  runtime: string
  package_manager: string
}

export interface DiscoveredTargets {
  discovery_id?: string
  detected_framework: DetectedFramework
  detected_version: string
  raw_version?: string
  tooling: ToolingInfo
  upgrade_target: UpgradeTargetInfo
  knowledge_updated: string
}

// ---------------------------------------------------------------------------
// Twin Workspace
// ---------------------------------------------------------------------------

export interface ChangedFile {
  path: string
  change_type: string
}

export interface TwinResult {
  rehearsal_id: string
  method: string
  twin_path: string
  worktree_branch?: string
  starting_revision?: string
  migration_status: 'PENDING' | 'SUCCESS' | 'PARTIAL' | 'FAILED'
  changed_files: ChangedFile[]
  git_diff?: string
  execution_log: string[]
  error_message?: string
  actions_applied: string[]
  actions_skipped: string[]
  manual_items: string[]
}

// ---------------------------------------------------------------------------
// Verification & Diagnosis
// ---------------------------------------------------------------------------

export interface VerificationResult {
  rehearsal_id: string
  context: string
  round: number
  install?: CommandResult
  build?: CommandResult
  test?: CommandResult
  lint?: CommandResult
  test_summary?: TestRunSummary
  passed: boolean
  regression_count: number
  regression_details: string[]
  baseline_test_total?: number
  baseline_test_passed?: number
  notes?: string
}

export interface DiagnosisRecord {
  step: string
  root_cause: string
  migration_relevant: boolean
  affected_files: string[]
  requires_human_review: boolean
  confidence: string
  repair_applied: boolean
  repair_notes: string
}

export interface RepairRecord {
  step: string
  applied: boolean
  changed_files: string[]
  notes: string
  requires_human_review: boolean
}

export interface VerificationRun {
  rehearsal_id: string
  round: number
  verification: VerificationResult
  diagnoses: DiagnosisRecord[]
  repairs: RepairRecord[]
  passed: boolean
  requires_human_review: boolean
  summary?: string
}

// ---------------------------------------------------------------------------
// Agent Task Spec & Pack
// ---------------------------------------------------------------------------

export interface TaskDetails {
  package: string
  from_version?: string
  to_version: string
  status: string
  summary?: string
}

export interface ImplementationStep {
  step_number: number
  action_type: string
  description: string
  target_files: string[]
  status: string
  notes?: string
}

export interface VerificationSummary {
  baseline_passed: boolean
  final_verification_passed: boolean
  regressions_count: number
  status: string
  details: string[]
}

export interface AgentTaskSpec {
  rehearsal_id: string
  task: TaskDetails
  repository: Record<string, unknown>
  findings: MigrationFinding[]
  implementation_plan: ImplementationStep[]
  constraints: string[]
  files_to_modify: string[]
  files_not_to_modify: string[]
  verification: VerificationSummary
  acceptance_criteria: string[]
}

// ---------------------------------------------------------------------------
// Rehearsal API response
// ---------------------------------------------------------------------------

export interface RehearsalResponse {
  rehearsal: Rehearsal
  repo_profile?: RepositoryProfile
  baseline?: BaselineResult
  migration_plan?: MigrationPlan
  twin_result?: TwinResult
  verification_run?: VerificationRun
  agent_task_spec?: AgentTaskSpec
  has_agent_pack?: boolean
}

// ---------------------------------------------------------------------------
// API response helpers
// ---------------------------------------------------------------------------

export interface HealthResponse {
  status: string
  app: string
  version: string
  environment: string
  timestamp: string
}

export interface ApiError {
  error: string
  detail: string
}

// ---------------------------------------------------------------------------
// Quick Start Demo Manifest
// ---------------------------------------------------------------------------

export interface DemoManifest {
  id: string
  name: string
  repository_url: string
  description: string
  package: string
  source_version: string
  target_version: string
}


