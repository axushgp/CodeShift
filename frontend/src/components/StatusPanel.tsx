/**
 * StatusPanel — displays the current rehearsal stage and status.
 */

import type { RehearsalStage, RehearsalStatus } from '../types'

interface StatusPanelProps {
  stage: RehearsalStage
  status: RehearsalStatus
  errorMessage?: string
}

const STAGE_LABELS: Record<RehearsalStage, string> = {
  INTAKE: 'Intake',
  SCANNING: 'Scanning repository',
  BASELINING: 'Establishing baseline',
  ANALYZING: 'Analyzing migration',
  TWIN_CREATING: 'Creating Twin',
  MIGRATING: 'Executing migration',
  VERIFYING: 'Verifying results',
  DIAGNOSING: 'Diagnosing failures',
  REPAIRING: 'Applying repairs',
  FINALIZING: 'Finalizing',
  COMPLETE: 'Complete',
  FAILED: 'Failed',
  REQUIRES_HUMAN_REVIEW: 'Requires human review',
}

export function StatusPanel({ stage, status, errorMessage }: StatusPanelProps) {
  const isRunning = status === 'RUNNING'
  const isFailed = status === 'FAILED'
  const isComplete = status === 'COMPLETE'

  return (
    <div
      className={`cs-status cs-status--${status.toLowerCase().replace(/_/g, '-')}`}
      data-testid="status-panel"
    >
      <span className="cs-status__stage" data-testid="status-stage">
        {isRunning && <span className="cs-status__spinner" aria-hidden="true" />}
        {STAGE_LABELS[stage]}
      </span>
      <span className="cs-status__badge" data-testid="status-badge">
        {isComplete ? 'Complete' : isRunning ? 'Running' : isFailed ? 'Failed' : status}
      </span>
      {errorMessage && (
        <p className="cs-status__error" data-testid="status-error">
          {errorMessage}
        </p>
      )}
    </div>
  )
}
