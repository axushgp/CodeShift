/**
 * AgentPackPanel — provides action controls to copy the implementation prompt
 * and download the generated Agent Pack archive.
 */

import { useState } from 'react'
import { getAgentPackDownloadUrl, getImplementationPrompt } from '../api/client'
import type { AgentTaskSpec } from '../types'

interface AgentPackPanelProps {
  rehearsalId: string
  agentTaskSpec?: AgentTaskSpec | null
  hasAgentPack: boolean
}

export function AgentPackPanel({
  rehearsalId,
  agentTaskSpec,
  hasAgentPack,
}: AgentPackPanelProps) {
  const [copied, setCopied] = useState(false)
  const [copyError, setCopyError] = useState<string | null>(null)
  const [isCopying, setIsCopying] = useState(false)

  async function handleCopyPrompt() {
    setIsCopying(true)
    setCopyError(null)
    try {
      const res = await getImplementationPrompt(rehearsalId)
      if (res.prompt) {
        await navigator.clipboard.writeText(res.prompt)
        setCopied(true)
        setTimeout(() => setCopied(false), 2500)
      } else {
        setCopyError('Implementation prompt is empty.')
      }
    } catch (err) {
      console.error('Failed to copy prompt:', err)
      setCopyError('Could not retrieve prompt from server.')
    } finally {
      setIsCopying(false)
    }
  }

  const downloadUrl = getAgentPackDownloadUrl(rehearsalId)

  return (
    <div className="cs-panel cs-agent-pack" data-testid="agent-pack-panel">
      <div className="cs-panel__header-row">
        <h2 className="cs-panel__title">Agent Pack Handoff</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          {hasAgentPack && <span className="cs-badge cs-badge--info">Pack Ready</span>}
          {agentTaskSpec?.task.status && (
            <span
              className={`cs-badge ${
                agentTaskSpec.task.status === 'VERIFIED'
                  ? 'cs-badge--success'
                  : 'cs-badge--warning'
              }`}
            >
              {agentTaskSpec.task.status}
            </span>
          )}
        </div>
      </div>

      <p className="cs-agent-pack__desc">
        CodeShift has completed the migration rehearsal. You can copy the verified
        implementation prompt directly to your autonomous coding agent (Claude Code, Cursor, Copilot, etc.)
        or download the complete machine-readable handoff package.
      </p>

      {agentTaskSpec && (
        <div className="cs-agent-pack__spec-summary">
          <dl className="cs-profile__grid">
            <dt className="cs-profile__label">Target Upgrade</dt>
            <dd className="cs-profile__value">
              {agentTaskSpec.task.package} {agentTaskSpec.task.from_version ?? ''} &rarr;{' '}
              {agentTaskSpec.task.to_version}
            </dd>

            <dt className="cs-profile__label">Files to Modify</dt>
            <dd className="cs-profile__value">
              {agentTaskSpec.files_to_modify.length > 0
                ? agentTaskSpec.files_to_modify.join(', ')
                : 'None identified'}
            </dd>

            <dt className="cs-profile__label">Rehearsal Regressions</dt>
            <dd className="cs-profile__value">
              {agentTaskSpec.verification.regressions_count} detected
            </dd>
          </dl>
        </div>
      )}

      <div className="cs-agent-pack__actions">
        <button
          type="button"
          className="cs-btn cs-btn--primary"
          onClick={handleCopyPrompt}
          disabled={isCopying}
          data-testid="btn-copy-prompt"
        >
          {copied ? 'Prompt Copied!' : isCopying ? 'Copying...' : 'Copy Implementation Prompt'}
        </button>

        <a
          href={downloadUrl}
          className="cs-btn cs-btn--secondary"
          download={`CodeShift-Agent-Pack-${rehearsalId.slice(0, 8)}.zip`}
          data-testid="btn-download-pack"
        >
          Download Agent Pack (.zip)
        </a>
      </div>

      {copyError && <p className="cs-form__error">{copyError}</p>}

      <div className="cs-agent-pack__contents">
        <h3 className="cs-panel__subtitle">Included Pack Artifacts</h3>
        <ul className="cs-agent-pack__file-list">
          <li><code>agent_task.json</code> &mdash; Machine-readable task spec</li>
          <li><code>implementation-prompt.md</code> &mdash; Standalone AI prompt</li>
          <li><code>AGENTS.md</code> &mdash; Behavioral instructions for coding agents</li>
          <li><code>migration-plan.md</code> &mdash; Structured plan & findings</li>
          <li><code>findings.json</code> &mdash; JSON findings with evidence</li>
          <li><code>verification.md</code> &mdash; Verification history and diff report</li>
          <li><code>patch.diff</code> &mdash; Unified diff rehearsed in Twin</li>
          <li><code>README.md</code> &mdash; Package documentation</li>
        </ul>
      </div>
    </div>
  )
}
