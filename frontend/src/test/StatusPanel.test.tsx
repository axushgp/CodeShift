/**
 * Tests for the StatusPanel component.
 */
import { render, screen } from '@testing-library/react'
import { StatusPanel } from '../components/StatusPanel'

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
})
