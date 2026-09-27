/**
 * Main App component — CodeShift application shell.
 *
 * Modern developer infrastructure product for repository migration rehearsal.
 * Wires the RehearsalForm & QuickStart demos to the backend API:
 * 1. Submit URL / ZIP / Quick Start Demo
 * 2. Poll GET /api/rehearsals/{id} until terminal stage
 * 3. Display WorkflowStepper, StatusPanel, and full-featured tabbed ResultsArea:
 *    Overview, Repository, Findings, Migration Plan, Verification, Diff, Agent Pack.
 */

import { useEffect, useRef, useState } from 'react'
import { ExternalLink } from 'lucide-react'
import { Header } from './components/Header'
import { RehearsalForm, type RehearsalFormValues } from './components/RehearsalForm'
import { WorkflowStepper } from './components/WorkflowStepper'
import { StatusPanel } from './components/StatusPanel'
import { QuickStartSection } from './components/QuickStartSection'
import { ResultsArea } from './components/ResultsArea'
import {
  ApiClientError,
  getRehearsalStatus,
  launchDemo,
  startRehearsalFromUrl,
  startRehearsalFromZip,
} from './api/client'
import type {
  AgentTaskSpec,
  BaselineResult,
  MigrationPlan,
  Rehearsal,
  RehearsalStage,
  RehearsalStatus,
  RepositoryProfile,
  TwinResult,
  VerificationRun,
} from './types'
import './App.css'

const TERMINAL_STAGES: RehearsalStage[] = ['COMPLETE', 'FAILED', 'REQUIRES_HUMAN_REVIEW']
const POLL_INTERVAL_MS = 2000

interface AppState {
  rehearsal: Rehearsal | null
  profile: RepositoryProfile | null
  baseline: BaselineResult | null
  migrationPlan: MigrationPlan | null
  twinResult: TwinResult | null
  verificationRun: VerificationRun | null
  agentTaskSpec: AgentTaskSpec | null
  hasAgentPack: boolean
  errorMessage: string | null
  isLoading: boolean
}

const INITIAL_STATE: AppState = {
  rehearsal: null,
  profile: null,
  baseline: null,
  migrationPlan: null,
  twinResult: null,
  verificationRun: null,
  agentTaskSpec: null,
  hasAgentPack: false,
  errorMessage: null,
  isLoading: false,
}

