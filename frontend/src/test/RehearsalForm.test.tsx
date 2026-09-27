/**
 * Tests for the RehearsalForm component.
 */
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { RehearsalForm, type RehearsalFormValues } from '../components/RehearsalForm'
import * as client from '../api/client'

vi.mock('../api/client', async () => {
  const actual = await vi.importActual('../api/client')
  return {
    ...actual,
    discoverTargetsFromUrl: vi.fn(),
    discoverTargetsFromZip: vi.fn(),
  }
})

describe('RehearsalForm', () => {
  it('renders all required inputs', () => {
    render(<RehearsalForm onSubmit={vi.fn()} />)
    expect(screen.getByTestId('input-repo-url')).toBeInTheDocument()
    expect(screen.getByTestId('input-target-package')).toBeInTheDocument()
    expect(screen.getByTestId('input-target-version')).toBeInTheDocument()
    expect(screen.getByTestId('btn-start-rehearsal')).toBeInTheDocument()
    expect(screen.getByTestId('btn-scan-repo')).toBeInTheDocument()
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
    expect(screen.getByTestId('btn-scan-repo')).toBeDisabled()
  })

  it('scans repository, displays detected stack, and allows click-to-select target', async () => {
    const mockDiscovery = {
      discovery_id: 'disc-1234',
      detected_framework: {
        id: 'react',
        name: 'React',
        package: 'react',
      },
      detected_version: '17.0.2',
      tooling: {
        build_tool: 'Vite',
        runtime: 'Node.js',
        package_manager: 'npm',
      },
      upgrade_target: {
        current: '17.0.2',
        recommended_target: '18.0.0',
        has_certified_recipe: true,
        options: [
          {
            target_version: '18.0.0',
            label: 'React 18.x',
            badge: 'Recommended',
            is_recommended: true,
            has_certified_recipe: true,
            recipe: 'react_17_to_18',
            description: 'Major upgrade to React 18',
          },
          {
            target_version: '17.0.2',
            label: 'React 17.0.2',
            badge: 'Latest Patch',
            is_recommended: false,
            has_certified_recipe: false,
            recipe: null,
            description: 'Latest patch',
          },
        ],
      },
      knowledge_updated: '2026-09',
    }

    vi.mocked(client.discoverTargetsFromUrl).mockResolvedValueOnce(mockDiscovery)

    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(<RehearsalForm onSubmit={onSubmit} />)

    await user.type(
      screen.getByTestId('input-repo-url'),
      'https://github.com/facebook/create-react-app'
    )
    await user.click(screen.getByTestId('btn-scan-repo'))

    await waitFor(() => {
      expect(screen.getByTestId('discovery-section')).toBeInTheDocument()
    })

    expect(screen.getByText('Detected Stack')).toBeInTheDocument()
    expect(screen.getAllByText(/React 17\.0\.2/).length).toBeGreaterThan(0)
    expect(screen.getByText('Vite')).toBeInTheDocument()
    expect(screen.getByText('React 18.x')).toBeInTheDocument()
    expect(screen.getByText('Recommended')).toBeInTheDocument()

    // Click start rehearsal without typing any package/version manually
    await user.click(screen.getByTestId('btn-start-rehearsal'))

    expect(onSubmit).toHaveBeenCalledOnce()
    const submitted = onSubmit.mock.calls[0][0] as RehearsalFormValues
    expect(submitted.repositoryUrl).toBe('https://github.com/facebook/create-react-app')
    expect(submitted.targetPackage).toBe('react')
    expect(submitted.targetVersion).toBe('18.0.0')
    expect(submitted.discoveryId).toBe('disc-1234')
  })
})
