/**
 * Main App component — CodeShift application shell.
 *
 * Wires the RehearsalForm to the backend API:
 * 1. Submit → POST /api/rehearsals (URL) or POST /api/rehearsals/upload (ZIP)
 * 2. Poll GET /api/rehearsals/{id} until terminal stage
 * 3. Display profile + baseline results
 */

import { useEffect, useRef, useState } from 'react'
import { Header } from './components/Header'
import { RehearsalForm, type RehearsalFormValues } from './components/RehearsalForm'
import { StatusPanel } from './components/StatusPanel'
import { ResultsArea } from './components/ResultsArea'
import { RepoProfilePanel } from './components/RepoProfilePanel'
import { BaselinePanel } from './components/BaselinePanel'
import { FindingsPanel } from './components/FindingsPanel'
import { VerificationPanel } from './components/VerificationPanel'
import { AgentPackPanel } from './components/AgentPackPanel'
import {
  ApiClientError,
  getRehearsalStatus,
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
    setState({ ...INITIAL_STATE, isLoading: true })

    try {
      let data
      if (values.mode === 'url') {
        data = await startRehearsalFromUrl({
          repository_url: values.repositoryUrl,
          target_package: values.targetPackage,
          target_version: values.targetVersion,
        })
      } else {
        if (!values.zipFile) return
        data = await startRehearsalFromZip(
          values.zipFile,
          values.targetPackage,
          values.targetVersion,
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
        isLoading: true,
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

  const currentStage: RehearsalStage = state.rehearsal?.stage ?? 'INTAKE'
  const currentStatus: RehearsalStatus = state.rehearsal?.status ?? (state.isLoading ? 'RUNNING' : 'PENDING')
  const showStatus = state.rehearsal != null || state.errorMessage != null || state.isLoading

  return (
    <div className="cs-app" data-testid="app-root">
      <Header subtitle="Repository Migration Rehearsal System" />

      <main className="cs-main">
        <section className="cs-section" aria-label="Start a rehearsal">
          <RehearsalForm
            onSubmit={handleStartRehearsal}
            disabled={state.isLoading}
          />
        </section>

        {showStatus && (
          <section className="cs-section" aria-label="Rehearsal status">
            <StatusPanel
              stage={currentStage}
              status={currentStatus}
              errorMessage={state.errorMessage ?? undefined}
            />
          </section>
        )}

        {state.profile && (
          <section className="cs-section" aria-label="Repository profile">
            <RepoProfilePanel profile={state.profile} />
          </section>
        )}

        {state.baseline && (
          <section className="cs-section" aria-label="Baseline results">
            <BaselinePanel baseline={state.baseline} />
          </section>
        )}

        {state.migrationPlan && state.migrationPlan.findings && state.migrationPlan.findings.length > 0 && (
          <section className="cs-section" aria-label="Migration findings">
            <FindingsPanel findings={state.migrationPlan.findings} />
          </section>
        )}

        {(state.verificationRun || state.twinResult) && (
          <section className="cs-section" aria-label="Verification and Twin results">
            <VerificationPanel
              verificationRun={state.verificationRun}
              twinResult={state.twinResult}
            />
          </section>
        )}

        {state.rehearsal && (state.agentTaskSpec || state.hasAgentPack || TERMINAL_STAGES.includes(currentStage)) && (
          <section className="cs-section" aria-label="Agent Pack and handoff">
            <AgentPackPanel
              rehearsalId={state.rehearsal.id}
              agentTaskSpec={state.agentTaskSpec}
              hasAgentPack={state.hasAgentPack}
            />
          </section>
        )}

        {!state.profile && !state.isLoading && (
          <section className="cs-section" aria-label="Results">
            <ResultsArea isLoading={false} />
          </section>
        )}
      </main>

      <footer className="cs-footer">
        <p>CodeShift — Migration Rehearsal System</p>
      </footer>
    </div>
  )
}

export default App
