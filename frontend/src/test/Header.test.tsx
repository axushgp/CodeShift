/**
 * Smoke test — Header component.
 */
import { render, screen } from '@testing-library/react'
import { Header } from '../components/Header'

describe('Header', () => {
  it('renders the CodeShift title', () => {
    render(<Header />)
    expect(screen.getByText('CodeShift')).toBeInTheDocument()
  })

  it('renders an optional subtitle', () => {
    render(<Header subtitle="Migration Rehearsal System" />)
    expect(screen.getByText('Migration Rehearsal System')).toBeInTheDocument()
  })

  it('does not render subtitle element when not provided', () => {
    render(<Header />)
    expect(screen.queryByText(/rehearsal/i)).not.toBeInTheDocument()
  })
})
