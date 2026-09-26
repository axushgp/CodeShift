/**
 * MigrationPlanPanel — displays planned and executed migration actions.
 * Clearly distinguishes APPLIED, PROPOSED, REQUIRES REVIEW, and SKIPPED.
 */

import { useState } from 'react'
import {
  ListChecks,
  FileCode,
  Terminal,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import type { MigrationPlan, PlannedAction, TwinResult } from '../types'

interface MigrationPlanPanelProps {
  plan?: MigrationPlan | null
  twinResult?: TwinResult | null
}

export function MigrationPlanPanel({ plan, twinResult }: MigrationPlanPanelProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  if (!plan || !plan.planned_actions || plan.planned_actions.length === 0) {
    return (
      <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center" data-testid="plan-empty">
        <ListChecks className="mx-auto h-7 w-7 text-zinc-500" />
        <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">No Planned Actions</h3>
        <p className="mt-1 text-xs text-zinc-500 font-mono">
          Migration plan has not been generated or contains zero action items.
        </p>
      </div>
    )
  }

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const getActionStatus = (action: PlannedAction) => {
    if (!twinResult) {
      return { label: 'PROPOSED', color: 'text-blue-400' }
    }
    if (twinResult.actions_applied?.includes(action.id)) {
      return { label: 'APPLIED', color: 'text-emerald-400' }
    }
    if (twinResult.actions_skipped?.includes(action.id)) {
      return { label: 'SKIPPED', color: 'text-zinc-500' }
    }
    if (twinResult.manual_items?.includes(action.id) || plan.requires_human_review) {
      return { label: 'REVIEW', color: 'text-amber-400' }
    }
    return { label: 'PROPOSED', color: 'text-blue-400' }
  }

  return (
    <div className="space-y-4" data-testid="migration-plan-panel">
      {/* ── Summary Bar ────────────────────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <ListChecks className="h-4 w-4 text-zinc-400" />
              <h3 className="text-base font-semibold text-white">
                Migration Plan ({plan.planned_actions.length} Actions)
              </h3>
              <span className="text-sm font-mono text-zinc-400">
                ({plan.package} &bull; {plan.to_version})
              </span>
            </div>
            <p className="mt-1 text-sm text-zinc-400">
              Ordered automated codemods, package upgrades, and manual review items
            </p>
          </div>

          <div className="flex items-center space-x-3 text-sm font-mono">
            {twinResult?.actions_applied && (
              <span className="text-zinc-300">
                <span className="text-emerald-400 font-bold">●</span> {twinResult.actions_applied.length} Applied
              </span>
            )}
            {plan.requires_human_review && (
              <span className="text-zinc-300">
                <span className="text-amber-400 font-bold">●</span> Review Required
              </span>
            )}
          </div>
        </div>

        {plan.notes && (
          <div className="mt-3 rounded border border-zinc-800 bg-zinc-900/60 p-2.5 text-sm text-zinc-300 font-mono">
            {plan.notes}
          </div>
        )}
      </div>

      {/* ── Technical Change List ─────────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] divide-y divide-zinc-800/80 overflow-hidden">
        {plan.planned_actions.map((action, idx) => {
          const status = getActionStatus(action)
          const isExpanded = expandedIds.has(action.id)
          const stepNum = String(idx + 1).padStart(2, '0')

          return (
            <div key={action.id || idx} className="transition hover:bg-zinc-900/30">
              <div
                onClick={() => toggleExpand(action.id)}
                className="flex cursor-pointer items-center justify-between p-3.5 select-none"
              >
                <div className="flex items-center space-x-3 truncate">
                  <span className="font-mono text-sm font-semibold text-zinc-500 w-7 shrink-0">
                    {stepNum}
                  </span>

                  <span className="text-sm font-medium text-zinc-100 truncate">
                    {action.description}
                  </span>

                  <span className="text-xs font-mono text-zinc-500 uppercase shrink-0">
                    [{action.action_type.replace(/_/g, ' ')}]
                  </span>
                </div>

                <div className="flex items-center space-x-4 shrink-0 ml-3">
                  {action.target_files && action.target_files.length > 0 && (
                    <span className="hidden sm:inline-flex items-center space-x-1 text-xs font-mono text-zinc-400">
                      <FileCode className="h-3.5 w-3.5 text-zinc-500" />
                      <span className="truncate max-w-[150px]">{action.target_files[0]}</span>
                      {action.target_files.length > 1 && <span>+{action.target_files.length - 1}</span>}
                    </span>
                  )}

                  <span className={`font-mono text-sm font-semibold w-16 text-right ${status.color}`}>
                    {status.label}
                  </span>

                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-zinc-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-zinc-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="border-t border-zinc-800 bg-[#0d0d10] p-4 text-sm space-y-3.5">
                  <div>
                    <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                      Action Details
                    </h4>
                    <p className="text-zinc-300 leading-relaxed font-sans">{action.description}</p>
                  </div>

                  {action.target_files && action.target_files.length > 0 && (
                    <div>
                      <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                        Target Files
                      </h4>
                      <div className="flex flex-wrap gap-1.5 font-mono">
                        {action.target_files.map((file) => (
                          <span
                            key={file}
                            className="inline-flex items-center space-x-1 rounded bg-zinc-900 border border-zinc-800 px-2 py-0.5 text-xs text-zinc-300"
                          >
                            <FileCode className="h-3.5 w-3.5 text-zinc-500" />
                            <span>{file}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {action.command && (
                    <div>
                      <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                        Execution Command
                      </h4>
                      <div className="rounded bg-zinc-950 border border-zinc-800 p-2 font-mono text-sm text-zinc-200 flex items-center space-x-2">
                        <Terminal className="h-4 w-4 text-zinc-500" />
                        <span>{action.command}</span>
                      </div>
                    </div>
                  )}

                  {action.patch && (
                    <div>
                      <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                        Proposed Code Patch
                      </h4>
                      <pre className="rounded bg-zinc-950 p-2.5 font-mono text-xs text-zinc-300 overflow-x-auto border border-zinc-800">
                        {action.patch}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
