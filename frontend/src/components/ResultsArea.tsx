/**
 * ResultsArea — placeholder for migration findings and verification results.
 *
 * Populated by later sessions when findings and verification results exist.
 */

import type { MigrationFinding } from '../types'

interface ResultsAreaProps {
  findings?: MigrationFinding[]
  isLoading?: boolean
}

export function ResultsArea({ findings, isLoading = false }: ResultsAreaProps) {
  if (isLoading) {
    return (
      <div className="cs-results cs-results--loading" data-testid="results-loading">
        <p>Analyzing migration...</p>
      </div>
    )
  }

  if (!findings || findings.length === 0) {
    return (
      <div className="cs-results cs-results--empty" data-testid="results-empty">
        <p>No findings yet. Start a rehearsal to see migration analysis.</p>
      </div>
    )
  }

  return (
    <div className="cs-results" data-testid="results-area">
      <h2 className="cs-results__title">Migration Findings ({findings.length})</h2>
      <ul className="cs-results__list">
        {findings.map((finding) => (
          <li key={finding.id} className={`cs-finding cs-finding--${finding.severity.toLowerCase()}`}>
            <span className="cs-finding__severity">{finding.severity}</span>
            <span className="cs-finding__title">{finding.title}</span>
            <span className="cs-finding__status">{finding.status}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
