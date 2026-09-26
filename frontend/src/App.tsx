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
import {
  ApiClientError,
  getRehearsalStatus,
  startRehearsalFromUrl,
  startRehearsalFromZip,
} from './api/client'
import type {
  BaselineResult,
  Rehearsal,
  RehearsalStage,
  RehearsalStatus,
  RepositoryProfile,
} from './types'
import './App.css'

const TERMINAL_STAGES: RehearsalStage[] = ['COMPLETE', 'FAILED', 'REQUIRES_HUMAN_REVIEW']
const POLL_INTERVAL_MS = 2000

interface AppState {
  rehearsal: Rehearsal | null
  profile: RepositoryProfile | null
  baseline: BaselineResult | null
  errorMessage: string | null
  isLoading: boolean
}

const INITIAL_STATE: AppState = {
  rehearsal: null,
  profile: null,
  baseline: null,
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
