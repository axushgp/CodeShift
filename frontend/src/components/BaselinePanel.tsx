/**
 * BaselinePanel — displays baseline command results.
 */

import { useState } from 'react'
import type { BaselineResult, CommandResult, StepStatus } from '../types'

interface BaselinePanelProps {
  baseline: BaselineResult
}

export function BaselinePanel({ baseline }: BaselinePanelProps) {
  const steps = [
    { label: 'Install', result: baseline.install },
    { label: 'Build', result: baseline.build },
    { label: 'Test', result: baseline.test },
    { label: 'Lint', result: baseline.lint },
  ].filter((s): s is { label: string; result: CommandResult } => s.result != null)

  const getOverallBadge = () => {
    if (baseline.status === 'ENVIRONMENT_UNAVAILABLE') {
      return { label: 'Environment Unavailable', modifier: 'unavailable' }
    }
    if (baseline.status === 'SKIPPED_NOT_APPLICABLE') {
      return { label: 'Not Applicable', modifier: 'not-applicable' }
    }
    if (baseline.status === 'PASS' || baseline.passed) {
      return { label: 'Passed', modifier: 'passed' }
    }
    return { label: 'Failed', modifier: 'failed' }
  }

  const badge = getOverallBadge()

  return (
    <div className="cs-baseline" data-testid="baseline-panel">
      <h2 className="cs-baseline__title">
        Baseline
        <span
          className={`cs-baseline__badge cs-baseline__badge--${badge.modifier}`}
        >
          {badge.label}
        </span>
      </h2>

      <div className="cs-baseline__steps">
        {steps.map(({ label, result }) => (
          <StepRow key={result.step} label={label} result={result} />
        ))}
      </div>

      {baseline.notes && (
        <p className="cs-baseline__notes">{baseline.notes}</p>
      )}
    </div>
  )
}

function statusColor(status: StepStatus): string {
  switch (status) {
    case 'PASSED': return 'passed'
    case 'FAILED': return 'failed'
    case 'ENVIRONMENT_UNAVAILABLE': return 'unavailable'
    case 'SKIPPED_NOT_APPLICABLE':
    case 'SKIPPED': return 'skipped'
    default: return 'not-run'
  }
}

function formatStatus(status: StepStatus): string {
  switch (status) {
    case 'SKIPPED_NOT_APPLICABLE': return 'NOT APPLICABLE'
    case 'ENVIRONMENT_UNAVAILABLE': return 'UNAVAILABLE'
    default: return status
  }
}

function StepRow({ label, result }: { label: string; result: CommandResult }) {
  const color = statusColor(result.status)
  const [expanded, setExpanded] = useState(false)
  const hasOutput = result.stdout || result.stderr

  return (
    <div className={`cs-step cs-step--${color}`} data-testid={`step-${result.step}`}>
      <div className="cs-step__header">
        <span className="cs-step__label">{label}</span>
        <span className={`cs-step__status cs-step__status--${color}`}>{formatStatus(result.status)}</span>
        <code className="cs-step__cmd">{result.command}</code>
        {result.duration_seconds != null && (
          <span className="cs-step__duration">{result.duration_seconds.toFixed(1)}s</span>
        )}
        {hasOutput && (
          <button
            type="button"
            className="cs-step__toggle"
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? 'Hide' : 'Show output'}
          </button>
        )}
      </div>

      {expanded && hasOutput && (
        <div className="cs-step__output">
          {result.stdout && (
            <pre className="cs-step__pre cs-step__pre--stdout">{result.stdout}</pre>
          )}
          {result.stderr && (
            <pre className="cs-step__pre cs-step__pre--stderr">{result.stderr}</pre>
          )}
        </div>
      )}
    </div>
  )
}
