/**
 * Main App component — CodeShift application shell.
 *
 * Provides the top-level layout and wires together:
 * - Header
 * - RehearsalForm (input)
 * - StatusPanel (current stage)
 * - ResultsArea (findings / results)
 *
 * Real API integration is added in later sessions.
 * This session establishes the clean structure and loading/error states.
 */

import { useState } from 'react'
import { Header } from './components/Header'
import { RehearsalForm, type RehearsalFormValues } from './components/RehearsalForm'
import { StatusPanel } from './components/StatusPanel'
import { ResultsArea } from './components/ResultsArea'
import type { RehearsalStage, RehearsalStatus } from './types'
import './App.css'

interface AppState {
  stage: RehearsalStage
  status: RehearsalStatus
  errorMessage?: string
  isLoading: boolean
}

const INITIAL_STATE: AppState = {
  stage: 'INTAKE',
  status: 'PENDING',
  isLoading: false,
}

function App() {
  const [state, setState] = useState<AppState>(INITIAL_STATE)

  function handleStartRehearsal(values: RehearsalFormValues) {
    // Placeholder: in Session 2+, this calls POST /api/rehearsals
    console.info('Starting rehearsal', values)
    setState({
      stage: 'SCANNING',
      status: 'RUNNING',
      isLoading: true,
    })
  }

  const isRunning = state.status === 'RUNNING'

  return (
    <div className="cs-app" data-testid="app-root">
      <Header subtitle="Repository Migration Rehearsal System" />

      <main className="cs-main">
        <section className="cs-section" aria-label="Start a rehearsal">
          <RehearsalForm
            onSubmit={handleStartRehearsal}
            disabled={isRunning}
          />
        </section>

        {state.status !== 'PENDING' && (
          <section className="cs-section" aria-label="Rehearsal status">
            <StatusPanel
              stage={state.stage}
              status={state.status}
              errorMessage={state.errorMessage}
            />
          </section>
        )}

        <section className="cs-section" aria-label="Results">
          <ResultsArea isLoading={state.isLoading} />
        </section>
      </main>

      <footer className="cs-footer">
        <p>CodeShift — Migration Rehearsal System</p>
      </footer>
    </div>
  )
}

export default App
