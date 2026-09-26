/**
 * Header component — CodeShift application title bar.
 */

interface HeaderProps {
  /** Optional subtitle shown below the main title */
  subtitle?: string
}

export function Header({ subtitle }: HeaderProps) {
  return (
    <header className="cs-header">
      <h1 className="cs-header__title">CodeShift</h1>
      {subtitle && <p className="cs-header__subtitle">{subtitle}</p>}
    </header>
  )
}
