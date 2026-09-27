/**
 * RehearsalForm — repository input, automatic framework detection, and click-to-select upgrade target.
 * Modern developer infrastructure styling inspired by Linear / Raycast.
 */

import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import {
  ArrowRight,
  FileArchive,
  Globe,
  Search,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { discoverTargetsFromUrl, discoverTargetsFromZip } from '../api/client'
import type { DiscoveredTargets, TargetOption } from '../types'

export type InputMode = 'url' | 'zip'

export interface RehearsalFormValues {
  mode: InputMode
  repositoryUrl: string
  zipFile: File | null
  targetPackage: string
  targetVersion: string
  discoveryId?: string
}

interface RehearsalFormProps {
  onSubmit: (values: RehearsalFormValues) => void
  disabled?: boolean
}

export function RehearsalForm({ onSubmit, disabled = false }: RehearsalFormProps) {
  const [mode, setMode] = useState<InputMode>('url')
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [zipFile, setZipFile] = useState<File | null>(null)
  const [targetPackage, setTargetPackage] = useState('')
  const [targetVersion, setTargetVersion] = useState('')
  const [discoveryId, setDiscoveryId] = useState<string | undefined>(undefined)

  const [isScanning, setIsScanning] = useState(false)
  const [scanError, setScanError] = useState<string | null>(null)
  const [discovery, setDiscovery] = useState<DiscoveredTargets | null>(null)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null
    setZipFile(f)
    setDiscovery(null)
    setScanError(null)
  }

  function handleUrlChange(e: ChangeEvent<HTMLInputElement>) {
    setRepositoryUrl(e.target.value)
    if (discovery) {
      setDiscovery(null)
      setScanError(null)
    }
  }

  function handleApplyPreset(pkg: string, ver: string) {
    setTargetPackage(pkg)
    setTargetVersion(ver)
  }

  async function handleScan() {
    if (disabled || isScanning) return
    const urlMissing = mode === 'url' && !repositoryUrl.trim()
    const zipMissing = mode === 'zip' && !zipFile
    if (urlMissing || zipMissing) {
      setScanError(mode === 'url' ? 'Please enter a repository URL first.' : 'Please select a ZIP file first.')
      return
    }

    setIsScanning(true)
    setScanError(null)

    try {
      let result: DiscoveredTargets
      if (mode === 'url') {
        result = await discoverTargetsFromUrl(repositoryUrl.trim())
      } else {
        result = await discoverTargetsFromZip(zipFile!)
      }

      setDiscovery(result)
      if (result.discovery_id) {
        setDiscoveryId(result.discovery_id)
      }

      // Pre-fill target package and version from data-driven registry
      const pkg = result.detected_framework.package || 'react'
      const ver =
        result.upgrade_target.recommended_target ||
        result.upgrade_target.options[0]?.target_version ||
        '18.0.0'

      setTargetPackage(pkg)
      setTargetVersion(ver)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to scan repository'
      setScanError(msg)
    } finally {
      setIsScanning(false)
    }
  }

  function handleSelectTarget(option: TargetOption) {
    setTargetVersion(option.target_version)
    if (discovery?.detected_framework.package) {
      setTargetPackage(discovery.detected_framework.package)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const urlMissing = mode === 'url' && !repositoryUrl.trim()
    const zipMissing = mode === 'zip' && !zipFile
    if (urlMissing || zipMissing) {
      return
    }

    // If target package or version is empty, fallback to defaults or trigger scan
    let pkg = targetPackage.trim()
    let ver = targetVersion.trim()

    if (!pkg && discovery) {
      pkg = discovery.detected_framework.package || 'react'
    }
    if (!ver && discovery) {
      ver = discovery.upgrade_target.recommended_target || '18.0.0'
    }

    if (!pkg) pkg = 'react'
    if (!ver) ver = '18.0.0'

    onSubmit({
      mode,
      repositoryUrl: repositoryUrl.trim(),
      zipFile,
      targetPackage: pkg,
      targetVersion: ver,
      discoveryId,
    })
  }

  return (
    <form
      className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm space-y-4"
      onSubmit={handleSubmit}
      data-testid="rehearsal-form"
    >
      {/* Mode toggle tabs */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex space-x-1 rounded bg-zinc-900 p-0.5 border border-zinc-800">
          <button
            type="button"
            className={`inline-flex items-center space-x-1.5 rounded px-3 py-1.5 text-sm font-medium transition ${
              mode === 'url'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
            onClick={() => {
              setMode('url')
              setDiscovery(null)
              setScanError(null)
            }}
            disabled={disabled}
          >
            <Globe className="h-4 w-4" />
            <span>Public Git URL</span>
          </button>
          <button
            type="button"
            className={`inline-flex items-center space-x-1.5 rounded px-3 py-1.5 text-sm font-medium transition ${
              mode === 'zip'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
            onClick={() => {
              setMode('zip')
              setDiscovery(null)
              setScanError(null)
            }}
            disabled={disabled}
          >
            <FileArchive className="h-4 w-4" />
            <span>ZIP Upload</span>
          </button>
        </div>

        <div className="hidden sm:flex items-center space-x-1.5 text-xs text-zinc-400">
          <span className="text-xs font-mono text-zinc-500">Preset:</span>
          <button
            type="button"
            onClick={() => handleApplyPreset('react', '18.0.0')}
            disabled={disabled}
            className="rounded border border-zinc-700 bg-zinc-800 px-2.5 py-1 text-xs font-mono text-zinc-300 hover:bg-zinc-700 hover:text-white transition"
          >
            React 18
          </button>
        </div>
      </div>

      {/* Repository Intake Row */}
      {mode === 'url' ? (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label htmlFor="repo-url" className="block text-sm font-medium text-zinc-300">
              Repository URL
            </label>
            <span className="text-xs text-zinc-500 font-mono">
              Auto-detects framework and upgrade paths
            </span>
          </div>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                id="repo-url"
                type="url"
                className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
                placeholder="https://github.com/organization/repository"
                value={repositoryUrl}
                onChange={handleUrlChange}
                disabled={disabled || isScanning}
                required={mode === 'url'}
                data-testid="input-repo-url"
              />
            </div>
            <button
              type="button"
              onClick={handleScan}
              disabled={disabled || isScanning || !repositoryUrl.trim()}
              data-testid="btn-scan-repo"
              className="inline-flex items-center space-x-1.5 rounded border border-zinc-700 bg-zinc-800 px-3.5 py-2 text-sm font-medium text-zinc-200 hover:bg-zinc-700 hover:text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isScanning ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-zinc-400" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 text-zinc-400" />
                  <span>Scan Stack</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label htmlFor="repo-zip" className="block text-sm font-medium text-zinc-300">
              Repository ZIP Archive
            </label>
            <span className="text-xs text-zinc-500 font-mono">
              Auto-detects framework and upgrade paths
            </span>
          </div>
          <div className="flex gap-2">
            <input
              id="repo-zip"
              type="file"
              accept=".zip,application/zip"
              className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-300 file:mr-3 file:rounded file:border-0 file:bg-zinc-800 file:px-2.5 file:py-1 file:text-xs file:font-medium file:text-zinc-200 hover:file:bg-zinc-700 outline-none transition focus:border-zinc-400 disabled:opacity-50"
              ref={fileInputRef}
              onChange={handleFileChange}
              disabled={disabled || isScanning}
              required={mode === 'zip'}
              data-testid="input-repo-zip"
            />
            <button
              type="button"
              onClick={handleScan}
              disabled={disabled || isScanning || !zipFile}
              data-testid="btn-scan-zip"
              className="inline-flex items-center space-x-1.5 rounded border border-zinc-700 bg-zinc-800 px-3.5 py-2 text-sm font-medium text-zinc-200 hover:bg-zinc-700 hover:text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isScanning ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-zinc-400" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 text-zinc-400" />
                  <span>Scan Stack</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Error state during scan */}
      {scanError && (
        <div className="rounded border border-red-900/60 bg-red-950/20 p-3 text-xs text-red-300 flex items-start space-x-2">
          <AlertCircle className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
          <span>{scanError}</span>
        </div>
      )}

      {/* ── Discovered Stack & Target Selection ────────────────────────────── */}
      {discovery && (
        <div className="space-y-3 pt-1" data-testid="discovery-section">
          {/* DETECTED STACK */}
          <div className="rounded border border-zinc-800 bg-zinc-900/40 p-3.5">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2 mb-2.5">
              <div className="flex items-center space-x-2">
                <Layers className="h-3.5 w-3.5 text-zinc-400" />
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-zinc-300">
                  Detected Stack
                </span>
              </div>
              <span className="text-[11px] font-mono text-zinc-500">
                Registry: {discovery.knowledge_updated}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4 text-xs font-mono">
              <div className="rounded border border-zinc-800 bg-[#121214] p-2">
                <span className="text-zinc-500 block text-[11px]">Framework</span>
                <span className="text-zinc-200 font-semibold mt-0.5 block">
                  {discovery.detected_framework.name} {discovery.detected_version || 'detected'}
                </span>
              </div>
              <div className="rounded border border-zinc-800 bg-[#121214] p-2">
                <span className="text-zinc-500 block text-[11px]">Build Tool</span>
                <span className="text-zinc-300 mt-0.5 block">
                  {discovery.tooling.build_tool || 'Standard'}
                </span>
              </div>
              <div className="rounded border border-zinc-800 bg-[#121214] p-2">
                <span className="text-zinc-500 block text-[11px]">Runtime</span>
                <span className="text-zinc-300 mt-0.5 block">
                  {discovery.tooling.runtime}
                </span>
              </div>
              <div className="rounded border border-zinc-800 bg-[#121214] p-2">
                <span className="text-zinc-500 block text-[11px]">Package Manager</span>
                <span className="text-zinc-300 mt-0.5 block">
                  {discovery.tooling.package_manager}
                </span>
              </div>
            </div>
          </div>

          {/* UPGRADE TARGET SELECTION */}
          <div className="rounded border border-zinc-800 bg-zinc-900/40 p-3.5">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2 mb-2.5">
              <div className="flex items-center space-x-2">
                <Cpu className="h-3.5 w-3.5 text-zinc-400" />
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-zinc-300">
                  Upgrade Target
                </span>
              </div>
              <span className="text-xs font-mono text-zinc-400">
                Current: <strong className="text-zinc-200">{discovery.upgrade_target.current}</strong>
              </span>
            </div>

            {discovery.upgrade_target.options.length > 0 ? (
              <div className="space-y-2">
                <div className="text-xs text-zinc-400 font-mono">Choose upgrade target:</div>
                <div className="flex flex-wrap gap-2">
                  {discovery.upgrade_target.options.map((opt) => {
                    const isSelected = targetVersion === opt.target_version
                    return (
                      <button
                        key={opt.target_version}
                        type="button"
                        onClick={() => handleSelectTarget(opt)}
                        disabled={disabled}
                        className={`inline-flex items-center space-x-2 rounded border px-3 py-1.5 text-xs font-mono transition ${
                          isSelected
                            ? 'border-white bg-zinc-800 text-white font-semibold shadow-sm'
                            : 'border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-zinc-600 hover:text-white'
                        }`}
                      >
                        {isSelected && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
                        <span>{opt.label || `${discovery.detected_framework.name} ${opt.target_version}`}</span>
                        {opt.is_recommended && (
                          <span className="rounded bg-emerald-950/60 border border-emerald-800/80 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">
                            Recommended
                          </span>
                        )}
                        {opt.has_certified_recipe && !opt.is_recommended && (
                          <span className="rounded bg-zinc-800 border border-zinc-700 px-1.5 py-0.5 text-[10px] text-zinc-400">
                            Automated
                          </span>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div className="rounded border border-amber-900/60 bg-amber-950/20 p-3 text-xs text-amber-300 flex items-start space-x-2 font-mono">
                <AlertCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold">No certified automated migration path available</div>
                  <div className="text-amber-400/80 mt-0.5">
                    CodeShift will perform deep AI-assisted repository analysis with Watsonx and produce an auditable human review migration plan.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Target upgrade fields (collapsible manual override, fully preserving testids) */}
      <div className="pt-1">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-zinc-500 hover:text-zinc-300 transition"
        >
          {showAdvanced ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          <span>{showAdvanced ? 'Hide manual target controls' : 'Show manual target controls / overrides'}</span>
        </button>

        <div className={`mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2 ${showAdvanced ? 'block' : 'hidden'}`}>
          <div className="space-y-1">
            <label htmlFor="target-pkg" className="block text-xs font-medium text-zinc-400">
              Target Package / Framework
            </label>
            <input
              id="target-pkg"
              type="text"
              className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
              placeholder="e.g. react"
              value={targetPackage}
              onChange={(e) => setTargetPackage(e.target.value)}
              disabled={disabled}
              required
              data-testid="input-target-package"
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="target-ver" className="block text-xs font-medium text-zinc-400">
              Target Version
            </label>
            <input
              id="target-ver"
              type="text"
              className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
              placeholder="e.g. 18.0.0"
              value={targetVersion}
              onChange={(e) => setTargetVersion(e.target.value)}
              disabled={disabled}
              required
              data-testid="input-target-version"
            />
          </div>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="flex items-center justify-between border-t border-zinc-800/80 pt-3">
        <div className="text-xs text-zinc-500 font-mono">
          Isolated Git worktree Twin &bull; Non-destructive rehearsal
        </div>

        <button
          type="submit"
          disabled={disabled || isScanning}
          data-testid="btn-start-rehearsal"
          className="ml-auto inline-flex items-center space-x-1.5 rounded bg-white px-4 py-2 text-sm font-semibold text-black transition hover:bg-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span>Start Rehearsal</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </form>
  )
}