function App() {
  const [state, setState] = useState<AppState>(INITIAL_STATE)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  function stopPolling() {
    if (pollRef.current != null) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  // Clean up on unmount
  useEffect(() => () => stopPolling(), [])

  function startPolling(rehearsalId: string) {
    stopPolling()
    pollRef.current = setInterval(async () => {
      try {
        const data = await getRehearsalStatus(rehearsalId)
        setState((prev) => ({
          ...prev,
          rehearsal: data.rehearsal,
          profile: data.repo_profile ?? prev.profile,
          baseline: data.baseline ?? prev.baseline,
          migrationPlan: data.migration_plan ?? prev.migrationPlan,
          twinResult: data.twin_result ?? prev.twinResult,
          verificationRun: data.verification_run ?? prev.verificationRun,
          agentTaskSpec: data.agent_task_spec ?? prev.agentTaskSpec,
          hasAgentPack: data.has_agent_pack ?? prev.hasAgentPack,
          isLoading: !TERMINAL_STAGES.includes(data.rehearsal.stage),
          errorMessage: data.rehearsal.error_message ?? null,
        }))
        if (TERMINAL_STAGES.includes(data.rehearsal.stage)) {
          stopPolling()
        }
      } catch (err) {
        console.error('Polling error', err)
        stopPolling()
        setState((prev) => ({
          ...prev,
          isLoading: false,
          errorMessage: 'Lost connection to backend. Please refresh and try again.',
        }))
      }
    }, POLL_INTERVAL_MS)
  }

  async function handleStartRehearsal(values: RehearsalFormValues) {
    stopPolling()
    setState({ ...INITIAL_STATE, isLoading: true })

    try {
      let data
      if (values.mode === 'url') {
        data = await startRehearsalFromUrl({
          repository_url: values.repositoryUrl,
          target_package: values.targetPackage,
          target_version: values.targetVersion,
          discovery_id: values.discoveryId,
        })
      } else {
        if (!values.zipFile) return
        data = await startRehearsalFromZip(
          values.zipFile,
          values.targetPackage,
          values.targetVersion,
          undefined,
          values.discoveryId,
        )
      }

      setState({
        rehearsal: data.rehearsal,
        profile: data.repo_profile ?? null,
        baseline: data.baseline ?? null,
        migrationPlan: data.migration_plan ?? null,
        twinResult: data.twin_result ?? null,
        verificationRun: data.verification_run ?? null,
        agentTaskSpec: data.agent_task_spec ?? null,
        hasAgentPack: data.has_agent_pack ?? false,
        errorMessage: null,
        isLoading: !TERMINAL_STAGES.includes(data.rehearsal.stage),
      })

      startPolling(data.rehearsal.id)
    } catch (err) {
      let msg = 'Failed to start rehearsal.'
      if (err instanceof ApiClientError) {
        const body = err.body as Record<string, unknown> | null
        msg = (body?.detail as string) || msg
      } else if (err instanceof Error) {
        msg = err.message
      }
      setState({ ...INITIAL_STATE, errorMessage: msg, isLoading: false })
    }
  }

  async function handleLaunchDemo(demoId: string) {
    stopPolling()
    setState({ ...INITIAL_STATE, isLoading: true })

    try {
      const data = await launchDemo(demoId)
      setState({
        rehearsal: data.rehearsal,
        profile: data.repo_profile ?? null,
        baseline: data.baseline ?? null,
        migrationPlan: data.migration_plan ?? null,
        twinResult: data.twin_result ?? null,
        verificationRun: data.verification_run ?? null,
        agentTaskSpec: data.agent_task_spec ?? null,
        hasAgentPack: data.has_agent_pack ?? false,
        errorMessage: null,
        isLoading: !TERMINAL_STAGES.includes(data.rehearsal.stage),
      })

      startPolling(data.rehearsal.id)
    } catch (err) {
      let msg = 'Failed to launch demo rehearsal.'
      if (err instanceof ApiClientError) {
        const body = err.body as Record<string, unknown> | null
        msg = (body?.detail as string) || msg
      } else if (err instanceof Error) {
        msg = err.message
      }
      setState({ ...INITIAL_STATE, errorMessage: msg, isLoading: false })
    }
  }

  function handleNewRehearsal() {
    stopPolling()
    setState(INITIAL_STATE)
  }

  const currentStage: RehearsalStage = state.rehearsal?.stage ?? 'INTAKE'
  const currentStatus: RehearsalStatus =
    state.rehearsal?.status ?? (state.isLoading ? 'RUNNING' : 'PENDING')
  const showStatus = state.rehearsal != null || state.errorMessage != null || state.isLoading
  const hasActiveRehearsal = Boolean(state.rehearsal || state.isLoading)

  return (
    <div className="cs-app bg-[#09090b] text-zinc-100 min-h-screen" data-testid="app-root">
      <Header
        subtitle="Migration Rehearsal Engine"
        hasActiveRehearsal={hasActiveRehearsal}
        onNewRehearsal={handleNewRehearsal}
      />

      <main className="cs-main mx-auto w-full max-w-7xl px-4 sm:px-6 py-6 space-y-6">
        {/* ── Active Rehearsal Workspace Header ────────────────────────── */}
        {state.rehearsal && (
          <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2.5">
                  <span className="flex h-2 w-2 rounded-full bg-blue-400" />
                  <span className="text-sm font-mono font-semibold uppercase tracking-wider text-zinc-400">
                    Active Rehearsal Workspace
                  </span>
                  <span className="font-mono text-sm text-zinc-500">
                    ID: {state.rehearsal.id.slice(0, 8)}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-2.5">
                  <h2 className="text-lg font-semibold text-white">
                    {state.profile?.name ||
                      state.rehearsal.repository.url?.split('/').pop()?.replace('.git', '') ||
                      'Target Repository'}
                  </h2>
                  {state.rehearsal.repository.url && (
                    <a
                      href={state.rehearsal.repository.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center space-x-1 rounded bg-zinc-900 border border-zinc-800 px-2.5 py-1 text-sm font-mono text-zinc-400 hover:text-white transition"
                    >
                      <span className="max-w-[220px] truncate">
                        {state.rehearsal.repository.url}
                      </span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  )}
                  {state.rehearsal.repository.is_demo && (
                    <span className="font-mono text-xs text-zinc-500 uppercase">
                      [DEMO REPO]
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-xs uppercase font-mono tracking-wider text-zinc-500">
                    Migration Target
                  </div>
                  <div className="text-sm font-mono font-semibold text-zinc-200">
                    {state.rehearsal.target_upgrade.package} &bull;{' '}
                    {state.rehearsal.target_upgrade.from_version ? (
                      <>
                        <span className="text-zinc-500">
                          {state.rehearsal.target_upgrade.from_version}
                        </span>{' '}
                        &rarr;{' '}
                      </>
                    ) : null}
                    <span className="text-emerald-400 font-bold">
                      {state.rehearsal.target_upgrade.to_version}
                    </span>
                  </div>
                </div>

                <div className="border-l border-zinc-800 pl-4">
                  <div className="text-xs uppercase font-mono tracking-wider text-zinc-500">
                    Status
                  </div>
                  <span
                    className={`inline-flex items-center space-x-1 text-sm font-mono font-bold ${
                      currentStatus === 'COMPLETE'
                        ? 'text-emerald-400'
                        : currentStatus === 'FAILED'
                        ? 'text-red-400'
                        : currentStatus === 'REQUIRES_HUMAN_REVIEW'
                        ? 'text-amber-400'
                        : 'text-blue-400'
                    }`}
                  >
                    <span>●</span>
                    <span>{currentStatus}</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Workflow Stepper */}
            <div className="pt-4">
              <WorkflowStepper stage={currentStage} status={currentStatus} />
            </div>
          </div>
        )}

        {/* ── Status Banner / Alerts ─────────────────────────────────────── */}
        {showStatus && (
          <section className="cs-section" aria-label="Rehearsal status">
            <StatusPanel
              stage={currentStage}
              status={currentStatus}
              errorMessage={state.errorMessage ?? undefined}
              activeOperation={state.rehearsal?.active_operation}
              baseline={state.baseline}
            />
          </section>
        )}

        {/* ── Intake Form ──────────────────────────────────────────────── */}
        <section className="cs-section" aria-label="Start a rehearsal">
          <RehearsalForm onSubmit={handleStartRehearsal} disabled={state.isLoading} />
        </section>

        {/* ── Quick Start Live Demos from /api/demos (Landing Only) ──────── */}
        {!state.rehearsal && (
          <section className="cs-section pt-2" aria-label="Quick Start Demos">
            <QuickStartSection
              onLaunchDemo={handleLaunchDemo}
              isLaunching={state.isLoading}
            />
          </section>
        )}

        {/* ── Main Tabbed Results Workspace ──────────────────────────────── */}
        <section className="cs-section" aria-label="Rehearsal analysis results">
          <ResultsArea
            rehearsal={state.rehearsal}
            profile={state.profile}
            baseline={state.baseline}
            migrationPlan={state.migrationPlan}
            twinResult={state.twinResult}
            verificationRun={state.verificationRun}
            agentTaskSpec={state.agentTaskSpec}
            hasAgentPack={state.hasAgentPack}
            isLoading={state.isLoading}
          />
        </section>
      </main>

      <footer className="cs-footer border-t border-slate-800/80 bg-[#070b14] py-6 px-4 text-center text-sm text-slate-500 font-mono">
        <div className="mx-auto max-w-7xl flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-slate-400">CodeShift Infrastructure Engine</span>
            <span>&bull;</span>
            <span>v1.0.0</span>
          </div>
          <div>Non-destructive twin rehearsal &bull; IBM watsonx.ai runtime engine</div>
        </div>
      </footer>
    </div>
  )
}

export default App
