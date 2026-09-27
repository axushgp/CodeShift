/**
 * Tests for the StatusPanel component.
 */
import { render, screen, within } from '@testing-library/react'
import { StatusPanel } from '../components/StatusPanel'
import type { BaselineResult } from '../types'

describe('StatusPanel', () => {
  it('renders the current stage label', () => {
    render(<StatusPanel stage="SCANNING" status="RUNNING" />)
    expect(screen.getByTestId('status-stage')).toHaveTextContent('Scanning repository')
  })

  it('renders an error message when provided', () => {
    render(
      <StatusPanel stage="FAILED" status="FAILED" errorMessage="Something went wrong" />
    )
    expect(screen.getByTestId('status-error')).toHaveTextContent('Something went wrong')
  })

  it('does not render error element when no errorMessage', () => {
    render(<StatusPanel stage="VERIFYING" status="RUNNING" />)
    expect(screen.queryByTestId('status-error')).not.toBeInTheDocument()
  })

  it('renders COMPLETE status correctly', () => {
    render(<StatusPanel stage="COMPLETE" status="COMPLETE" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Complete')
  })

  it('renders active operation and baseline sequence when baselining', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'reh-1',
      active_step: 'build',
      active_operation: 'Building with react-scripts...',
      active_timeout: 300,
      active_started_at: Math.floor(Date.now() / 1000) - 10,
      install: {
        step: 'install',
        command: 'yarn install',
        exit_code: 0,
        stdout: '',
        stderr: '',
        duration_seconds: 24,
        status: 'PASSED',
      },
      passed: false,
    }

    render(
      <StatusPanel
        stage="BASELINING"
        status="RUNNING"
        activeOperation="Building with react-scripts..."
        baseline={baseline}
      />
    )

    expect(screen.getByTestId('status-stage')).toHaveTextContent('Building with react-scripts...')
    const sequence = screen.getByTestId('baseline-sequence')
    expect(sequence).toBeInTheDocument()
    expect(within(sequence).getByText('Build')).toBeInTheDocument()
    expect(within(sequence).getByText('Install')).toBeInTheDocument()
    expect(screen.getByTestId('status-elapsed')).toHaveTextContent('Elapsed: 00:10')
  })

  it('displays soft waiting message and rotating facts after 10 seconds for any running process', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'reh-2',
      active_step: 'install',
      active_operation: 'Installing dependencies with Yarn...',
      active_timeout: 300,
      active_started_at: Math.floor(Date.now() / 1000) - 12, // 12 seconds elapsed (>= 10s)
      passed: false,
    }

    render(
      <StatusPanel
        stage="BASELINING"
        status="RUNNING"
        activeOperation="Installing dependencies with Yarn..."
        baseline={baseline}
      />
    )

    expect(screen.getByTestId('waiting-panel')).toBeInTheDocument()
    expect(screen.getByText('Still working')).toBeInTheDocument()
    expect(screen.getByText(/cold dependency\/build environment/)).toBeInTheDocument()
    expect(screen.getByTestId('rotating-facts-panel')).toBeInTheDocument()
    expect(screen.getByTestId('rotating-category-badge')).toHaveTextContent(/WHY CODESHIFT|WHILE YOU WAIT/)
    expect(screen.getByTestId('rotating-progress-bar')).toBeInTheDocument()
  })

  it('does not display waiting quotes when process has run for less than 10 seconds', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'reh-2b',
      active_step: 'install',
      active_operation: 'Installing dependencies...',
      active_timeout: 300,
      active_started_at: Math.floor(Date.now() / 1000) - 5, // 5 seconds elapsed (< 10s)
      passed: false,
    }

    render(
      <StatusPanel
        stage="BASELINING"
        status="RUNNING"
        activeOperation="Installing dependencies..."
        baseline={baseline}
      />
    )

    expect(screen.queryByTestId('waiting-panel')).not.toBeInTheDocument()
  })

  it('displays explicit TIMEOUT state when command exceeds timeout limit', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'reh-3',
      status: 'TIMEOUT',
      notes: 'Install step timed out after 300s (limit: 300s). Subsequent steps were not run.',
      install: {
        step: 'install',
        command: 'npm install',
        exit_code: -1,
        stdout: '',
        stderr: 'Command exceeded the configured timeout limit of 300s.',
        duration_seconds: 300.0,
        status: 'TIMEOUT',
      },
      passed: false,
    }

    render(
      <StatusPanel
        stage="BASELINING"
        status="FAILED"
        errorMessage="Baseline execution timed out"
        baseline={baseline}
      />
    )

    expect(screen.getByTestId('status-badge')).toHaveTextContent('Timeout')
    expect(screen.getByTestId('timeout-details')).toBeInTheDocument()
    expect(screen.getByText('TIMEOUT')).toBeInTheDocument()
    expect(screen.getByText('npm install')).toBeInTheDocument()
    expect(screen.getAllByText(/Command exceeded the configured timeout limit/).length).toBeGreaterThan(0)
  })
})
