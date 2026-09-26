/**
 * AgentPackPanel — Agent-ready implementation handoff package.
 * Displays file package explorer, copy prompt, and download actions.
 */

import { useState } from 'react'
import {
  Copy,
  Check,
  Download,
  FileCode,
  FileText,
  Bot,
  ListOrdered,
  ShieldCheck,
  Loader2,
} from 'lucide-react'
import { getAgentPackDownloadUrl, getImplementationPrompt } from '../api/client'
import type { AgentTaskSpec } from '../types'

interface AgentPackPanelProps {
  rehearsalId: string
  agentTaskSpec?: AgentTaskSpec | null
  hasAgentPack: boolean
}

const PACK_FILES = [
  { name: 'agent_task.json', desc: 'Structured machine-readable task specification', icon: FileCode },
  { name: 'implementation-prompt.md', desc: 'Curated prompt for Claude Code, Cursor, Copilot', icon: FileText },
  { name: 'AGENTS.md', desc: 'Repository behavioral instructions and constraints', icon: Bot },
  { name: 'migration-plan.md', desc: 'Chronological step-by-step migration guide', icon: ListOrdered },
  { name: 'findings.json', desc: 'Full migration findings and AST evidence', icon: FileCode },
  { name: 'verification.md', desc: 'Pre- & post-migration command execution logs', icon: ShieldCheck },
  { name: 'patch.diff', desc: 'Deterministic unified git diff patch', icon: FileText },
  { name: 'README.md', desc: 'Agent pack overview and verification report', icon: FileText },
]

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
    <div className="space-y-4" data-testid="agent-pack-panel">
      {/* ── Header & Action Controls ────────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <Bot className="h-4 w-4 text-zinc-400" />
              <h3 className="text-base font-semibold text-white">
                Agent Pack Handoff
              </h3>
              <div className="flex items-center space-x-2 text-sm font-mono">
                {hasAgentPack && (
                  <span className="text-zinc-400">
                    <span>Pack Ready</span>
                  </span>
                )}
                {agentTaskSpec?.task.status && (
                  <span
                    className={`font-semibold inline-flex items-center space-x-1 ${
                      agentTaskSpec.task.status === 'VERIFIED'
                        ? 'text-emerald-400'
                        : 'text-amber-400'
                    }`}
                  >
                    <span>●</span>
                    <span>{agentTaskSpec.task.status}</span>
                  </span>
                )}
              </div>
            </div>
            <p className="mt-1 text-sm text-zinc-400">
              Agent-ready implementation package to delegate safe production migration to Claude Code, Cursor, Copilot
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleCopyPrompt}
              disabled={isCopying}
              data-testid="btn-copy-prompt"
              className="inline-flex items-center space-x-1.5 rounded border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-semibold text-zinc-200 transition hover:bg-zinc-700 hover:text-white disabled:opacity-50"
            >
              {isCopying ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : copied ? (
                <Check className="h-4 w-4 text-emerald-400" />
              ) : (
                <Copy className="h-4 w-4 text-zinc-400" />
              )}
              <span>{copied ? 'Prompt Copied!' : 'Copy Implementation Prompt'}</span>
            </button>

            {hasAgentPack && (
              <a
                href={downloadUrl}
                download
                data-testid="btn-download-pack"
                className="inline-flex items-center space-x-1.5 rounded bg-white px-4 py-2 text-sm font-semibold text-black transition hover:bg-zinc-200"
              >
                <Download className="h-4 w-4" />
                <span>Download Agent Pack (.zip)</span>
              </a>
            )}
          </div>
        </div>

        {copyError && (
          <p className="mt-3 text-sm text-red-400 font-mono bg-zinc-900 p-2.5 rounded border border-zinc-800">
            {copyError}
          </p>
        )}

        {/* Spec Overview Grid */}
        {agentTaskSpec && (
          <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3 text-sm font-mono">
            <div className="rounded border border-zinc-800 bg-zinc-900/50 p-3.5">
              <span className="text-xs text-zinc-500 uppercase tracking-wider block">Target Upgrade</span>
              <span className="text-zinc-200 font-semibold mt-0.5 block">
                {agentTaskSpec.task.package} {agentTaskSpec.task.from_version ?? ''} &rarr; {agentTaskSpec.task.to_version}
              </span>
            </div>

            <div className="rounded border border-zinc-800 bg-zinc-900/50 p-3.5">
              <span className="text-xs text-zinc-500 uppercase tracking-wider block">Files To Modify</span>
              <span className="text-zinc-200 font-semibold mt-0.5 block truncate">
                {agentTaskSpec.files_to_modify.length > 0
                  ? `${agentTaskSpec.files_to_modify.length} file(s)`
                  : 'None identified'}
              </span>
            </div>

            <div className="rounded border border-zinc-800 bg-zinc-900/50 p-3.5">
              <span className="text-xs text-zinc-500 uppercase tracking-wider block">Regressions Count</span>
              <span
                className={`font-semibold mt-0.5 block ${
                  agentTaskSpec.verification.regressions_count === 0 ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {agentTaskSpec.verification.regressions_count} detected
              </span>
            </div>
          </div>
        )}
      </div>

      {/* ── 8 Generated Files Explorer ────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-300">
          Generated Agent Pack Files (8 Artifacts)
        </h4>

        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
          {PACK_FILES.map((f) => {
            const Icon = f.icon
            return (
              <div
                key={f.name}
                className="flex items-start space-x-3 rounded border border-zinc-800 bg-zinc-900/30 p-3 transition hover:border-zinc-700 hover:bg-zinc-900/60"
              >
                <div className="rounded border border-zinc-800 bg-zinc-900 p-2 text-zinc-400 shrink-0">
                  <Icon className="h-4 w-4" />
                </div>
                <div className="truncate">
                  <span className="text-sm font-semibold font-mono text-zinc-200 block truncate">
                    {f.name}
                  </span>
                  <span className="text-xs text-zinc-500 block truncate mt-0.5">
                    {f.desc}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Implementation Steps & Acceptance Criteria ────────────────────── */}
      {agentTaskSpec && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Steps */}
          {agentTaskSpec.implementation_plan && agentTaskSpec.implementation_plan.length > 0 && (
            <div className="rounded border border-zinc-800 bg-[#121214] p-5 text-sm font-mono">
              <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-300 flex items-center space-x-2">
                <ListOrdered className="h-4 w-4 text-zinc-400" />
                <span>Implementation Steps ({agentTaskSpec.implementation_plan.length})</span>
              </h4>
              <ol className="space-y-2.5">
                {agentTaskSpec.implementation_plan.map((step) => (
                  <li
                    key={step.step_number}
                    className="rounded border border-zinc-800 bg-zinc-900/40 p-3"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-zinc-200">Step {step.step_number}</span>
                      <span className="text-xs font-mono text-zinc-500 uppercase">
                        [{step.action_type}]
                      </span>
                    </div>
                    <p className="text-zinc-300 font-sans text-sm">{step.description}</p>
                    {step.target_files && step.target_files.length > 0 && (
                      <span className="text-zinc-500 text-xs mt-1 block truncate">
                        Target: {step.target_files.join(', ')}
                      </span>
                    )}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Acceptance Criteria & Constraints */}
          <div className="space-y-4">
            {agentTaskSpec.acceptance_criteria && agentTaskSpec.acceptance_criteria.length > 0 && (
              <div className="rounded border border-zinc-800 bg-[#121214] p-5 text-sm">
                <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-300 flex items-center space-x-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  <span>Acceptance Criteria</span>
                </h4>
                <ul className="space-y-2 font-mono text-zinc-300">
                  {agentTaskSpec.acceptance_criteria.map((c, idx) => (
                    <li key={idx} className="flex items-center space-x-2">
                      <Check className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {agentTaskSpec.constraints && agentTaskSpec.constraints.length > 0 && (
              <div className="rounded border border-zinc-800 bg-[#121214] p-5 text-sm">
                <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-300">
                  Agent Constraints
                </h4>
                <ul className="space-y-1.5 font-mono text-zinc-400 list-disc list-inside">
                  {agentTaskSpec.constraints.map((c, idx) => (
                    <li key={idx}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
