/**
 * StatusPanel — displays current rehearsal stage, status badge, and optional error.
 * Styled with modern developer infrastructure theme.
 */

import { Loader2, CheckCircle2, AlertCircle, AlertTriangle } from 'lucide-react'
import type { RehearsalStage, RehearsalStatus } from '../types'

interface StatusPanelProps {
  stage: RehearsalStage
  status: RehearsalStatus
  errorMessage?: string
  activeOperation?: string | null
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

export function StatusPanel({ stage, status, errorMessage, activeOperation }: StatusPanelProps) {
  const isRunning = status === 'RUNNING'
  const isFailed = status === 'FAILED'
  const isComplete = status === 'COMPLETE'
  const isReview = status === 'REQUIRES_HUMAN_REVIEW'

  const badgeText = isComplete
    ? 'Complete'
    : isRunning
    ? 'Running'
    : isFailed
    ? 'Failed'
    : isReview
    ? 'Requires Review'
    : status

  return (
    <div
      className={`rounded border border-zinc-800 bg-[#121214] px-4 py-2.5 transition-all ${
        isFailed
          ? 'border-l-2 border-l-red-500'
          : isReview
          ? 'border-l-2 border-l-amber-500'
          : isComplete
          ? 'border-l-2 border-l-emerald-500'
          : 'border-l-2 border-l-blue-500'
      }`}
      data-testid="status-panel"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          {isRunning && <Loader2 className="h-4 w-4 animate-spin text-blue-400" />}
          {isComplete && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
          {isFailed && <AlertCircle className="h-4 w-4 text-red-400" />}
          {isReview && <AlertTriangle className="h-4 w-4 text-amber-400" />}

          <span
            className="text-sm font-medium text-zinc-200"
            data-testid="status-stage"
          >
            {STAGE_LABELS[stage] ?? stage}
            {isRunning && activeOperation ? (
              <span className="ml-1.5 text-zinc-400 font-normal">
                — {activeOperation}
              </span>
            ) : null}
          </span>
        </div>

        <span
          className={`inline-flex items-center space-x-1.5 text-sm font-mono font-medium ${
            isComplete
              ? 'text-emerald-400'
              : isFailed
              ? 'text-red-400'
              : isReview
              ? 'text-amber-400'
              : 'text-blue-400'
          }`}
          data-testid="status-badge"
        >
          <span>●</span>
          <span>{badgeText}</span>
        </span>
      </div>

      {errorMessage && (
        <p
          className="mt-2 text-sm text-red-400 font-mono bg-red-950/20 rounded p-2.5 border border-red-900/40"
          data-testid="status-error"
        >
          {errorMessage}
        </p>
      )}
    </div>
  )
}
