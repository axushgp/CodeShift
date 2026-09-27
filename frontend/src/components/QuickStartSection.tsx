/**
 * QuickStartSection component.
 * Displays default verified demo repositories dynamically loaded from GET /api/demos.
 */

import { useEffect, useState } from 'react'
import { Loader2, ExternalLink } from 'lucide-react'
import { listDemos } from '../api/client'
import type { DemoManifest } from '../types'

interface QuickStartSectionProps {
  onSelectDemo?: (demoId: string) => Promise<void> | void
  onLaunchDemo?: (demoId: string) => Promise<void> | void
  disabled?: boolean
  isLaunching?: boolean
  launchingDemoId?: string | null
}

export function QuickStartSection({
  onSelectDemo,
  onLaunchDemo,
  disabled = false,
  isLaunching = false,
  launchingDemoId = null,
}: QuickStartSectionProps) {
  const handleLaunch = onSelectDemo || onLaunchDemo || (() => {})
  const isDisabled = disabled || isLaunching
  const [demos, setDemos] = useState<DemoManifest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    listDemos()
      .then((data) => {
        if (mounted) {
          setDemos(data)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load demo catalog')
          setLoading(false)
        }
      })
    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-6">
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
          <span>Loading verified Quick Start repositories...</span>
        </div>
      </div>
    )
  }

  if (error && demos.length === 0) {
    return null
  }

  return (
    <section className="w-full">
      <div className="mb-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-300">
            Quick Start Demos
          </h2>
          <span className="text-xs font-mono text-zinc-500">
            (Live React 17 Repositories)
          </span>
        </div>
        <p className="text-xs text-zinc-500 hidden sm:block">
          Run CodeShift rehearsal against a public repository
        </p>
      </div>

      <div className="rounded border border-zinc-800 bg-[#121214] divide-y divide-zinc-800/80">
        {demos.map((demo) => {
          const isCurrentLaunching = launchingDemoId === demo.id
          const isButtonDisabled = isDisabled || isCurrentLaunching

          return (
            <div
              key={demo.id}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 hover:bg-zinc-900/50 transition"
            >
              <div className="space-y-1 min-w-0 flex-1">
                <div className="flex items-center space-x-2.5">
                  <h3 className="text-sm font-semibold text-zinc-100">
                    {demo.name}
                  </h3>
                  <a
                    href={demo.repository_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-zinc-500 hover:text-zinc-300 transition"
                    title="View repository on GitHub"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                  <span className="text-xs font-mono text-zinc-500 truncate hidden md:inline">
                    {demo.repository_url.replace('https://github.com/', '')}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 truncate max-w-xl">
                  {demo.description}
                </p>
              </div>

              <div className="flex items-center justify-between sm:justify-end space-x-4 shrink-0">
                <div className="text-xs font-mono text-zinc-400">
                  {demo.package && demo.target_version ? (
                    <>
                      <span>{demo.package} {demo.source_version}</span>
                      <span className="mx-1.5 text-zinc-600">&rarr;</span>
                      <span className="text-zinc-200">{demo.target_version}</span>
                    </>
                  ) : (
                    <span className="text-zinc-400">Auto-Detect</span>
                  )}
                </div>

                <button
                  type="button"
                  data-testid={`btn-run-demo-${demo.id}`}
                  disabled={isButtonDisabled}
                  onClick={() => handleLaunch(demo.id)}
                  className="inline-flex items-center space-x-1.5 rounded border border-zinc-700 bg-zinc-800/80 px-3 py-1.5 text-xs font-medium text-zinc-200 transition hover:bg-zinc-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isCurrentLaunching ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-zinc-400" />
                      <span>Launching...</span>
                    </>
                  ) : (
                    <>
                      <span>Run Demo</span>
                      <span>&rarr;</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
