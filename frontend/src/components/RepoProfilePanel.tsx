/**
 * RepoProfilePanel — Comprehensive Repository Intelligence Display.
 * Exposes Level 1 (Overview), Level 2 (Analysis: Identity, Environment, Dependencies, Scripts, Structure),
 * and Level 3 (Technical Details & Raw Manifest Drawer).
 */

import { useState, useMemo } from 'react'
import {
  Boxes,
  Code2,
  FileCode,
  FolderTree,
  GitBranch,
  Layers,
  Package,
  Search,
  Server,
  Settings,
  Terminal,
  Cpu,
  CheckCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from 'lucide-react'
import type { RepositoryProfile } from '../types'

interface RepoProfilePanelProps {
  profile: RepositoryProfile
  targetUpgrade?: {
    package: string
    from_version?: string
    to_version: string
  }
}

export function RepoProfilePanel({ profile, targetUpgrade }: RepoProfilePanelProps) {
  const [depSearch, setDepSearch] = useState('')
  const [activeDepTab, setActiveDepTab] = useState<'all' | 'prod' | 'dev' | 'migration'>('migration')
  const [showRawManifest, setShowRawManifest] = useState(false)
  const [copiedRaw, setCopiedRaw] = useState(false)

  // Identify migration-relevant dependencies
  const migrationRelevantPkgs = useMemo(() => {
    const target = targetUpgrade?.package.toLowerCase() ?? 'react'
    const related = [target, `${target}-dom`, `@types/${target}`, `@types/${target}-dom`, 'vite', 'webpack']
    return related
  }, [targetUpgrade])

  // Filter dependencies
  const filteredDeps = useMemo(() => {
    const q = depSearch.toLowerCase()
    const allProd = Object.entries(profile.dependencies || {}).map(([name, version]) => ({
      name,
      version,
      type: 'prod' as const,
      isMigration: migrationRelevantPkgs.some((p) => name.toLowerCase().includes(p)),
    }))

    const allDev = Object.entries(profile.dev_dependencies || {}).map(([name, version]) => ({
      name,
      version,
      type: 'dev' as const,
      isMigration: migrationRelevantPkgs.some((p) => name.toLowerCase().includes(p)),
    }))

    let combined = [...allProd, ...allDev]

    if (activeDepTab === 'prod') combined = allProd
    else if (activeDepTab === 'dev') combined = allDev
    else if (activeDepTab === 'migration') combined = combined.filter((d) => d.isMigration)

    if (q) {
      combined = combined.filter((d) => d.name.toLowerCase().includes(q) || d.version.toLowerCase().includes(q))
    }

    return combined
  }, [profile.dependencies, profile.dev_dependencies, depSearch, activeDepTab, migrationRelevantPkgs])

  const handleCopyRaw = () => {
    if (!profile.raw_manifest) return
    navigator.clipboard.writeText(JSON.stringify(profile.raw_manifest, null, 2))
    setCopiedRaw(true)
    setTimeout(() => setCopiedRaw(false), 2000)
  }

  const allExecutedScriptNames = useMemo(() => {
    const executed = new Set<string>()
    profile.build_scripts?.forEach((s) => executed.add(s.name))
    profile.test_scripts?.forEach((s) => executed.add(s.name))
    profile.lint_scripts?.forEach((s) => executed.add(s.name))
    return executed
  }, [profile.build_scripts, profile.test_scripts, profile.lint_scripts])

  return (
    <div className="space-y-4" data-testid="repo-profile">
      {/* ── Section 1: Executive Repository Overview Grid ──────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center space-x-2">
            <Package className="h-4 w-4 text-zinc-400" />
            <h3 className="text-base font-semibold tracking-wide text-white">
              Repository Overview
            </h3>
          </div>
          {profile.source_url && (
            <a
              href={profile.source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1 text-sm text-zinc-400 hover:text-white"
            >
              <span className="font-mono text-xs truncate max-w-xs">{profile.source_url}</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-4">
          <OverviewItem
            icon={GitBranch}
            label="Project Name"
            value={profile.name || 'Anonymous Repository'}
            sub="from package.json"
          />
          <OverviewItem
            icon={Layers}
            label="Ecosystem"
            value={profile.ecosystem.toUpperCase()}
          />
          <OverviewItem
            icon={Boxes}
            label="Framework"
            value={profile.framework ? profile.framework.toUpperCase() : 'Standard'}
          />
          <OverviewItem
            icon={Terminal}
            label="Package Manager"
            value={profile.package_manager}
            sub={profile.package_manager_version ? `v${profile.package_manager_version}` : undefined}
          />
          <OverviewItem
            icon={Server}
            label="Runtime Engine"
            value={profile.runtime || 'Node.js detected'}
          />
          <OverviewItem
            icon={FileCode}
            label="Lockfile"
            value={profile.lockfile || 'None detected'}
            sub={profile.lockfile ? 'deterministic' : 'unpinned'}
          />
          {profile.dependencies?.react && (
            <OverviewItem
              icon={Code2}
              label="React Version"
              value={profile.dependencies.react}
            />
          )}
          {profile.dependencies?.['react-dom'] && (
            <OverviewItem
              icon={Code2}
              label="ReactDOM Version"
              value={profile.dependencies['react-dom']}
            />
          )}
        </div>
      </div>

      {/* ── Section 2: Detailed Repository Analysis (Tabbed Intelligence) ────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3">
          <Cpu className="h-4 w-4 text-zinc-400" />
          <h3 className="text-base font-semibold tracking-wide text-white">
            Complete Repository Analysis
          </h3>
          <span className="font-mono text-xs text-zinc-500 uppercase">
            [AUTO-PROFILED]
          </span>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column: Environment & Structure */}
          <div className="space-y-4">
            {/* Project Structure */}
            <div className="rounded border border-zinc-800 bg-zinc-900/40 p-4">
              <div className="mb-3 flex items-center space-x-2 text-sm font-semibold uppercase tracking-wider text-zinc-300">
                <FolderTree className="h-4 w-4 text-zinc-400" />
                <span>Project Structure & Directories</span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <StructureRow
                  label="Source Dirs"
                  items={profile.structure.src_dirs}
                  emptyLabel="Root directory"
                />
                <StructureRow
                  label="Test Dirs"
                  items={profile.structure.test_dirs}
                  emptyLabel="Inline / root"
                />
                <StructureRow
                  label="Config Files"
                  items={profile.structure.config_files}
                  emptyLabel="No root config files"
                />
                {profile.structure.entry_points && profile.structure.entry_points.length > 0 && (
                  <StructureRow
                    label="Entry Points"
                    items={profile.structure.entry_points}
                  />
                )}
              </div>
            </div>

            {/* Runtime & Environment Requirements */}
            <div className="rounded border border-zinc-800 bg-zinc-900/40 p-4">
              <div className="mb-3 flex items-center space-x-2 text-sm font-semibold uppercase tracking-wider text-zinc-300">
                <Settings className="h-4 w-4 text-zinc-400" />
                <span>Runtime & Engine Requirements</span>
              </div>
              {profile.environment_requirements &&
              Object.keys(profile.environment_requirements).length > 0 ? (
                <div className="grid grid-cols-2 gap-2 text-sm font-mono">
                  {Object.entries(profile.environment_requirements).map(([k, v]) => (
                    <div
                      key={k}
                      className="flex items-center justify-between rounded border border-zinc-800 bg-zinc-950/60 px-2.5 py-1.5"
                    >
                      <span className="text-zinc-500">{k}:</span>
                      <span className="font-semibold text-zinc-200">{v}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-zinc-500 font-mono">
                  No strict engine constraints specified in package.json engines field.
                </p>
              )}
            </div>

            {/* Detection Details */}
            <div className="rounded border border-zinc-800 bg-zinc-900/40 p-4">
              <div className="mb-2 text-sm font-semibold uppercase tracking-wider text-zinc-300">
                Detection Conclusions
              </div>
              <ul className="space-y-1.5 text-sm text-zinc-400">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>
                    Package manager resolved to{' '}
                    <strong className="text-zinc-200 font-mono">{profile.package_manager}</strong> via lockfile / package metadata.
                  </span>
                </li>
                {profile.framework && (
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-emerald-400 shrink-0" />
                    <span>
                      Primary framework recognized as{' '}
                      <strong className="text-zinc-200 font-mono">{profile.framework}</strong>.
                    </span>
                  </li>
                )}
                <li className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>
                    Target upgrade scenario: <strong className="text-zinc-200 font-mono">React 17 &rarr; 18</strong>
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Column: Scripts & Commands */}
          <div className="space-y-4">
            <div className="rounded border border-zinc-800 bg-zinc-900/40 p-4">
              <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sm font-semibold uppercase tracking-wider text-zinc-300">
                  <Terminal className="h-4 w-4 text-zinc-400" />
                  <span>Detected NPM / Package Scripts</span>
                </div>
                <span className="text-xs text-zinc-500 font-mono">
                  {profile.relevant_scripts ? Object.keys(profile.relevant_scripts).length : 0} scripts
                </span>
              </div>

              {profile.relevant_scripts && Object.keys(profile.relevant_scripts).length > 0 ? (
                <div className="max-h-72 overflow-y-auto space-y-1.5 pr-1">
                  {Object.entries(profile.relevant_scripts).map(([name, cmd]) => {
                    const wasExecuted = allExecutedScriptNames.has(name)
                    return (
                      <div
                        key={name}
                        className={`flex items-center justify-between rounded border px-3 py-2 text-sm font-mono transition ${
                          wasExecuted
                            ? 'border-zinc-700 bg-zinc-900'
                            : 'border-zinc-800/80 bg-zinc-950/60'
                        }`}
                      >
                        <div className="flex items-center space-x-2 truncate">
                          <span className="font-semibold text-zinc-200">{name}</span>
                          <span className="text-zinc-500 truncate max-w-[160px] sm:max-w-xs">{cmd}</span>
                        </div>
                        {wasExecuted && (
                          <span className="font-mono text-[10px] font-semibold text-zinc-300 uppercase shrink-0">
                            [EXECUTED]
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-sm text-zinc-500 font-mono">No scripts defined in package manifest.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Section 3: Interactive Dependency Analysis ────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-3">
          <div className="flex items-center space-x-2">
            <Boxes className="h-4 w-4 text-zinc-400" />
            <h3 className="text-base font-semibold tracking-wide text-white">
              Dependency Analysis
            </h3>
            <span className="text-xs font-mono text-zinc-400">
              ({Object.keys(profile.dependencies || {}).length} prod &bull;{' '}
              {Object.keys(profile.dev_dependencies || {}).length} dev)
            </span>
          </div>

          {/* Search & Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex rounded border border-zinc-800 bg-zinc-900/60 p-0.5 text-xs font-mono">
              <button
                type="button"
                onClick={() => setActiveDepTab('migration')}
                className={`px-2.5 py-1 font-medium transition ${
                  activeDepTab === 'migration'
                    ? 'bg-zinc-800 text-white font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Migration Target
              </button>
              <button
                type="button"
                onClick={() => setActiveDepTab('all')}
                className={`px-2.5 py-1 font-medium transition ${
                  activeDepTab === 'all'
                    ? 'bg-zinc-800 text-white font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setActiveDepTab('prod')}
                className={`px-2.5 py-1 font-medium transition ${
                  activeDepTab === 'prod'
                    ? 'bg-zinc-800 text-white font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Prod
              </button>
              <button
                type="button"
                onClick={() => setActiveDepTab('dev')}
                className={`px-2.5 py-1 font-medium transition ${
                  activeDepTab === 'dev'
                    ? 'bg-zinc-800 text-white font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Dev
              </button>
            </div>

            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
              <input
                type="text"
                placeholder="Filter dependencies..."
                value={depSearch}
                onChange={(e) => setDepSearch(e.target.value)}
                className="w-48 rounded border border-zinc-800 bg-zinc-900 py-1.5 pl-8 pr-2.5 text-sm text-zinc-200 placeholder-zinc-500 outline-none focus:border-zinc-600 font-mono"
              />
            </div>
          </div>
        </div>

        <div className="max-h-60 overflow-y-auto pr-1">
          {filteredDeps.length > 0 ? (
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3">
              {filteredDeps.map((dep) => (
                <div
                  key={`${dep.type}-${dep.name}`}
                  className={`flex items-center justify-between rounded border p-2.5 text-sm font-mono transition ${
                    dep.isMigration
                      ? 'border-zinc-700 bg-zinc-900/90'
                      : 'border-zinc-800/80 bg-zinc-900/40 hover:border-zinc-700'
                  }`}
                >
                  <div className="truncate mr-2">
                    <span className="font-semibold text-zinc-200">{dep.name}</span>
                    {dep.isMigration && (
                      <span className="ml-1.5 font-mono text-[10px] font-semibold text-zinc-400 uppercase">
                        [TARGET]
                      </span>
                    )}
                  </div>
                  <span className="shrink-0 text-xs text-zinc-400">
                    {dep.version}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-6 text-center text-sm text-zinc-500 font-mono">
              No dependencies match current filter criteria.
            </p>
          )}
        </div>
      </div>

      {/* ── Section 4: Collapsible Technical Details / Raw Manifest Drawer ──── */}
      {profile.raw_manifest && (
        <div className="rounded border border-zinc-800 bg-[#121214] overflow-hidden">
          <button
            type="button"
            onClick={() => setShowRawManifest(!showRawManifest)}
            className="flex w-full items-center justify-between p-4 text-left transition hover:bg-zinc-900/40"
          >
            <div className="flex items-center space-x-2 text-sm font-semibold text-zinc-200">
              {showRawManifest ? (
                <ChevronDown className="h-4 w-4 text-zinc-400" />
              ) : (
                <ChevronRight className="h-4 w-4 text-zinc-400" />
              )}
              <span>Raw Package Manifest (package.json)</span>
            </div>
            <span className="text-xs font-mono text-zinc-500">
              {showRawManifest ? 'Click to collapse' : 'Click to inspect raw AST'}
            </span>
          </button>

          {showRawManifest && (
            <div className="border-t border-zinc-800 bg-[#0d0d10] p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">
                  Full Manifest JSON
                </span>
                <button
                  type="button"
                  onClick={handleCopyRaw}
                  className="inline-flex items-center space-x-1 text-xs text-zinc-400 hover:text-white"
                >
                  {copiedRaw ? (
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                  <span>{copiedRaw ? 'Copied' : 'Copy JSON'}</span>
                </button>
              </div>
              <pre className="max-h-80 overflow-y-auto rounded bg-zinc-950 p-3 font-mono text-xs text-zinc-300 border border-zinc-800">
                {JSON.stringify(profile.raw_manifest, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function OverviewItem({
  icon: Icon,
  label,
  value,
  sub,
  badge,
}: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  badge?: string
}) {
  return (
    <div className="rounded border border-zinc-800 bg-zinc-900/40 p-3.5 transition hover:border-zinc-700">
      <div className="flex items-center justify-between text-zinc-400">
        <span className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-500">{label}</span>
        <Icon className="h-4 w-4 text-zinc-500" />
      </div>
      <div className="mt-1 flex items-baseline justify-between">
        <span className="font-mono text-sm font-semibold text-zinc-100 truncate">{value}</span>
        {badge && (
          <span className="text-[10px] font-mono text-zinc-500 uppercase">
            {badge}
          </span>
        )}
      </div>
      {sub && <span className="text-xs text-zinc-500 font-mono truncate block mt-0.5">{sub}</span>}
    </div>
  )
}

function StructureRow({
  label,
  items,
  emptyLabel,
}: {
  label: string
  items: string[]
  emptyLabel?: string
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between border-b border-zinc-800/40 pb-2 last:border-0 last:pb-0">
      <span className="text-zinc-400 text-xs font-mono">{label}:</span>
      {items.length > 0 ? (
        <span className="text-zinc-200 text-right truncate max-w-xs text-sm">{items.join(', ')}</span>
      ) : (
        <span className="text-zinc-600 text-right text-sm">{emptyLabel || 'None'}</span>
      )}
    </div>
  )
}
