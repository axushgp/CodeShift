/**
 * VerificationPanel — displays Twin migration results, verification checks,
 * and regression diagnosis/repair status.
 */

import { useState } from 'react'
import type { TwinResult, VerificationRun } from '../types'

interface VerificationPanelProps {
  twinResult?: TwinResult | null
  verificationRun?: VerificationRun | null
}

export function VerificationPanel({ twinResult, verificationRun }: VerificationPanelProps) {
  const [showDiff, setShowDiff] = useState(false)

  if (!twinResult && !verificationRun) {
    return null
  }

  const ver = verificationRun?.verification
  const isVerified = verificationRun?.passed ?? false
  const outcomeText = isVerified ? 'VERIFIED' : 'REQUIRES HUMAN REVIEW'
  const outcomeBadgeClass = isVerified
    ? 'cs-badge--success'
    : 'cs-badge--warning'

  return (
    <div className="cs-panel cs-verification" data-testid="verification-panel">
      <div className="cs-panel__header-row">
        <h2 className="cs-panel__title">Rehearsal Verification</h2>
        <span className={`cs-badge ${outcomeBadgeClass}`} data-testid="verification-outcome">
          {outcomeText}
        </span>
      </div>

      {/* Twin workspace migration summary */}
      {twinResult && (
        <div className="cs-verification__section">
          <h3 className="cs-panel__subtitle">Twin Workspace Execution</h3>
          <p className="cs-verification__summary">
            Status: <strong>{twinResult.migration_status}</strong> &bull;{' '}
            {twinResult.changed_files.length} file(s) modified in disposable Twin
          </p>

          {twinResult.changed_files.length > 0 && (
            <ul className="cs-verification__file-list">
              {twinResult.changed_files.map((cf) => (
                <li key={cf.path} className="cs-verification__file-item">
                  <span className="cs-verification__file-type">[{cf.change_type}]</span>{' '}
                  <code>{cf.path}</code>
                </li>
              ))}
            </ul>
          )}

          {twinResult.git_diff && (
            <div className="cs-verification__diff-toggle">
              <button
                type="button"
                className="cs-btn cs-btn--secondary cs-btn--small"
                onClick={() => setShowDiff((v) => !v)}
              >
                {showDiff ? 'Hide Twin Diff' : 'View Rehearsed Diff'}
              </button>
              {showDiff && (
                <pre className="cs-verification__diff-block">{twinResult.git_diff}</pre>
              )}
            </div>
          )}
        </div>
      )}

      {/* Verification & Regression Details */}
      {verificationRun && (
        <div className="cs-verification__section">
          <h3 className="cs-panel__subtitle">
            Checks & Regressions (Round {verificationRun.round})
          </h3>

          {verificationRun.summary && (
            <p className="cs-verification__run-summary">{verificationRun.summary}</p>
          )}

          {ver && (
            <dl className="cs-profile__grid">
              <dt className="cs-profile__label">Baseline Comparison</dt>
              <dd className="cs-profile__value">
                {ver.baseline_test_passed != null && ver.baseline_test_total != null
                  ? `${ver.baseline_test_passed}/${ver.baseline_test_total} baseline tests passing`
                  : 'No baseline test counts'}
              </dd>

              <dt className="cs-profile__label">Twin Verification</dt>
              <dd className="cs-profile__value">
                {ver.test_summary
                  ? `${ver.test_summary.passed}/${ver.test_summary.total} tests passing`
                  : ver.passed
                    ? 'All executed checks passed'
                    : 'Checks failed'}
              </dd>

              <dt className="cs-profile__label">Regressions</dt>
              <dd className="cs-profile__value">
                {ver.regression_count === 0
                  ? '0 regressions'
                  : `${ver.regression_count} regression(s) detected`}
              </dd>
            </dl>
          )}

          {/* Diagnoses & Repairs */}
          {verificationRun.diagnoses && verificationRun.diagnoses.length > 0 && (
            <div className="cs-verification__diagnoses">
              <h4 className="cs-panel__subsubtitle">Diagnoses & Targeted Repairs</h4>
              <ul className="cs-verification__diag-list">
                {verificationRun.diagnoses.map((d, i) => (
                  <li key={i} className="cs-verification__diag-item">
                    <strong>[{d.step}]</strong> {d.root_cause}
                    {d.repair_applied && (
                      <span className="cs-badge cs-badge--success cs-badge--inline">
                        Repair Applied
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
