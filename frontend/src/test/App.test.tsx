/**
 * App smoke tests — top-level application shell.
 */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import App from '../App'

// Mock the API client so tests don't make real network calls.
vi.mock('../api/client', () => ({
  ApiClientError: class ApiClientError extends Error {
    constructor(public status: number, public body: unknown, message: string) {
      super(message)
      this.name = 'ApiClientError'
    }
  },
  startRehearsalFromUrl: vi.fn().mockResolvedValue({
    rehearsal: {
      id: 'test-id',
      status: 'RUNNING',
      stage: 'SCANNING',
      repository: { url: 'https://github.com/example/app', is_demo: false },
      target_upgrade: { package: 'react', to_version: '18' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    repo_profile: null,
    baseline: null,
  }),
  startRehearsalFromZip: vi.fn(),
  getRehearsalStatus: vi.fn().mockResolvedValue({
    rehearsal: {
      id: 'test-id',
      status: 'COMPLETE',
      stage: 'COMPLETE',
      repository: { url: 'https://github.com/example/app', is_demo: false },
      target_upgrade: { package: 'react', to_version: '18' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    repo_profile: null,
    baseline: null,
  }),
  listDemos: vi.fn().mockResolvedValue([
    {
      id: 'howtotax',
      name: 'HowToTax',
      repository_url: 'https://github.com/taepras/howtotax',
      description: 'Thai personal income tax calculation web application built with React 17',
      package: 'react',
      source_version: '17.0.2',
      target_version: '18.0.0',
    },
    {
      id: 'cocos-can-i-use-npm',
      name: 'Cocos Can I Use npm',
      repository_url: 'https://github.com/cocos/cocos-can-i-use-npm',
      description: 'Cocos Creator npm package compatibility checker built with React 17',
      package: 'react',
      source_version: '17.0.2',
      target_version: '18.0.0',
    },
    {
      id: 'observablehq-plot-cra-example',
      name: 'Observable Plot CRA Example',
      repository_url: 'https://github.com/observablehq/plot-create-react-app-example',
      description: 'Observable Plot React integration example application using React 17',
      package: 'react',
      source_version: '17.0.2',
      target_version: '18.0.0',
    },
  ]),
  launchDemo: vi.fn().mockResolvedValue({
    rehearsal: {
      id: 'demo-rehearsal-id',
      status: 'RUNNING',
      stage: 'SCANNING',
      repository: { url: 'https://github.com/taepras/howtotax', is_demo: true },
      target_upgrade: { package: 'react', from_version: '17.0.2', to_version: '18.0.0' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    repo_profile: null,
    baseline: null,
  }),
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('app-root')).toBeInTheDocument()
  })

  it('renders the CodeShift header', () => {
    render(<App />)
    expect(screen.getByText('CodeShift')).toBeInTheDocument()
  })

  it('renders the rehearsal form in initial state', () => {
    render(<App />)
    expect(screen.getByTestId('rehearsal-form')).toBeInTheDocument()
    expect(screen.getByTestId('btn-start-rehearsal')).not.toBeDisabled()
  })

  it('shows results area in initial state', () => {
    render(<App />)
    expect(screen.getByTestId('results-empty')).toBeInTheDocument()
  })

  it('disables form and shows status panel after submission', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.type(
      screen.getByTestId('input-repo-url'),
      'https://github.com/example/app'
    )
    await user.type(screen.getByTestId('input-target-package'), 'react')
    await user.type(screen.getByTestId('input-target-version'), '18')
    await user.click(screen.getByTestId('btn-start-rehearsal'))

    // Wait for the async submit handler to fire and set loading state.
    await waitFor(() =>
      expect(screen.getByTestId('btn-start-rehearsal')).toBeDisabled()
    )

    // Status panel should appear
    expect(screen.getByTestId('status-panel')).toBeInTheDocument()
  })
})
