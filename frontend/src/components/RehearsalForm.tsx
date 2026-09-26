/**
 * RehearsalForm — repository input and start rehearsal action.
 *
 * Supports:
 * - Public Git URL
 * - ZIP file upload
 */

import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'

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
    <form className="cs-form" onSubmit={handleSubmit} data-testid="rehearsal-form">
      {/* Input mode tabs */}
      <div className="cs-form__tabs" role="group" aria-label="Repository input method">
        <button
          type="button"
          className={`cs-tab ${mode === 'url' ? 'cs-tab--active' : ''}`}
          onClick={() => setMode('url')}
          disabled={disabled}
        >
          Git URL
        </button>
        <button
          type="button"
          className={`cs-tab ${mode === 'zip' ? 'cs-tab--active' : ''}`}
          onClick={() => setMode('zip')}
          disabled={disabled}
        >
          ZIP Upload
        </button>
      </div>

      {mode === 'url' ? (
        <div className="cs-form__group">
          <label htmlFor="repo-url" className="cs-form__label">
            Public Git repository URL
          </label>
          <input
            id="repo-url"
            type="url"
            className="cs-form__input"
            placeholder="https://github.com/example/my-app"
            value={repositoryUrl}
            onChange={(e) => setRepositoryUrl(e.target.value)}
            disabled={disabled}
            required={mode === 'url'}
            data-testid="input-repo-url"
          />
        </div>
      ) : (
        <div className="cs-form__group">
          <label htmlFor="repo-zip" className="cs-form__label">
            Repository ZIP archive
          </label>
          <input
            id="repo-zip"
            type="file"
            accept=".zip,application/zip"
            className="cs-form__input"
            ref={fileInputRef}
            onChange={handleFileChange}
            disabled={disabled}
            data-testid="input-repo-zip"
          />
          {zipFile && (
            <span className="cs-form__hint">{zipFile.name} ({(zipFile.size / 1024).toFixed(1)} KB)</span>
          )}
        </div>
      )}

      <div className="cs-form__group">
        <label htmlFor="target-package" className="cs-form__label">
          Package to upgrade
        </label>
        <input
          id="target-package"
          type="text"
          className="cs-form__input"
          placeholder="e.g. react"
          value={targetPackage}
          onChange={(e) => setTargetPackage(e.target.value)}
          disabled={disabled}
          required
          data-testid="input-target-package"
        />
      </div>

      <div className="cs-form__group">
        <label htmlFor="target-version" className="cs-form__label">
          Target version
        </label>
        <input
          id="target-version"
          type="text"
          className="cs-form__input"
          placeholder="e.g. 18"
          value={targetVersion}
          onChange={(e) => setTargetVersion(e.target.value)}
          disabled={disabled}
          required
          data-testid="input-target-version"
        />
      </div>

      <button
        type="submit"
        className="cs-button cs-button--primary"
        disabled={disabled}
        data-testid="btn-start-rehearsal"
      >
        Start Rehearsal
      </button>
    </form>
  )
}
