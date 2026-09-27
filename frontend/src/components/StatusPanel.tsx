/**
 * StatusPanel — displays current rehearsal stage, status badge, active operation,
 * dynamic baseline sequence, soft waiting message, rotating technical facts,
 * and explicit TIMEOUT failure state.
 * Dense developer infrastructure styling.
 */

import { useEffect, useRef, useState } from 'react'
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  AlertOctagon,
  Clock,
} from 'lucide-react'
import type { BaselineResult, CommandResult, RehearsalStage, RehearsalStatus } from '../types'

interface StatusPanelProps {
  stage: RehearsalStage
  status: RehearsalStatus
  errorMessage?: string
  activeOperation?: string | null
  baseline?: BaselineResult | null
  onApprove?: () => void | Promise<void>
  isApproving?: boolean
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

interface RotatingSnippet {
  category: 'WHILE YOU WAIT' | 'WHY CODESHIFT'
  text: string
}

const ROTATING_SNIPPETS: RotatingSnippet[] = [
  {
    category: 'WHY CODESHIFT',
    text: 'Framework upgrades are rarely just version bumps. Breaking changes, dependency conflicts, regressions, and compatibility issues can turn a migration into weeks or months of engineering investigation.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'JavaScript was first created by Brendan Eich at Netscape in 1995 in just 10 days.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'CodeShift compresses that investigation into an executable rehearsal: scan, analyze, migrate, verify, diagnose, and repair — inside a disposable Twin.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Git was created by Linus Torvalds for the Linux kernel project in 2005.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Your original repository stays untouched. CodeShift tests the migration in an isolated Twin before implementation reaches the real codebase.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'TypeScript is compiled to standard JavaScript and was created by Anders Hejlsberg at Microsoft in 2012.',
  },
  {
    category: 'WHY CODESHIFT',
    text: "Don't guess whether an upgrade will work. CodeShift establishes a baseline, rehearses the migration, and compares verification results.",
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'React was originally open-sourced by Facebook at JSConf US in May 2013.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'AI explains what needs to change. Deterministic execution applies safe changes. Verification checks whether the result actually works.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Node.js was initially created by Ryan Dahl in 2009 based on Google Chrome V8 engine.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'CodeShift turns migration findings into an agent-ready implementation package, so the next step is execution rather than starting the investigation from scratch.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Vite leverages native browser ES modules during development for instant HMR without bundling.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'For supported migrations, CodeShift is designed to compress a workflow that can take days of manual investigation into a single rehearsal measured in minutes.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Lockfiles (package-lock, yarn.lock, pnpm-lock) guarantee deterministic dependency trees across development environments.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Supported migrations can move from repository analysis to verified rehearsal in under 10 minutes on suitable repositories and environments.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'The npm registry was founded in 2010 and currently hosts over 3 million open-source JavaScript packages.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Isolated Twins eliminate risk. If a migration step breaks, your production branch and local repository remain completely unaffected.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Webpack was created by Tobias Koppers in 2012 to enable code-splitting and asset bundling for complex web apps.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Automated dependency tree resolution discovers peer dependency incompatibilities before you trigger production build pipelines.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'pnpm uses a content-addressable storage model with hard links, saving gigabytes of disk space on multi-project machines.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Verification runs the exact test, build, and lint commands your team relies on, providing mathematical proof of migration success.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Yarn was open-sourced in 2016 through collaboration between Facebook, Exponent, Google, and Tilde.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'CodeShift outputs an Agent Task Spec that AI coding agents can consume directly to execute pull requests with zero guesswork.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'React 18 introduced concurrent rendering features, automatic state batching, and useTransition for responsive UIs.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Catching breaking changes during an automated rehearsal saves engineering teams dozens of hours of manual debugging in staging.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Semantic Versioning (SemVer) standardizes version numbers as MAJOR.MINOR.PATCH to explicitly signal breaking API modifications.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'With CodeShift, migration knowledge is version-controlled and codified into reusable recipes rather than lost in wiki documentation.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'Node.js 18 introduced native global fetch, aligning server-side JavaScript with browser web standards.',
  },
  {
    category: 'WHY CODESHIFT',
    text: 'Continuous rehearsals transform framework upgrades from dreaded annual engineering blockades into routine, manageable maintenance.',
  },
  {
    category: 'WHILE YOU WAIT',
    text: 'ESLint was created by Nicholas C. Zakas in 2013 to provide pluggable static analysis rules for JavaScript codebases.',
  },
]

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export function StatusPanel({
  stage,
  status,
  errorMessage,
  activeOperation,
  baseline,
  onApprove,
  isApproving = false,
}: StatusPanelProps) {
  const isRunning = status === 'RUNNING'
  const isFailed = status === 'FAILED'
  const isComplete = status === 'COMPLETE'
  const isReview = status === 'REQUIRES_HUMAN_REVIEW' || stage === 'REQUIRES_HUMAN_REVIEW'

  const [now, setNow] = useState<number>(Date.now())
  const [snippetIndex, setSnippetIndex] = useState<number>(0)
  const [snippetVisible, setSnippetVisible] = useState<boolean>(true)

  // Track start time of active operation or process if active_started_at is not provided by backend
  const opStartRef = useRef<{ op: string; time: number } | null>(null)
  const processStartRef = useRef<number | null>(null)

  useEffect(() => {
    if (isRunning) {
      if (!processStartRef.current) {
        processStartRef.current = Date.now()
      }
    } else {
      processStartRef.current = null
    }
  }, [isRunning])

  useEffect(() => {
    if (activeOperation) {
      if (!opStartRef.current || opStartRef.current.op !== activeOperation) {
        opStartRef.current = { op: activeOperation, time: Date.now() }
      }
    } else {
      opStartRef.current = null
    }
  }, [activeOperation])

  // Tick timer every second while running
  useEffect(() => {
    if (!isRunning) return
    const timer = setInterval(() => {
      setNow(Date.now())
    }, 1000)
    return () => clearInterval(timer)
  }, [isRunning])

  // Rotate technical facts and product value snippets every 6.5s when waiting
  useEffect(() => {
    if (!isRunning) return
    const interval = setInterval(() => {
      setSnippetVisible(false)
      setTimeout(() => {
        setSnippetIndex((prev) => (prev + 1) % ROTATING_SNIPPETS.length)
        setSnippetVisible(true)
      }, 300)
    }, 6500)
    return () => clearInterval(interval)
  }, [isRunning])

  // Calculate elapsed time for currently active step or process without resetting on every poll
  let elapsedSeconds = 0
  if (baseline?.active_started_at) {
    elapsedSeconds = Math.max(0, Math.floor(now / 1000 - baseline.active_started_at))
  } else if (opStartRef.current) {
    elapsedSeconds = Math.max(0, Math.floor((now - opStartRef.current.time) / 1000))
  } else if (processStartRef.current) {
    elapsedSeconds = Math.max(0, Math.floor((now - processStartRef.current) / 1000))
  }

  const timeoutLimit = baseline?.active_timeout ?? 300
  const isTimeoutError =
    isFailed &&
    (baseline?.status === 'TIMEOUT' ||
      baseline?.notes?.toLowerCase().includes('timed out') ||
      errorMessage?.toLowerCase().includes('timed out') ||
      errorMessage?.toLowerCase().includes('timeout'))

  // Find timed out step if applicable
  const timedOutStep: CommandResult | undefined =
    baseline?.install?.status === 'TIMEOUT'
      ? baseline.install
      : baseline?.build?.status === 'TIMEOUT'
      ? baseline.build
      : baseline?.test?.status === 'TIMEOUT'
      ? baseline.test
      : baseline?.lint?.status === 'TIMEOUT'
      ? baseline.lint
      : undefined

  const badgeText = isComplete
    ? 'Complete'
    : isRunning
    ? 'Running'
    : isTimeoutError
    ? 'Timeout'
    : isFailed
    ? 'Failed'
    : isReview
    ? 'Requires Review'
    : status

  // Baseline step sequence detection
  const baselineSequence = [
    { key: 'install', label: 'Install', res: baseline?.install },
    { key: 'build', label: 'Build', res: baseline?.build },
    { key: 'test', label: 'Test', res: baseline?.test },
    { key: 'lint', label: 'Lint', res: baseline?.lint },
  ]

  const activeStepKey = baseline?.active_step || (isRunning && stage === 'BASELINING' ? 'install' : null)
  const activeStepLabel =
    baselineSequence.find((s) => s.key === activeStepKey)?.label || 'Baseline step'

  // Show soft waiting message and rotating quotes/facts after 10s for ANY running process
  const showWaitingPanel = isRunning && elapsedSeconds >= 10

  return (
    <div
      className={`rounded border border-zinc-800 bg-[#121214] p-4 transition-all space-y-3 ${
        isTimeoutError
          ? 'border-l-2 border-l-amber-500'
          : isFailed
          ? 'border-l-2 border-l-red-500'
          : isReview
          ? 'border-l-2 border-l-amber-500'
          : isComplete
          ? 'border-l-2 border-l-emerald-500'
          : 'border-l-2 border-l-blue-500'
      }`}
      data-testid="status-panel"
    >
      {/* ── Primary Status Row ────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2.5">
          {isRunning && <Loader2 className="h-4 w-4 animate-spin text-blue-400 shrink-0" />}
          {isComplete && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
          {isTimeoutError && <AlertOctagon className="h-4 w-4 text-amber-400 shrink-0" />}
          {isFailed && !isTimeoutError && <AlertCircle className="h-4 w-4 text-red-400 shrink-0" />}
          {isReview && <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />}

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

        <div className="flex items-center space-x-3">
          {isRunning && elapsedSeconds > 0 && (
            <span
              className="flex items-center space-x-1 text-xs font-mono text-zinc-400 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded"
              data-testid="status-elapsed"
            >
              <Clock className="h-3 w-3 text-zinc-500" />
              <span>Elapsed: {formatDuration(elapsedSeconds)}</span>
            </span>
          )}

          <span
            className={`inline-flex items-center space-x-1.5 text-sm font-mono font-medium ${
              isComplete
                ? 'text-emerald-400'
                : isTimeoutError
                ? 'text-amber-400'
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
      </div>

      {/* ── Dynamic Baseline Steps Sequence ───────────────────────────────── */}
      {stage === 'BASELINING' && (
        <div
          className="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono"
          data-testid="baseline-sequence"
        >
          <span className="text-zinc-500 text-[11px] uppercase mr-1">Baseline:</span>
          {baselineSequence.map(({ key, label, res }) => {
            const isStepActive = isRunning && activeStepKey === key
            const isPassed = res?.status === 'PASSED'
            const isStepFailed = res?.status === 'FAILED'
            const isStepTimeout = res?.status === 'TIMEOUT'
            const isSkipped =
              res?.status === 'SKIPPED' || res?.status === 'SKIPPED_NOT_APPLICABLE'

            return (
              <span
                key={key}
                className={`inline-flex items-center space-x-1.5 rounded px-2 py-0.5 border ${
                  isStepActive
                    ? 'border-blue-500/60 bg-blue-500/10 text-blue-300 font-semibold'
                    : isPassed
                    ? 'border-emerald-800/60 bg-emerald-950/30 text-emerald-400'
                    : isStepTimeout
                    ? 'border-amber-800/60 bg-amber-950/30 text-amber-300'
                    : isStepFailed
                    ? 'border-red-800/60 bg-red-950/30 text-red-400'
                    : isSkipped
                    ? 'border-zinc-800 bg-zinc-900/40 text-zinc-500'
                    : 'border-zinc-800 bg-zinc-900/60 text-zinc-400'
                }`}
              >
                {isStepActive ? (
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
                ) : isPassed ? (
                  <span className="text-emerald-400">✓</span>
                ) : isStepTimeout ? (
                  <span className="text-amber-400">⏱</span>
                ) : isStepFailed ? (
                  <span className="text-red-400">✕</span>
                ) : (
                  <span className="text-zinc-500">○</span>
                )}
                <span>{label}</span>
                {res?.duration_seconds != null && (
                  <span className="text-[10px] text-zinc-500">
                    ({res.duration_seconds.toFixed(0)}s)
                  </span>
                )}
              </span>
            )
          })}
        </div>
      )}

      {/* ── Soft Waiting Message (after 30-45s) ───────────────────────────── */}
      {showWaitingPanel && (
        <div
          className="rounded border border-zinc-800 bg-zinc-900/70 p-3.5 space-y-2.5 transition-all"
          data-testid="waiting-panel"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800/80 pb-2">
            <div className="flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-amber-400/80 animate-pulse" />
              <span className="text-xs font-semibold uppercase tracking-wider text-zinc-200 font-mono">
                Still working
              </span>
            </div>
            <div className="text-xs font-mono text-zinc-400">
              <span className="text-zinc-200">
                {stage === 'BASELINING' ? activeStepLabel : (activeOperation || STAGE_LABELS[stage] || stage)}
              </span>
              {' '}&bull;{' '}
              <span>{formatDuration(elapsedSeconds)} elapsed</span>
              {stage === 'BASELINING' && (
                <>
                  {' '}&bull;{' '}
                  <span className="text-zinc-500">Timeout limit {formatDuration(timeoutLimit)}</span>
                </>
              )}
            </div>
          </div>

          <p className="text-xs text-zinc-400 font-mono leading-relaxed">
            {stage === 'BASELINING'
              ? 'This repository has a cold dependency/build environment. Baseline checks can take a few minutes on larger repositories.'
              : 'Operation in progress. Initial cold runs and repository checks can take a few moments.'}
          </p>

          {/* ── Rotating Content (WHILE YOU WAIT & WHY CODESHIFT) ──────────── */}
          <div
            className="pt-2 border-t border-zinc-800/80 flex flex-col space-y-2"
            data-testid="rotating-facts-panel"
          >
            <div className="flex items-center space-x-2">
              <span
                className={`rounded px-2.5 py-0.5 text-xs font-mono uppercase tracking-wider font-semibold border ${
                  ROTATING_SNIPPETS[snippetIndex].category === 'WHY CODESHIFT'
                    ? 'border-blue-700/60 bg-blue-950/40 text-blue-300'
                    : 'border-zinc-700 bg-zinc-800 text-zinc-400'
                }`}
                data-testid="rotating-category-badge"
              >
                {ROTATING_SNIPPETS[snippetIndex].category}
              </span>
            </div>
            <div
              className={`text-sm md:text-base text-zinc-200 font-mono leading-relaxed transition-opacity duration-300 min-h-[3.5rem] ${
                snippetVisible ? 'opacity-100' : 'opacity-0'
              }`}
              data-testid="rotating-snippet-text"
            >
              &ldquo;{ROTATING_SNIPPETS[snippetIndex].text}&rdquo;
            </div>

            {/* ── Thin Progress Bar Synchronized with 6.5s Interval ─────────── */}
            <div
              className="h-[2px] w-full bg-zinc-800/80 rounded-full overflow-hidden"
              data-testid="rotating-progress-track"
            >
              <div
                key={snippetIndex}
                data-testid="rotating-progress-bar"
                className={`h-full rounded-full transition-all ${
                  ROTATING_SNIPPETS[snippetIndex].category === 'WHY CODESHIFT'
                    ? 'bg-blue-400/80'
                    : 'bg-zinc-400/80'
                }`}
                style={{
                  animation: 'snippetProgress 6500ms linear forwards',
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Human Review Action Banner ────────────────────────────────────── */}
      {isReview && (
        <div
          className="rounded border border-amber-800/80 bg-amber-950/25 p-3.5 space-y-2.5 font-mono text-xs"
          data-testid="review-action-banner"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-amber-300 font-semibold text-sm">
                <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
                <span>Review Recommended — Migration Rehearsed</span>
              </div>
              <p className="text-zinc-300 text-xs font-normal">
                Rehearsal produced actionable findings or non-blocking anomalies. You can acknowledge and mark the migration complete.
              </p>
            </div>
            {onApprove && (
              <button
                type="button"
                data-testid="btn-approve-rehearsal"
                disabled={isApproving}
                onClick={onApprove}
                className="inline-flex items-center space-x-2 rounded border border-emerald-600 bg-emerald-600 hover:bg-emerald-500 px-3.5 py-2 text-xs font-semibold text-white transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
              >
                {isApproving ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-white" />
                    <span>Marking Complete...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-3.5 w-3.5 text-white" />
                    <span>Approve & Complete Migration</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Explicit TIMEOUT Failure Box ───────────────────────────────────── */}
      {isTimeoutError && (
        <div
          className="rounded border border-amber-800/80 bg-amber-950/20 p-3.5 space-y-2.5 font-mono text-xs"
          data-testid="timeout-details"
        >
          <div className="flex items-center justify-between border-b border-amber-900/50 pb-2">
            <div className="flex items-center space-x-2 text-amber-300 font-semibold text-sm">
              <AlertOctagon className="h-4 w-4 text-amber-400" />
              <span>TIMEOUT</span>
            </div>
            <span className="text-amber-400/80">
              Elapsed: {formatDuration(timedOutStep?.duration_seconds || timeoutLimit || 300)}
            </span>
          </div>

          {timedOutStep?.command && (
            <div>
              <span className="text-zinc-500 text-[10px] uppercase block mb-0.5">Command:</span>
              <code className="text-zinc-200 bg-zinc-900/80 border border-zinc-800 px-2 py-1 rounded block overflow-x-auto text-[11px]">
                {timedOutStep.command}
              </code>
            </div>
          )}

          <div>
            <span className="text-zinc-500 text-[10px] uppercase block mb-0.5">Reason:</span>
            <span className="text-amber-200">
              Command exceeded the configured timeout limit ({timedOutStep?.duration_seconds ? `${timedOutStep.duration_seconds.toFixed(0)}s` : `${timeoutLimit}s`}).
            </span>
          </div>

          {(timedOutStep?.stderr || errorMessage) && (
            <div className="pt-1">
              <span className="text-zinc-500 text-[10px] uppercase block mb-1">
                Execution Output / Error Details:
              </span>
              <pre className="rounded bg-black/60 p-2.5 text-[11px] text-amber-300 whitespace-pre-wrap max-h-48 overflow-y-auto border border-zinc-800/80">
                {timedOutStep?.stderr || errorMessage}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Standard Error Display (if not timeout) */}
      {errorMessage && !isTimeoutError && (
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
