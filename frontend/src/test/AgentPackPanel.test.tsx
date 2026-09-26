/**
 * Tests for AgentPackPanel — verifies handoff buttons and artifacts listing.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { AgentPackPanel } from '../components/AgentPackPanel'
import type { AgentTaskSpec } from '../types'

vi.mock('../api/client', () => ({
  getImplementationPrompt: vi.fn().mockResolvedValue({
    prompt: '# Implementation Prompt\nMigrate React 17 to React 18.',
  }),
  getAgentPackDownloadUrl: vi.fn(
    (id: string) => `/api/rehearsals/${id}/agent-pack/download`
  ),
}))

const mockTaskSpec: AgentTaskSpec = {
  rehearsal_id: 'rehearsal-123',
  task: {
    package: 'react',
    from_version: '17.0.2',
    to_version: '18.2.0',
    status: 'VERIFIED',
    summary: 'Upgrade React',
  },
  repository: {
    source: 'local',
    name: 'test-app',
    ecosystem: 'javascript',
    primary_language: 'typescript',
  },
  findings: [],
  implementation_plan: [],
  constraints: [],
  files_to_modify: ['src/index.tsx'],
  files_not_to_modify: [],
  verification: {
    baseline_passed: true,
    final_verification_passed: true,
    regressions_count: 0,
    status: 'PASSED',
    details: [],
  },
  acceptance_criteria: ['All tests pass'],
}

describe('AgentPackPanel', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  it('renders copy prompt button and download pack link', () => {
    render(
      <AgentPackPanel
        rehearsalId="rehearsal-123"
        agentTaskSpec={mockTaskSpec}
        hasAgentPack={true}
      />
    )

    expect(screen.getByTestId('agent-pack-panel')).toBeInTheDocument()
    expect(screen.getByTestId('btn-copy-prompt')).toBeInTheDocument()
    expect(screen.getByTestId('btn-download-pack')).toBeInTheDocument()
    expect(screen.getByText('Pack Ready')).toBeInTheDocument()
    expect(screen.getByText('VERIFIED')).toBeInTheDocument()
  })

  it('copies implementation prompt when copy button is clicked', async () => {
    render(
      <AgentPackPanel
        rehearsalId="rehearsal-123"
        agentTaskSpec={mockTaskSpec}
        hasAgentPack={true}
      />
    )

    const copyBtn = screen.getByTestId('btn-copy-prompt')
    fireEvent.click(copyBtn)

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining('Migrate React 17 to React 18')
      )
      expect(screen.getByText('Prompt Copied!')).toBeInTheDocument()
    })
  })
})
