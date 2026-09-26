/**
 * RehearsalForm — repository input and start rehearsal action.
 * Modern developer infrastructure styling inspired by Linear / Raycast.
 */

import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { ArrowRight, FileArchive, Globe } from 'lucide-react'

export type InputMode = 'url' | 'zip'

export interface RehearsalFormValues {
  mode: InputMode
  repositoryUrl: string
  zipFile: File | null
  targetPackage: string
  targetVersion: string
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
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null
    setZipFile(f)
  }

  function handleApplyPreset(pkg: string, ver: string) {
    setTargetPackage(pkg)
    setTargetVersion(ver)
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const urlMissing = mode === 'url' && !repositoryUrl.trim()
    const zipMissing = mode === 'zip' && !zipFile
    if (urlMissing || zipMissing || !targetPackage.trim() || !targetVersion.trim()) {
      return
    }
    onSubmit({ mode, repositoryUrl, zipFile, targetPackage, targetVersion })
  }

  return (
    <form
      className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm"
      onSubmit={handleSubmit}
      data-testid="rehearsal-form"
    >
      {/* Mode toggle tabs */}
      <div className="mb-4 flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex space-x-1 rounded bg-zinc-900 p-0.5 border border-zinc-800">
          <button
            type="button"
            className={`inline-flex items-center space-x-1.5 rounded px-3 py-1.5 text-sm font-medium transition ${
              mode === 'url'
                ? 'bg-zinc-800 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
            onClick={() => setMode('url')}
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
            onClick={() => setMode('zip')}
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

      {mode === 'url' ? (
        <div className="space-y-1.5">
          <label htmlFor="repo-url" className="block text-sm font-medium text-zinc-300">
            Repository URL
          </label>
          <div className="relative">
            <input
              id="repo-url"
              type="url"
              className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
              placeholder="https://github.com/organization/repository"
              value={repositoryUrl}
              onChange={(e) => setRepositoryUrl(e.target.value)}
              disabled={disabled}
              required={mode === 'url'}
              data-testid="input-repo-url"
            />
          </div>
        </div>
      ) : (
        <div className="space-y-1.5">
          <label htmlFor="repo-zip" className="block text-sm font-medium text-zinc-300">
            Repository ZIP Archive
          </label>
          <input
            id="repo-zip"
            type="file"
            accept=".zip,application/zip"
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-300 file:mr-3 file:rounded file:border-0 file:bg-zinc-800 file:px-2.5 file:py-1 file:text-xs file:font-medium file:text-zinc-200 hover:file:bg-zinc-700 outline-none transition focus:border-zinc-400 disabled:opacity-50"
            ref={fileInputRef}
            onChange={handleFileChange}
            disabled={disabled}
            required={mode === 'zip'}
            data-testid="input-repo-zip"
          />
        </div>
      )}

      {/* Target upgrade fields */}
      <div className="mt-3.5 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label htmlFor="target-pkg" className="block text-sm font-medium text-zinc-300">
            Target Package / Framework
          </label>
          <input
            id="target-pkg"
            type="text"
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
            placeholder="e.g. react"
            value={targetPackage}
            onChange={(e) => setTargetPackage(e.target.value)}
            disabled={disabled}
            required
            data-testid="input-target-package"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="target-ver" className="block text-sm font-medium text-zinc-300">
            Target Version
          </label>
          <input
            id="target-ver"
            type="text"
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3.5 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-zinc-400 disabled:opacity-50 font-mono"
            placeholder="e.g. 18.0.0"
            value={targetVersion}
            onChange={(e) => setTargetVersion(e.target.value)}
            disabled={disabled}
            required
            data-testid="input-target-version"
          />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-zinc-800/80 pt-3.5">
        <div className="text-xs text-zinc-500 font-mono">
          Isolated Git worktree Twin &bull; Non-destructive rehearsal
        </div>

        <button
          type="submit"
          disabled={disabled}
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
