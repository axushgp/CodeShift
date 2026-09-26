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

export type StepStatus = 'PASSED' | 'FAILED' | 'SKIPPED' | 'NOT_RUN'

export interface CommandResult {
  step: string
  command: string
  exit_code: number
  stdout: string
  stderr: string
  duration_seconds?: number
  status: StepStatus
}

export interface BaselineResult {
  rehearsal_id: string
  install?: CommandResult
  build?: CommandResult
  test?: CommandResult
  lint?: CommandResult
  passed: boolean
  notes?: string
}

// ---------------------------------------------------------------------------
// Rehearsal API response
// ---------------------------------------------------------------------------

export interface RehearsalResponse {
  rehearsal: Rehearsal
  repo_profile?: RepositoryProfile
  baseline?: BaselineResult
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
