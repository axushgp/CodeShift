/**
 * Tests for the RehearsalForm component.
 */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RehearsalForm, type RehearsalFormValues } from '../components/RehearsalForm'

describe('RehearsalForm', () => {
  it('renders all required inputs', () => {
    render(<RehearsalForm onSubmit={vi.fn()} />)
    expect(screen.getByTestId('input-repo-url')).toBeInTheDocument()
    expect(screen.getByTestId('input-target-package')).toBeInTheDocument()
    expect(screen.getByTestId('input-target-version')).toBeInTheDocument()
    expect(screen.getByTestId('btn-start-rehearsal')).toBeInTheDocument()
  })

  it('calls onSubmit with form values when submitted', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(<RehearsalForm onSubmit={onSubmit} />)

    await user.type(
      screen.getByTestId('input-repo-url'),
      'https://github.com/example/app'
    )
    await user.type(screen.getByTestId('input-target-package'), 'react')
    await user.type(screen.getByTestId('input-target-version'), '18')
    await user.click(screen.getByTestId('btn-start-rehearsal'))

    expect(onSubmit).toHaveBeenCalledOnce()
    const submitted = onSubmit.mock.calls[0][0] as RehearsalFormValues
    expect(submitted.repositoryUrl).toBe('https://github.com/example/app')
    expect(submitted.targetPackage).toBe('react')
    expect(submitted.targetVersion).toBe('18')
  })

  it('disables all inputs and button when disabled=true', () => {
    render(<RehearsalForm onSubmit={vi.fn()} disabled />)
    expect(screen.getByTestId('input-repo-url')).toBeDisabled()
    expect(screen.getByTestId('input-target-package')).toBeDisabled()
    expect(screen.getByTestId('input-target-version')).toBeDisabled()
    expect(screen.getByTestId('btn-start-rehearsal')).toBeDisabled()
  })
})
