/**
 * FindingsPanel — Interactive migration findings list with progressive disclosure.
 * Shows Level 1 summary badges, Level 2 expandable cards with rationale, evidence, and actions.
 */

import { useState, useMemo } from 'react'
import {
  CheckCircle2,
  FileCode,
  ChevronDown,
  ChevronUp,
  Search,
  Zap,
} from 'lucide-react'
import type { MigrationFinding, FindingSeverity } from '../types'

interface FindingsPanelProps {
  findings: MigrationFinding[]
  targetPackage?: string
  fromVersion?: string
  toVersion?: string
}

export function FindingsPanel({
  findings,
  targetPackage = 'react',
  fromVersion = '17.0.2',
  toVersion = '18.0.0',
}: FindingsPanelProps) {
  const [severityFilter, setSeverityFilter] = useState<'ALL' | FindingSeverity>('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
      INFO: 0,
    }
    findings.forEach((f) => {
      if (counts[f.severity] !== undefined) counts[f.severity]++
    })
    return counts
  }, [findings])

  const filteredFindings = useMemo(() => {
    return findings.filter((f) => {
      const matchSeverity = severityFilter === 'ALL' || f.severity === severityFilter
      const q = searchQuery.toLowerCase()
      const matchQuery =
        !q ||
        f.title.toLowerCase().includes(q) ||
        f.reason.toLowerCase().includes(q) ||
        f.affected_files.some((file) => file.toLowerCase().includes(q))
      return matchSeverity && matchQuery
    })
  }, [findings, severityFilter, searchQuery])

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const toggleExpandAll = () => {
    if (expandedIds.size === filteredFindings.length) {
      setExpandedIds(new Set())
    } else {
      setExpandedIds(new Set(filteredFindings.map((f) => f.id)))
    }
  }

  if (!findings || findings.length === 0) {
    return (
      <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center" data-testid="findings-panel">
        <CheckCircle2 className="mx-auto h-7 w-7 text-emerald-400" />
        <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-200">No Breaking Migration Findings</h3>
        <p className="mt-1 text-xs text-zinc-500 font-mono">
          Watsonx and migration analysis detected no mandatory code changes for this repository.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4" data-testid="findings-panel">
      {/* ── Top Summary & Filter Bar ────────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <Zap className="h-4 w-4 text-zinc-400" />
              <h3 className="text-base font-semibold text-white">
                Migration Analysis Findings ({findings.length})
              </h3>
              <span className="text-sm font-mono text-zinc-400">
                ({targetPackage} {fromVersion} &rarr; {toVersion})
              </span>
            </div>
            <p className="mt-1 text-sm text-zinc-400">
              Breaking changes, deprecated APIs, and required code modifications discovered by Watsonx
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={toggleExpandAll}
              className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm font-medium text-zinc-300 hover:bg-zinc-700 hover:text-white transition"
            >
              {expandedIds.size === filteredFindings.length ? 'Collapse All' : 'Expand All'}
            </button>
          </div>
        </div>

        {/* Severity Filter Tabs & Search */}
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1 border border-zinc-800 bg-zinc-900/60 p-1 rounded text-xs font-mono">
            <button
              type="button"
              onClick={() => setSeverityFilter('ALL')}
              className={`px-2.5 py-1 text-xs font-semibold transition ${
                severityFilter === 'ALL'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              ALL ({findings.length})
            </button>

            {severityCounts.CRITICAL > 0 && (
              <button
                type="button"
                onClick={() => setSeverityFilter('CRITICAL')}
                className={`px-2.5 py-1 text-xs font-semibold transition ${
                  severityFilter === 'CRITICAL'
                    ? 'bg-zinc-800 text-red-400'
                    : 'text-zinc-400 hover:text-red-400 hover:bg-zinc-800/50'
                }`}
              >
                CRITICAL ({severityCounts.CRITICAL})
              </button>
            )}

            {severityCounts.HIGH > 0 && (
              <button
                type="button"
                onClick={() => setSeverityFilter('HIGH')}
                className={`px-2.5 py-1 text-xs font-semibold transition ${
                  severityFilter === 'HIGH'
                    ? 'bg-zinc-800 text-amber-400'
                    : 'text-zinc-400 hover:text-amber-400 hover:bg-zinc-800/50'
                }`}
              >
                HIGH ({severityCounts.HIGH})
              </button>
            )}

            {severityCounts.MEDIUM > 0 && (
              <button
                type="button"
                onClick={() => setSeverityFilter('MEDIUM')}
                className={`px-2.5 py-1 text-xs font-semibold transition ${
                  severityFilter === 'MEDIUM'
                    ? 'bg-zinc-800 text-blue-400'
                    : 'text-zinc-400 hover:text-blue-400 hover:bg-zinc-800/50'
                }`}
              >
                MEDIUM ({severityCounts.MEDIUM})
              </button>
            )}

            {severityCounts.LOW > 0 && (
              <button
                type="button"
                onClick={() => setSeverityFilter('LOW')}
                className={`px-2.5 py-1 text-xs font-semibold transition ${
                  severityFilter === 'LOW'
                    ? 'bg-zinc-800 text-white'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
              >
                LOW ({severityCounts.LOW})
              </button>
            )}
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Search findings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 rounded border border-zinc-800 bg-zinc-900 py-1.5 pl-8 pr-2.5 text-sm text-zinc-200 placeholder-zinc-500 outline-none focus:border-zinc-600 font-mono"
            />
          </div>
        </div>
      </div>

      {/* ── Findings List ───────────────────────────────────────────────────── */}
      <div className="space-y-2">
        {filteredFindings.map((f) => {
          const isExpanded = expandedIds.has(f.id)
          const isCritical = f.severity === 'CRITICAL'
          const isHigh = f.severity === 'HIGH'
          const isMedium = f.severity === 'MEDIUM'

          const severityColor = isCritical
            ? 'text-red-400'
            : isHigh
            ? 'text-amber-400'
            : isMedium
            ? 'text-blue-400'
            : 'text-zinc-400'

          return (
            <div
              key={f.id}
              className="rounded border border-zinc-800 bg-[#121214] hover:border-zinc-700 transition"
              data-testid={`finding-${f.id}`}
            >
              {/* Header (Code review / static analysis style) */}
              <div
                onClick={() => toggleExpand(f.id)}
                className="flex cursor-pointer items-start justify-between p-3.5 select-none"
              >
                <div className="flex items-start space-x-3 truncate">
                  <span className={`font-mono text-sm font-bold tracking-wider shrink-0 w-20 pt-0.5 ${severityColor}`}>
                    {f.severity}
                  </span>

                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-semibold text-zinc-100 truncate">{f.title}</span>
                      <span className="text-xs font-mono text-zinc-500 uppercase">
                        [{f.type.replace(/_/g, ' ')}]
                      </span>
                    </div>
                    {f.affected_files && f.affected_files.length > 0 && (
                      <div className="mt-1 flex items-center space-x-1.5 text-xs font-mono text-zinc-400">
                        <FileCode className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
                        <span className="truncate">{f.affected_files.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-3 shrink-0 ml-3 pt-0.5">
                  <span className="font-mono text-xs text-zinc-400 uppercase">
                    {f.status.replace(/_/g, ' ')}
                  </span>

                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-zinc-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-zinc-400" />
                  )}
                </div>
              </div>

              {/* Expanded details (Level 2) */}
              {isExpanded && (
                <div className="border-t border-zinc-800 bg-[#0d0d10] p-4 text-sm space-y-3.5">
                  <div>
                    <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                      Reason & Rationale
                    </h4>
                    <p className="text-zinc-300 leading-relaxed font-sans">{f.reason}</p>
                  </div>

                  <div>
                    <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-400 mb-1">
                      Required Action
                    </h4>
                    <div className="rounded bg-zinc-900 border border-zinc-800 p-2.5 font-mono text-sm text-zinc-200">
                      {f.required_action}
                    </div>
                  </div>

                  {f.evidence && (
                    <div>
                      <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                        Code Evidence / AST Match
                      </h4>
                      <pre className="rounded bg-zinc-950 p-2.5 font-mono text-xs text-zinc-300 whitespace-pre-wrap overflow-x-auto border border-zinc-800">
                        {f.evidence}
                      </pre>
                    </div>
                  )}

                  {f.affected_files && f.affected_files.length > 0 && (
                    <div>
                      <h4 className="font-semibold uppercase tracking-wider text-xs text-zinc-500 mb-1">
                        Affected Files ({f.affected_files.length})
                      </h4>
                      <div className="flex flex-wrap gap-1.5 font-mono">
                        {f.affected_files.map((file) => (
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

                  {f.verification_note && (
                    <div className="rounded border border-zinc-800 bg-zinc-900 p-2 text-zinc-300 text-xs font-mono">
                      Verification: {f.verification_note}
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
