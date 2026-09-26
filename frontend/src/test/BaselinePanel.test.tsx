/**
 * Tests for BaselinePanel component with status distinctions.
 */
import { render, screen } from '@testing-library/react'
import { BaselinePanel } from '../components/BaselinePanel'
import type { BaselineResult } from '../types'

describe('BaselinePanel', () => {
  it('renders Passed badge when baseline status is PASS', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'test-1',
      status: 'PASS',
      passed: true,
      install: {
        step: 'install',
        command: 'yarn install',
        exit_code: 0,
        stdout: '',
        stderr: '',
        status: 'PASSED',
      },
      test: {
        step: 'test',
        command: 'yarn run test',
        exit_code: 0,
        stdout: '',
        stderr: '',
        status: 'PASSED',
      },
    }

    render(<BaselinePanel baseline={baseline} />)
    expect(screen.getByText('Passed')).toBeInTheDocument()
    expect(screen.getByTestId('step-install')).toBeInTheDocument()
    expect(screen.getByTestId('step-test')).toBeInTheDocument()
  })

  it('renders Failed badge when baseline fails', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'test-2',
      status: 'FAIL',
      passed: false,
      install: {
        step: 'install',
        command: 'npm install',
        exit_code: 0,
        stdout: '',
        stderr: '',
        status: 'PASSED',
      },
      test: {
        step: 'test',
        command: 'npm run test',
        exit_code: 1,
        stdout: '',
        stderr: 'Tests failed',
        status: 'FAILED',
      },
    }

    render(<BaselinePanel baseline={baseline} />)
    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText('FAILED')).toBeInTheDocument()
  })

  it('renders Environment Unavailable badge and status when package manager is unavailable', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'test-3',
      status: 'ENVIRONMENT_UNAVAILABLE',
      passed: false,
      install: {
        step: 'install',
        command: 'bun install',
        exit_code: -1,
        stdout: '',
        stderr: "Package manager 'bun' is not installed on PATH.",
        status: 'ENVIRONMENT_UNAVAILABLE',
      },
    }

    render(<BaselinePanel baseline={baseline} />)
    expect(screen.getByText('Environment Unavailable')).toBeInTheDocument()
    expect(screen.getByText('UNAVAILABLE')).toBeInTheDocument()
  })

  it('renders NOT APPLICABLE status for steps without scripts', () => {
    const baseline: BaselineResult = {
      rehearsal_id: 'test-4',
      status: 'PASS',
      passed: true,
      install: {
        step: 'install',
        command: 'pnpm install',
        exit_code: 0,
        stdout: '',
        stderr: '',
        status: 'PASSED',
      },
      lint: {
        step: 'lint',
        command: 'pnpm run lint',
        exit_code: 0,
        stdout: '',
        stderr: "No 'lint' script found in package.json.",
        status: 'SKIPPED_NOT_APPLICABLE',
      },
    }

    render(<BaselinePanel baseline={baseline} />)
    expect(screen.getByText('Passed')).toBeInTheDocument()
    expect(screen.getByText('NOT APPLICABLE')).toBeInTheDocument()
  })
})
