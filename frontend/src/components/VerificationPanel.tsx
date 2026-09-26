/**
 * VerificationPanel — displays dynamic BASELINE vs TWIN comparison matrix,
 * failure clusters, Watsonx diagnoses, and repair records.
 */

import { useState } from 'react'
import {
  Shield,
  Cpu,
  FileCode,
} from 'lucide-react'
import type { BaselineResult, TwinResult, VerificationRun, StepStatus } from '../types'

interface VerificationPanelProps {
  baseline?: BaselineResult | null
  twinResult?: TwinResult | null
  verificationRun?: VerificationRun | null
}

export function VerificationPanel({
  baseline,
  twinResult,
  verificationRun,
}: VerificationPanelProps) {
  const [showDiff, setShowDiff] = useState(false)

  if (!twinResult && !verificationRun && !baseline) {
    return (
      <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center" data-testid="verification-pending">
        <Shield className="mx-auto h-7 w-7 text-zinc-500" />
        <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">Verification Pending</h3>
        <p className="mt-1 text-xs text-zinc-500 font-mono">
          Comparative baseline vs twin verification will run once migration actions are staged in the Twin workspace.
        </p>
      </div>
    )
  }

  const ver = verificationRun?.verification
  const isVerified = verificationRun?.passed ?? false
  const outcomeText = verificationRun
    ? isVerified
      ? 'VERIFIED'
      : 'REQUIRES HUMAN REVIEW'
    : baseline
    ? 'BASELINE RECORDED'
    : 'PENDING'

  // Extract all distinct steps checked (install, build, test, lint)
  const stepsList = ['install', 'build', 'test', 'lint'] as const

  const getStepStatus = (status?: StepStatus) => {
    switch (status) {
      case 'PASSED':
        return { label: 'PASS', color: 'text-emerald-400' }
      case 'FAILED':
        return { label: 'FAIL', color: 'text-red-400' }
      case 'TIMEOUT':
        return { label: 'TIMEOUT', color: 'text-amber-400' }
      case 'ENVIRONMENT_UNAVAILABLE':
        return { label: 'UNAVAILABLE', color: 'text-amber-400' }
      case 'SKIPPED_NOT_APPLICABLE':
      case 'SKIPPED':
        return { label: 'N/A', color: 'text-zinc-500' }
      default:
        return { label: '—', color: 'text-zinc-600' }
    }
  }

  return (
    <div className="space-y-4" data-testid="verification-panel">
      {/* ── Top Header & Outcome Banner ────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <Shield className="h-4 w-4 text-zinc-400" />
              <h3 className="text-base font-semibold text-white">Rehearsal Verification</h3>
              <span
                className={`font-mono text-sm font-bold flex items-center space-x-1 ${
                  isVerified ? 'text-emerald-400' : 'text-amber-400'
                }`}
                data-testid="verification-outcome"
              >
                <span>●</span>
                <span>{outcomeText}</span>
              </span>
            </div>
            <p className="mt-1 text-sm text-zinc-400">
              Comparative execution in isolated Git Twin worktree to guarantee zero regressions
            </p>
          </div>

          <div className="flex items-center space-x-3 text-sm font-mono">
            {ver && (
              <span className={`font-semibold ${ver.regression_count === 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {ver.regression_count} Regressions
              </span>
            )}
            {verificationRun?.round && (
              <span className="text-zinc-400">
                Round {verificationRun.round}
              </span>
            )}
          </div>
        </div>

        {/* Twin Isolation Callout */}
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 rounded border border-zinc-800 bg-zinc-900/50 px-3.5 py-2 text-sm text-zinc-300">
          <div className="flex items-center space-x-2">
            <span className="text-emerald-400 font-mono">✓</span>
            <span>
              <strong>Original repository protected.</strong> Rehearsal ran inside a disposable git-worktree Twin.
            </span>
          </div>
          {twinResult?.changed_files && (
            <span className="font-mono text-xs text-zinc-400">
              {twinResult.changed_files.length} modified file(s) in Twin
            </span>
          )}
        </div>
      </div>

      {/* ── Engineering Test Report Matrix: BASELINE vs TWIN ─────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-300">
          Baseline vs Twin Test Report
        </h4>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm font-mono">
            <thead>
              <tr className="border-b border-zinc-800 text-xs text-zinc-500 uppercase tracking-wider">
                <th className="pb-3 font-medium">Pipeline Step</th>
                <th className="pb-3 font-medium">Baseline</th>
                <th className="pb-3 font-medium">Twin</th>
                <th className="pb-3 font-medium">Parity</th>
                <th className="pb-3 font-medium text-right">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {stepsList.map((stepKey) => {
                const baseCmd = baseline ? baseline[stepKey] : undefined
                const twinCmd = ver ? ver[stepKey] : undefined

                if (!baseCmd && !twinCmd) return null

                const baseStatus = getStepStatus(baseCmd?.status)
                const twinStatus = getStepStatus(twinCmd?.status)

                const isRegressed =
                  baseCmd?.status === 'PASSED' && twinCmd?.status === 'FAILED'

                return (
                  <tr key={stepKey} className="hover:bg-zinc-900/30 transition-colors">
                    <td className="py-3 font-medium text-zinc-200 capitalize">
                      {stepKey}
                    </td>

                    <td className="py-3">
                      <span className={`font-semibold ${baseStatus.color}`}>
                        {baseStatus.label}
                      </span>
                    </td>

                    <td className="py-3">
                      <span className={`font-semibold ${twinStatus.color}`}>
                        {twinStatus.label}
                      </span>
                    </td>

                    <td className="py-3">
                      {!twinCmd ? (
                        <span className="text-zinc-600">
                          AWAITING
                        </span>
                      ) : isRegressed ? (
                        <span className="text-red-400 font-semibold">
                          REGRESSION
                        </span>
                      ) : (
                        <span className="text-emerald-400 font-semibold">
                          PASS
                        </span>
                      )}
                    </td>

                    <td className="py-3 text-right text-zinc-500">
                      {twinCmd?.duration_seconds != null
                        ? `${twinCmd.duration_seconds.toFixed(1)}s`
                        : baseCmd?.duration_seconds != null
                        ? `${baseCmd.duration_seconds.toFixed(1)}s`
                        : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Diagnosis & Repair Records (if applicable) ────────────────────── */}
      {verificationRun?.diagnoses && verificationRun.diagnoses.length > 0 && (
        <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
          <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3 mb-3">
            <Cpu className="h-4 w-4 text-zinc-400" />
            <h4 className="text-sm font-semibold uppercase tracking-wider text-zinc-300">
              Watsonx Failure Diagnosis & Targeted Repairs
            </h4>
          </div>

          <div className="space-y-3">
            {verificationRun.diagnoses.map((diag, idx) => (
              <div
                key={idx}
                className="rounded border border-zinc-800 bg-zinc-900/50 p-4 text-sm space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-semibold text-zinc-300 uppercase">
                      {diag.step} Failure
                    </span>
                    <span className="text-zinc-500 font-mono text-xs">
                      &bull; Confidence: {diag.confidence}
                    </span>
                  </div>
                  <span
                    className={`font-mono text-xs font-semibold ${
                      diag.repair_applied ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    {diag.repair_applied ? 'REPAIR APPLIED' : 'MANUAL REVIEW REQUIRED'}
                  </span>
                </div>

                <div>
                  <span className="text-zinc-500 font-medium">Root Cause: </span>
                  <span className="text-zinc-300 font-mono">{diag.root_cause}</span>
                </div>

                {diag.repair_notes && (
                  <div className="rounded bg-zinc-950 p-2 font-mono text-xs text-zinc-300 border border-zinc-800">
                    Repair Note: {diag.repair_notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Changed Files in Twin ─────────────────────────────────────────── */}
      {twinResult?.changed_files && twinResult.changed_files.length > 0 && (
        <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
          <div className="mb-3 flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center space-x-2">
              <FileCode className="h-4 w-4 text-zinc-400" />
              <h4 className="text-sm font-semibold uppercase tracking-wider text-zinc-300">
                Modified Files in Disposable Twin ({twinResult.changed_files.length})
              </h4>
            </div>
            {twinResult.git_diff && (
              <button
                type="button"
                onClick={() => setShowDiff(!showDiff)}
                className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm font-medium text-zinc-300 hover:bg-zinc-700 hover:text-white transition"
              >
                {showDiff ? 'Hide Diff' : 'Preview Diff'}
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm font-mono">
            {twinResult.changed_files.map((cf) => (
              <div
                key={cf.path}
                className="flex items-center justify-between rounded border border-zinc-800 bg-zinc-900/40 px-3 py-2"
              >
                <span className="text-zinc-300 truncate">{cf.path}</span>
                <span className="font-mono text-xs text-zinc-500 uppercase">
                  [{cf.change_type}]
                </span>
              </div>
            ))}
          </div>

          {showDiff && twinResult.git_diff && (
            <div className="mt-4 border-t border-zinc-800 pt-3">
              <pre className="max-h-80 overflow-y-auto rounded bg-zinc-950 p-3 font-mono text-xs text-zinc-300 border border-zinc-800 whitespace-pre-wrap">
                {twinResult.git_diff}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
