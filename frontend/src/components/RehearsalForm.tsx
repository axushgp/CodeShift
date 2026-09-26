/**
 * RehearsalForm — repository input and start rehearsal action.
 *
 * Collects the two required inputs (repository URL and target upgrade)
 * and notifies the parent when the user submits.
 */

import { useState, type FormEvent } from 'react'

export interface RehearsalFormValues {
  repositoryUrl: string
  targetPackage: string
  targetVersion: string
}

interface RehearsalFormProps {
  onSubmit: (values: RehearsalFormValues) => void
  disabled?: boolean
}

export function RehearsalForm({ onSubmit, disabled = false }: RehearsalFormProps) {
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [targetPackage, setTargetPackage] = useState('')
  const [targetVersion, setTargetVersion] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!repositoryUrl.trim() || !targetPackage.trim() || !targetVersion.trim()) {
      return
    }
    onSubmit({ repositoryUrl, targetPackage, targetVersion })
  }

  return (
    <form className="cs-form" onSubmit={handleSubmit} data-testid="rehearsal-form">
      <div className="cs-form__group">
        <label htmlFor="repo-url" className="cs-form__label">
          Repository URL
        </label>
        <input
          id="repo-url"
          type="url"
          className="cs-form__input"
          placeholder="https://github.com/example/my-app"
          value={repositoryUrl}
          onChange={(e) => setRepositoryUrl(e.target.value)}
          disabled={disabled}
          required
          data-testid="input-repo-url"
        />
      </div>

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
