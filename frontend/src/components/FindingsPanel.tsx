/**
 * FindingsPanel — displays migration findings identified during analysis.
 */

import type { MigrationFinding } from '../types'

interface FindingsPanelProps {
  findings: MigrationFinding[]
}

export function FindingsPanel({ findings }: FindingsPanelProps) {
  if (!findings || findings.length === 0) {
    return null
  }

  return (
    <div className="cs-panel cs-findings" data-testid="findings-panel">
      <h2 className="cs-panel__title">
        Migration Findings ({findings.length})
      </h2>

      <div className="cs-findings__list">
        {findings.map((f) => (
          <div
            key={f.id}
            className={`cs-finding cs-finding--${f.severity.toLowerCase()}`}
            data-testid={`finding-${f.id}`}
          >
            <div className="cs-finding__header">
              <span className={`cs-badge cs-badge--severity-${f.severity.toLowerCase()}`}>
                {f.severity}
              </span>
              <span className={`cs-badge cs-badge--status-${f.status.toLowerCase().replace(/_/g, '-')}`}>
                {f.status.replace(/_/g, ' ')}
              </span>
              <span className="cs-finding__title">{f.title}</span>
            </div>

            <p className="cs-finding__reason">{f.reason}</p>

            <div className="cs-finding__action">
              <strong>Required Action:</strong> {f.required_action}
            </div>

            {f.affected_files && f.affected_files.length > 0 && (
              <div className="cs-finding__files">
                <strong>Affected Files:</strong> {f.affected_files.join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
