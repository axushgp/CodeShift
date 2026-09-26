/**
 * RepoProfilePanel — displays the detected repository profile after scanning.
 */

import type { RepositoryProfile } from '../types'

interface RepoProfilePanelProps {
  profile: RepositoryProfile
}

export function RepoProfilePanel({ profile }: RepoProfilePanelProps) {
  return (
    <div className="cs-profile" data-testid="repo-profile">
      <h2 className="cs-profile__title">Repository Profile</h2>

      <dl className="cs-profile__grid">
        {profile.name && <Row label="Name" value={profile.name} />}
        <Row label="Ecosystem" value={profile.ecosystem} />
        <Row label="Package Manager" value={profile.package_manager} />
        {profile.runtime && <Row label="Runtime" value={profile.runtime} />}
        {profile.framework && <Row label="Framework" value={profile.framework} />}
        {profile.lockfile && <Row label="Lockfile" value={profile.lockfile} />}
      </dl>

      {Object.keys(profile.dependencies).length > 0 && (
        <section className="cs-profile__section">
          <h3 className="cs-profile__section-title">
            Dependencies ({Object.keys(profile.dependencies).length})
          </h3>
          <ul className="cs-profile__dep-list">
            {Object.entries(profile.dependencies).map(([name, version]) => (
              <li key={name} className="cs-profile__dep">
                <span className="cs-profile__dep-name">{name}</span>
                <span className="cs-profile__dep-version">{version}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {Object.keys(profile.dev_dependencies).length > 0 && (
        <section className="cs-profile__section">
          <h3 className="cs-profile__section-title">
            Dev Dependencies ({Object.keys(profile.dev_dependencies).length})
          </h3>
          <ul className="cs-profile__dep-list">
            {Object.entries(profile.dev_dependencies).map(([name, version]) => (
              <li key={name} className="cs-profile__dep">
                <span className="cs-profile__dep-name">{name}</span>
                <span className="cs-profile__dep-version">{version}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {(profile.structure.src_dirs.length > 0 ||
        profile.structure.test_dirs.length > 0 ||
        profile.structure.config_files.length > 0) && (
        <section className="cs-profile__section">
          <h3 className="cs-profile__section-title">Structure</h3>
          <dl className="cs-profile__grid">
            {profile.structure.src_dirs.length > 0 && (
              <Row label="Source dirs" value={profile.structure.src_dirs.join(', ')} />
            )}
            {profile.structure.test_dirs.length > 0 && (
              <Row label="Test dirs" value={profile.structure.test_dirs.join(', ')} />
            )}
            {profile.structure.config_files.length > 0 && (
              <Row label="Config files" value={profile.structure.config_files.join(', ')} />
            )}
          </dl>
        </section>
      )}
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <>
      <dt className="cs-profile__label">{label}</dt>
      <dd className="cs-profile__value">{value}</dd>
    </>
  )
}
