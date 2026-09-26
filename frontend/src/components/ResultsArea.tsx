/**
 * ResultsArea — Tabbed developer workspace for CodeShift analysis and rehearsal results.
 * Implements 7 shadcn/ui style tabs:
 * 1. Overview — Executive summary, 4 cardinal pillar cards, severity breakdown, agent handoff CTA
 * 2. Repository — Level 2 deep repository intelligence & AST inspection (RepoProfilePanel)
 * 3. Findings — Migration findings with severity filtering and code evidence (FindingsPanel)
 * 4. Migration Plan — Action item tracker with APPLIED/PROPOSED/REVIEW states (MigrationPlanPanel)
 * 5. Verification — Dynamic Baseline vs Twin matrix, regressions, failure clusters & Watsonx diagnosis (VerificationPanel)
 * 6. Diff — Syntax-highlighted git diff and changed files navigation (DiffViewer)
 * 7. Agent Pack — 8 agent-ready artifacts, prompt copier, and download pack (AgentPackPanel)
 */

import { useState } from 'react'
import {
  FolderGit2,
  Package,
  Activity,
  Clock,
  ArrowRight,
} from 'lucide-react'
import type {
  AgentTaskSpec,
  BaselineResult,
  MigrationFinding,
  MigrationPlan,
  Rehearsal,
  RepositoryProfile,
  TwinResult,
  VerificationRun,
} from '../types'
import { RepoProfilePanel } from './RepoProfilePanel'
import { FindingsPanel } from './FindingsPanel'
import { MigrationPlanPanel } from './MigrationPlanPanel'
import { VerificationPanel } from './VerificationPanel'
import { DiffViewer } from './DiffViewer'
import { AgentPackPanel } from './AgentPackPanel'

export type ResultsTab =
  | 'overview'
  | 'repository'
  | 'findings'
  | 'plan'
  | 'verification'
  | 'diff'
  | 'agentpack'

export interface ResultsAreaProps {
  rehearsal?: Rehearsal | null
  profile?: RepositoryProfile | null
  baseline?: BaselineResult | null
  migrationPlan?: MigrationPlan | null
  twinResult?: TwinResult | null
  verificationRun?: VerificationRun | null
  agentTaskSpec?: AgentTaskSpec | null
  hasAgentPack?: boolean
  isLoading?: boolean
  /** Backward-compatibility prop */
  findings?: MigrationFinding[]
}

