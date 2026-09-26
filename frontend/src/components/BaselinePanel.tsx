/**
 * BaselinePanel — displays baseline command results and execution logs.
 * Dense developer infrastructure styling.
 */

import { useState } from 'react'
import {
  CheckCircle2,
  XCircle,
  AlertOctagon,
  MinusCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  Terminal,
  Copy,
  Check,
} from 'lucide-react'
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
      return {
        label: 'Environment Unavailable',
        cls: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
        icon: AlertOctagon,
      }
    }
    if (baseline.status === 'TIMEOUT') {
      return {
        label: 'Timed Out',
        cls: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
        icon: AlertOctagon,
      }
    }
    if (baseline.status === 'SKIPPED_NOT_APPLICABLE') {
      return {
        label: 'Not Applicable',
        cls: 'border-slate-700 bg-slate-800 text-slate-400',
        icon: MinusCircle,
      }
    }
    if (baseline.status === 'PASS' || baseline.passed) {
      return {
        label: 'Passed',
        cls: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
        icon: CheckCircle2,
      }
    }
    return {
      label: 'Failed',
      cls: 'border-rose-500/40 bg-rose-500/10 text-rose-300',
      icon: XCircle,
    }
  }

  const badge = getOverallBadge()
  const BadgeIcon = badge.icon

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0c121e] p-5" data-testid="baseline-panel">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h3 className="text-base font-semibold text-white">Baseline</h3>
            <span
              className={`inline-flex items-center space-x-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badge.cls}`}
            >
              <BadgeIcon className="h-3.5 w-3.5" />
              <span>{badge.label}</span>
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Clean isolated execution verification before migration rehearsal begins
          </p>
        </div>

        {baseline.test_summary && (
          <div className="flex items-center space-x-3 rounded-md border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs">
            <span className="text-slate-400">Tests:</span>
            <span className="font-semibold text-emerald-400">
              {baseline.test_summary.passed} passed
            </span>
            {baseline.test_summary.failed > 0 && (
              <span className="font-semibold text-rose-400">
                {baseline.test_summary.failed} failed
              </span>
            )}
            <span className="text-slate-500">/ {baseline.test_summary.total} total</span>
          </div>
        )}
      </div>

      <div className="mt-4 space-y-3">
        {steps.map(({ label, result }) => (
          <StepRow key={result.step} label={label} result={result} />
        ))}
      </div>

      {baseline.notes && (
        <div className="mt-4 rounded-lg border border-slate-800/60 bg-slate-900/40 p-3 text-xs text-slate-400">
          <p className="font-mono">{baseline.notes}</p>
        </div>
      )}
    </div>
  )
}

function formatStatus(status: StepStatus): string {
  switch (status) {
    case 'SKIPPED_NOT_APPLICABLE':
      return 'NOT APPLICABLE'
    case 'ENVIRONMENT_UNAVAILABLE':
      return 'UNAVAILABLE'
    default:
      return status
  }
}

function StepRow({ label, result }: { label: string; result: CommandResult }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)
  const hasOutput = Boolean(result.stdout || result.stderr)

  const isPassed = result.status === 'PASSED'
  const isFailed = result.status === 'FAILED'
  const isTimeout = result.status === 'TIMEOUT'
  const isUnavailable = result.status === 'ENVIRONMENT_UNAVAILABLE'
  const isSkipped = result.status === 'SKIPPED_NOT_APPLICABLE' || result.status === 'SKIPPED'

  const handleCopy = () => {
    const text = [result.command, result.stdout, result.stderr].filter(Boolean).join('\n')
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className={`rounded-lg border transition-all ${
        isPassed
          ? 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
          : isTimeout
          ? 'border-amber-500/30 bg-amber-500/5'
          : isFailed
          ? 'border-rose-500/30 bg-rose-500/5'
          : isUnavailable
          ? 'border-amber-500/30 bg-amber-500/5'
          : 'border-slate-800/60 bg-slate-900/20 text-slate-400'
      }`}
      data-testid={`step-${result.step}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 p-3">
        <div className="flex items-center space-x-3">
          {isPassed && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
          {isTimeout && <AlertOctagon className="h-4 w-4 text-amber-400 shrink-0" />}
          {isFailed && <XCircle className="h-4 w-4 text-rose-400 shrink-0" />}
          {isUnavailable && <AlertOctagon className="h-4 w-4 text-amber-400 shrink-0" />}
          {isSkipped && <MinusCircle className="h-4 w-4 text-slate-500 shrink-0" />}

          <span className="text-xs font-semibold text-white">{label}</span>

          <span
            className={`rounded px-2 py-0.5 text-[10px] font-bold font-mono ${
              isPassed
                ? 'bg-emerald-500/20 text-emerald-300'
                : isTimeout
                ? 'bg-amber-500/20 text-amber-300'
                : isFailed
                ? 'bg-rose-500/20 text-rose-300'
                : isUnavailable
                ? 'bg-amber-500/20 text-amber-300'
                : 'bg-slate-800 text-slate-400'
            }`}
          >
            {formatStatus(result.status)}
          </span>

          <code className="hidden rounded bg-slate-950/80 px-2 py-0.5 text-[11px] font-mono text-cyan-300 md:inline-block max-w-[280px] lg:max-w-md truncate">
            {result.command}
          </code>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          {result.duration_seconds != null && (
            <span className="flex items-center space-x-1 text-slate-400 font-mono text-[11px]">
              <Clock className="h-3 w-3 text-slate-500" />
              <span>{result.duration_seconds.toFixed(1)}s</span>
            </span>
          )}

          {hasOutput && (
            <button
              type="button"
              onClick={() => setExpanded(!expanded)}
              className="inline-flex items-center space-x-1 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-[11px] font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition"
            >
              <Terminal className="h-3 w-3 text-slate-400" />
              <span>{expanded ? 'Hide' : 'Show output'}</span>
              {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
          )}
        </div>
      </div>

      {expanded && hasOutput && (
        <div className="border-t border-slate-800 bg-[#070b13] p-3 rounded-b-lg">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
              Standard Output & Errors
            </span>
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center space-x-1 text-[10px] font-mono text-slate-400 hover:text-slate-200"
            >
              {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <div className="max-h-64 overflow-y-auto space-y-2 font-mono text-xs">
            {result.stdout && (
              <pre className="whitespace-pre-wrap break-all text-slate-300 selection:bg-slate-800">
                {result.stdout}
              </pre>
            )}
            {result.stderr && (
              <pre className="whitespace-pre-wrap break-all text-rose-400 selection:bg-rose-950">
                {result.stderr}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
