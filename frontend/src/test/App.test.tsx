/**
 * App smoke tests — top-level application shell.
 */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'

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

    // Form should be disabled while running
    expect(screen.getByTestId('btn-start-rehearsal')).toBeDisabled()

    // Status panel should appear
    expect(screen.getByTestId('status-panel')).toBeInTheDocument()
    expect(screen.getByTestId('status-stage')).toHaveTextContent('Scanning repository')
  })
})