export function ResultsArea({
  rehearsal,
  profile,
  baseline,
  migrationPlan,
  twinResult,
  verificationRun,
  agentTaskSpec,
  hasAgentPack = false,
  isLoading = false,
  findings: directFindings,
}: ResultsAreaProps) {
  const [activeTab, setActiveTab] = useState<ResultsTab>('overview')

  const effectiveFindings = migrationPlan?.findings || directFindings || []
  const hasRehearsal = Boolean(rehearsal || profile || baseline || effectiveFindings.length > 0)

  // Empty state when no rehearsal exists
  if (!hasRehearsal && !isLoading) {
    return (
      <div
        className="rounded border border-zinc-800 bg-[#121214] p-8 text-center"
        data-testid="results-empty"
      >
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="flex h-10 w-10 items-center justify-center rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
            <Activity className="h-5 w-5 text-zinc-300" />
          </div>
          <div className="max-w-md">
            <h3 className="text-sm font-semibold text-zinc-100">No Rehearsal Active</h3>
            <p className="mt-1 text-xs text-zinc-400 leading-relaxed font-sans">
              Enter a repository URL above or launch one of the Quick Start demos below to run
              automated intake, baseline execution, twin isolation, and verification.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Loading state when initial analysis is running
  if (isLoading && !hasRehearsal) {
    return (
      <div
        className="rounded border border-zinc-800 bg-[#121214] p-8 text-center"
        data-testid="results-loading"
      >
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="flex h-10 w-10 items-center justify-center rounded border border-zinc-800 bg-zinc-900 text-blue-400 animate-spin">
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Analyzing Repository Migration</h3>
            <p className="mt-1 text-xs text-zinc-400 font-mono">
              Cloning repository, scanning dependencies, and executing baseline checks...
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Metrics for overview and tab badges
  const criticalFindingsCount = effectiveFindings.filter((f) => f.severity === 'CRITICAL').length
  const highFindingsCount = effectiveFindings.filter((f) => f.severity === 'HIGH').length
  const actionsCount = migrationPlan?.planned_actions?.length || 0
  const actionsAppliedCount = twinResult?.actions_applied?.length || 0
  const changedFilesCount = twinResult?.changed_files?.length || 0
  const isVerified = verificationRun?.passed === true && verificationRun.verification.regression_count === 0
  const requiresReview =
    rehearsal?.status === 'REQUIRES_HUMAN_REVIEW' ||
    migrationPlan?.requires_human_review ||
    verificationRun?.requires_human_review

  return (
    <div className="space-y-4" data-testid="results-area">
      {/* ── Tab Navigation Bar ────────────────────────────────────────────── */}
      <div className="border-b border-zinc-800">
        <div className="flex items-center space-x-6 overflow-x-auto scrollbar-none px-1">
          <button
            type="button"
            onClick={() => setActiveTab('overview')}
            className={`pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'overview'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Overview
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('repository')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'repository'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Repository</span>
            {profile && (
              <span className="text-xs font-mono text-zinc-500">
                ({profile.framework || profile.package_manager})
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('findings')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'findings'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Findings</span>
            {effectiveFindings.length > 0 && (
              <span className={`text-xs font-mono ${criticalFindingsCount > 0 ? 'text-red-400 font-semibold' : 'text-zinc-500'}`}>
                ({effectiveFindings.length})
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('plan')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'plan'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Migration Plan</span>
            {actionsCount > 0 && (
              <span className="text-xs font-mono text-zinc-500">
                ({actionsCount})
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('verification')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'verification'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Verification</span>
            {verificationRun && (
              <span className={`text-xs font-mono ${isVerified ? 'text-emerald-400' : 'text-red-400'}`}>
                ●
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('diff')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'diff'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Diff</span>
            {changedFilesCount > 0 && (
              <span className="text-xs font-mono text-zinc-500">
                ({changedFilesCount})
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('agentpack')}
            className={`flex items-center space-x-1.5 pb-2.5 pt-1 text-sm font-medium border-b-2 transition select-none ${
              activeTab === 'agentpack'
                ? 'border-white text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Agent Pack</span>
            {hasAgentPack && (
              <span className="text-xs font-mono text-emerald-400">
                ●
              </span>
            )}
          </button>
        </div>
      </div>

      {/* ── TAB 1: OVERVIEW ──────────────────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Executive Summary Banner */}
          <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs text-zinc-400 uppercase tracking-wider">
                    Rehearsal Verdict
                  </span>
                  <span
                    className={`inline-flex items-center space-x-1 text-sm font-mono font-semibold ${
                      isVerified
                        ? 'text-emerald-400'
                        : requiresReview
                        ? 'text-amber-400'
                        : rehearsal?.status === 'FAILED'
                        ? 'text-red-400'
                        : 'text-blue-400'
                    }`}
                  >
                    <span>●</span>
                    <span>{rehearsal?.status || 'ANALYZING'}</span>
                  </span>
                </div>
                <h2 className="mt-1 text-lg font-semibold text-white">
                  {isVerified
                    ? 'Migration Rehearsal Successfully Verified'
                    : requiresReview
                    ? 'Migration Rehearsed — Human Review Required'
                    : rehearsal?.status === 'FAILED'
                    ? 'Rehearsal Verification Blocked with Diagnoses'
                    : 'Migration Analysis and Twin Rehearsal in Progress'}
                </h2>
                <p className="mt-1.5 text-sm text-zinc-400 max-w-2xl font-sans leading-relaxed">
                  {isVerified
                    ? 'All baseline verification checks passed in the isolated worktree Twin with 0 test regressions. The generated Agent Pack is ready for autonomous agent delegation.'
                    : requiresReview
                    ? 'Automated codemods were applied, but breaking changes or manual review items were identified that require developer confirmation before merge.'
                    : rehearsal?.status === 'FAILED'
                    ? 'Verification failed during compilation or test runs. Root cause analysis and repair attempts are documented in the Verification tab.'
                    : 'CodeShift is executing safe migration rehearsal in an isolated git worktree without touching your original repository.'}
                </p>
              </div>

              {/* Quick Jump CTA */}
              <div className="flex items-center space-x-2 shrink-0">
                <button
                  type="button"
                  onClick={() => setActiveTab('repository')}
                  className="rounded border border-zinc-700 bg-zinc-800 px-3.5 py-1.5 text-sm font-medium text-zinc-200 hover:bg-zinc-700 hover:text-white transition"
                >
                  Inspect Repo
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('agentpack')}
                  className="rounded bg-white px-4 py-2 text-sm font-semibold text-black transition hover:bg-zinc-200 flex items-center space-x-1.5"
                >
                  <span>Agent Pack</span>
                  <span>&rarr;</span>
                </button>
              </div>
            </div>

            {/* 4 Cardinal Pillars Grid */}
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Pillar 1: Baseline */}
              <div
                onClick={() => setActiveTab('verification')}
                className="cursor-pointer rounded border border-zinc-800 bg-zinc-900/60 p-3.5 transition hover:border-zinc-700"
              >
                <div className="flex items-center justify-between text-xs text-zinc-400">
                  <span className="font-mono uppercase text-xs font-medium text-zinc-500">
                    1. Baseline
                  </span>
                  <span className={`text-xs font-mono font-medium ${baseline?.passed ? 'text-emerald-400' : baseline?.status === 'ENVIRONMENT_UNAVAILABLE' || baseline?.status === 'TIMEOUT' ? 'text-amber-400' : 'text-red-400'}`}>
                    ●
                  </span>
                </div>
                <div className="mt-1 text-base font-semibold text-white">
                  {baseline?.status || 'PENDING'}
                </div>
                <div className="mt-1 flex items-center space-x-1 text-xs text-zinc-400 font-mono">
                  <span>Install: {baseline?.install?.status === 'PASSED' ? 'PASS' : baseline?.install?.status === 'TIMEOUT' ? 'TIMEOUT' : baseline?.install?.status === 'FAILED' ? 'FAIL' : '—'}</span>
                  <span>&bull;</span>
                  <span>Test: {baseline?.test?.status === 'PASSED' ? 'PASS' : baseline?.test?.status === 'TIMEOUT' ? 'TIMEOUT' : baseline?.test?.status === 'FAILED' ? 'FAIL' : '—'}</span>
                </div>
              </div>

              {/* Pillar 2: Twin Isolation */}
              <div
                onClick={() => setActiveTab('diff')}
                className="cursor-pointer rounded border border-zinc-800 bg-zinc-900/60 p-3.5 transition hover:border-zinc-700"
              >
                <div className="flex items-center justify-between text-xs text-zinc-400">
                  <span className="font-mono uppercase text-xs font-medium text-zinc-500">
                    2. Twin Isolation
                  </span>
                  <span className="text-cyan-400 text-xs font-mono">●</span>
                </div>
                <div className="mt-1 text-base font-semibold text-white">
                  {twinResult ? 'Created & Protected' : 'Initializing'}
                </div>
                <div className="mt-1 text-xs text-zinc-400 font-mono">
                  {changedFilesCount > 0
                    ? `${changedFilesCount} files modified in sandbox`
                    : 'Original repo untouched'}
                </div>
              </div>

              {/* Pillar 3: Migration Plan */}
              <div
                onClick={() => setActiveTab('plan')}
                className="cursor-pointer rounded border border-zinc-800 bg-zinc-900/60 p-3.5 transition hover:border-zinc-700"
              >
                <div className="flex items-center justify-between text-xs text-zinc-400">
                  <span className="font-mono uppercase text-xs font-medium text-zinc-500">
                    3. Migration
                  </span>
                  <span className="text-blue-400 text-xs font-mono">●</span>
                </div>
                <div className="mt-1 text-base font-semibold text-white">
                  {actionsAppliedCount > 0
                    ? `${actionsAppliedCount} / ${actionsCount} Applied`
                    : actionsCount > 0
                    ? `${actionsCount} Actions Proposed`
                    : 'Analyzing'}
                </div>
                <div className="mt-1 text-xs text-zinc-400 font-mono">
                  {rehearsal?.target_upgrade
                    ? `${rehearsal.target_upgrade.package} → ${rehearsal.target_upgrade.to_version}`
                    : 'Target upgrade'}
                </div>
              </div>

              {/* Pillar 4: Verification */}
              <div
                onClick={() => setActiveTab('verification')}
                className="cursor-pointer rounded border border-zinc-800 bg-zinc-900/60 p-3.5 transition hover:border-zinc-700"
              >
                <div className="flex items-center justify-between text-xs text-zinc-400">
                  <span className="font-mono uppercase text-xs font-medium text-zinc-500">
                    4. Verification
                  </span>
                  <span className={`text-xs font-mono ${isVerified ? 'text-emerald-400' : 'text-amber-400'}`}>
                    ●
                  </span>
                </div>
                <div className="mt-1 text-base font-semibold text-white">
                  {verificationRun
                    ? `${verificationRun.verification.regression_count} Regressions`
                    : 'Pending'}
                </div>
                <div className="mt-1 text-xs text-zinc-400 font-mono">
                  {verificationRun?.diagnoses && verificationRun.diagnoses.length > 0
                    ? `${verificationRun.diagnoses.length} diagnoses recorded`
                    : 'Verification suite'}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Findings & Plan Preview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Findings Summary Card */}
            <div className="rounded border border-zinc-800 bg-[#121214] p-5">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-amber-400 font-mono text-sm">▲</span>
                  <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Migration Findings</h3>
                  <span className="font-mono text-sm text-zinc-400">
                    ({effectiveFindings.length})
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab('findings')}
                  className="text-sm text-zinc-400 hover:text-white transition font-medium flex items-center space-x-1"
                >
                  <span>View All</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="mt-3 grid grid-cols-4 gap-2 text-center">
                <div className="rounded border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <div className="text-xs font-mono text-zinc-400 uppercase font-medium">Critical</div>
                  <div className="text-lg font-bold text-red-400">{criticalFindingsCount}</div>
                </div>
                <div className="rounded border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <div className="text-xs font-mono text-zinc-400 uppercase font-medium">High</div>
                  <div className="text-lg font-bold text-amber-400">{highFindingsCount}</div>
                </div>
                <div className="rounded border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <div className="text-xs font-mono text-zinc-400 uppercase font-medium">Medium</div>
                  <div className="text-lg font-bold text-zinc-200">
                    {effectiveFindings.filter((f) => f.severity === 'MEDIUM').length}
                  </div>
                </div>
                <div className="rounded border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <div className="text-xs font-mono text-zinc-400 uppercase font-medium">Low</div>
                  <div className="text-lg font-bold text-zinc-400">
                    {effectiveFindings.filter((f) => f.severity === 'LOW').length}
                  </div>
                </div>
              </div>

              {effectiveFindings.length > 0 ? (
                <div className="mt-3.5 space-y-2">
                  {effectiveFindings.slice(0, 3).map((f) => (
                    <div
                      key={f.id}
                      onClick={() => setActiveTab('findings')}
                      className="cursor-pointer rounded border border-zinc-800/80 bg-zinc-900/30 p-3 text-sm hover:border-zinc-700 transition"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-zinc-200 truncate">{f.title}</span>
                        <span className="text-xs font-mono text-zinc-500 shrink-0 ml-2">
                          {f.affected_files?.[0] || 'Repository'}
                        </span>
                      </div>
                      <p className="mt-1 text-zinc-400 text-xs line-clamp-1">{f.reason}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-sm text-zinc-500 font-mono text-center">
                  No migration findings detected.
                </p>
              )}
            </div>

            {/* Repository Snapshot Card */}
            <div className="rounded border border-zinc-800 bg-[#121214] p-5">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div className="flex items-center space-x-2">
                  <FolderGit2 className="h-4 w-4 text-zinc-400" />
                  <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Repository Identity</h3>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab('repository')}
                  className="text-sm text-zinc-400 hover:text-white transition font-medium flex items-center space-x-1"
                >
                  <span>Detailed AST</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>

              {profile ? (
                <div className="mt-3 space-y-2 text-sm">
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Repository</span>
                    <span className="font-mono text-zinc-200">{profile.name || 'Target Project'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Ecosystem & Runtime</span>
                    <span className="font-mono text-zinc-200">
                      {profile.ecosystem} &bull; {profile.runtime || 'node'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Framework</span>
                    <span className="font-mono text-zinc-200">{profile.framework || 'React'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Package Manager</span>
                    <span className="font-mono text-zinc-200">
                      {profile.package_manager} {profile.package_manager_version || ''}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-zinc-500">Lockfile Detected</span>
                    <span className="font-mono text-zinc-300">
                      {profile.lockfile || 'None'}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-sm text-zinc-500 font-mono text-center">
                  Scanning repository identity...
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: REPOSITORY ────────────────────────────────────────────── */}
      {activeTab === 'repository' && (
        <div>
          {profile ? (
            <RepoProfilePanel profile={profile} />
          ) : (
            <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center">
              <FolderGit2 className="mx-auto h-7 w-7 text-zinc-500" />
              <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">
                Repository Analysis In Progress
              </h3>
              <p className="mt-1 text-xs text-zinc-500 font-mono">
                Scanner is extracting manifest, scripts, and runtime engine constraints.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: FINDINGS ──────────────────────────────────────────────── */}
      {activeTab === 'findings' && (
        <div>
          <FindingsPanel findings={effectiveFindings} />
        </div>
      )}

      {/* ── TAB 4: MIGRATION PLAN ────────────────────────────────────────── */}
      {activeTab === 'plan' && (
        <div>
          <MigrationPlanPanel plan={migrationPlan} twinResult={twinResult} />
        </div>
      )}

      {/* ── TAB 5: VERIFICATION ──────────────────────────────────────────── */}
      {activeTab === 'verification' && (
        <div>
          <VerificationPanel baseline={baseline} verificationRun={verificationRun} twinResult={twinResult} />
        </div>
      )}

      {/* ── TAB 6: DIFF ──────────────────────────────────────────────────── */}
      {activeTab === 'diff' && (
        <div>
          <DiffViewer twinResult={twinResult} />
        </div>
      )}

      {/* ── TAB 7: AGENT PACK ────────────────────────────────────────────── */}
      {activeTab === 'agentpack' && (
        <div>
          {rehearsal ? (
            <AgentPackPanel
              rehearsalId={rehearsal.id}
              agentTaskSpec={agentTaskSpec}
              hasAgentPack={hasAgentPack}
            />
          ) : (
            <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center">
              <Package className="mx-auto h-7 w-7 text-zinc-500" />
              <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">Agent Pack Pending</h3>
              <p className="mt-1 text-xs text-zinc-500 font-mono">
                The agent handoff package will be synthesized once rehearsal verification completes.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
