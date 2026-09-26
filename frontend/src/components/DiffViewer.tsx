/**
 * DiffViewer — Developer-facing syntax-highlighted Git diff viewer.
 * Highlights additions (+), removals (-), chunks (@@), and provides file navigation.
 */

import { useState, useMemo } from 'react'
import { FileDiff, Copy, Check, FileCode } from 'lucide-react'
import type { TwinResult } from '../types'

interface DiffViewerProps {
  twinResult?: TwinResult | null
}

interface DiffFileSection {
  fileName: string
  lines: string[]
  additions: number
  deletions: number
}

export function DiffViewer({ twinResult }: DiffViewerProps) {
  const [copied, setCopied] = useState(false)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const rawDiff = twinResult?.git_diff || ''

  // Parse raw git diff into per-file sections
  const fileSections: DiffFileSection[] = useMemo(() => {
    if (!rawDiff) return []

    const sections: DiffFileSection[] = []
    const lines = rawDiff.split('\n')
    let currentFile: DiffFileSection | null = null

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      if (line.startsWith('diff --git ')) {
        if (currentFile) {
          sections.push(currentFile)
        }
        // Extract file name
        const match = line.match(/b\/(.+)$/)
        const fileName = match ? match[1] : `file-${sections.length + 1}`
        currentFile = {
          fileName,
          lines: [line],
          additions: 0,
          deletions: 0,
        }
      } else if (currentFile) {
        currentFile.lines.push(line)
        if (line.startsWith('+') && !line.startsWith('+++')) {
          currentFile.additions++
        } else if (line.startsWith('-') && !line.startsWith('---')) {
          currentFile.deletions++
        }
      } else {
        // First lines before first diff header
        currentFile = {
          fileName: 'patch',
          lines: [line],
          additions: 0,
          deletions: 0,
        }
      }
    }

    if (currentFile) {
      sections.push(currentFile)
    }

    return sections
  }, [rawDiff])

  const totalAdditions = useMemo(
    () => fileSections.reduce((acc, s) => acc + s.additions, 0),
    [fileSections]
  )
  const totalDeletions = useMemo(
    () => fileSections.reduce((acc, s) => acc + s.deletions, 0),
    [fileSections]
  )

  const handleCopy = () => {
    if (!rawDiff) return
    navigator.clipboard.writeText(rawDiff)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!twinResult) {
    return (
      <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center" data-testid="diff-empty">
        <FileDiff className="mx-auto h-7 w-7 text-zinc-500" />
        <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">Twin Workspace Initializing</h3>
        <p className="mt-1 text-xs text-zinc-500 font-mono">
          The disposable Git worktree Twin environment is being prepared.
        </p>
      </div>
    )
  }

  if (!rawDiff && (!twinResult.changed_files || twinResult.changed_files.length === 0)) {
    return (
      <div className="rounded border border-zinc-800 bg-[#121214] p-8 text-center" data-testid="diff-empty">
        <FileDiff className="mx-auto h-7 w-7 text-zinc-500" />
        <h3 className="mt-2 text-xs font-semibold uppercase tracking-wider text-zinc-300">No Changes In Rehearsal</h3>
        <p className="mt-1 text-xs text-zinc-500 font-mono">
          No files were modified during the migration execution.
        </p>
      </div>
    )
  }

  const activeSection = selectedFile
    ? fileSections.find((s) => s.fileName === selectedFile) || fileSections[0]
    : null

  return (
    <div className="space-y-4" data-testid="diff-viewer">
      {/* ── Header Bar & Changed Files Navigation ─────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#121214] p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <FileDiff className="h-4 w-4 text-zinc-400" />
              <h3 className="text-base font-semibold text-white">Migration Diff</h3>
              <div className="flex items-center space-x-2 text-sm font-mono">
                <span className="text-emerald-400 font-semibold">+{totalAdditions}</span>
                <span className="text-red-400 font-semibold">-{totalDeletions}</span>
              </div>
            </div>
            <p className="mt-1 text-sm text-zinc-400">
              Verified syntax changes applied inside the disposable Git worktree Twin
            </p>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center space-x-1.5 rounded border border-zinc-700 bg-zinc-800 px-3.5 py-2 text-sm font-medium text-zinc-300 hover:bg-zinc-700 hover:text-white transition"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4 text-zinc-400" />}
            <span>{copied ? 'Copied Patch' : 'Copy Full Patch'}</span>
          </button>
        </div>

        {/* CHANGED FILES Segmented Text List */}
        <div className="mt-4">
          <div className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-semibold mb-2">
            Changed Files
          </div>
          <div className="flex flex-wrap gap-1 border border-zinc-800 bg-zinc-900/60 p-1 rounded">
            <button
              type="button"
              onClick={() => setSelectedFile(null)}
              className={`px-3 py-1.5 text-xs font-mono transition text-left ${
                selectedFile === null
                  ? 'bg-zinc-800 text-white font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              }`}
            >
              All Files ({fileSections.length})
            </button>
            {fileSections.map((section) => (
              <button
                key={section.fileName}
                type="button"
                onClick={() => setSelectedFile(section.fileName)}
                className={`inline-flex items-center space-x-2 px-3 py-1.5 text-xs font-mono transition ${
                  selectedFile === section.fileName
                    ? 'bg-zinc-800 text-white font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                }`}
              >
                <FileCode className="h-3.5 w-3.5 text-zinc-500" />
                <span>{section.fileName}</span>
                <span className="text-xs text-emerald-400 font-medium">+{section.additions}</span>
                <span className="text-xs text-red-400 font-medium">-{section.deletions}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Syntax Diff Viewer ────────────────────────────────────────────── */}
      <div className="rounded border border-zinc-800 bg-[#0d0d10] overflow-hidden">
        <div className="max-h-[550px] overflow-y-auto overflow-x-auto p-4 font-mono text-xs leading-relaxed select-text">
          {(activeSection ? [activeSection] : fileSections).map((sec, secIdx) => (
            <div key={secIdx} className="mb-6 last:mb-0">
              <div className="mb-2 flex items-center justify-between border-b border-zinc-800 pb-1.5 text-zinc-400">
                <span className="text-sm font-semibold text-zinc-200">{sec.fileName}</span>
                <span className="text-xs">
                  <span className="text-emerald-400 font-semibold">+{sec.additions}</span>{' '}
                  <span className="text-red-400 font-semibold">-{sec.deletions}</span>
                </span>
              </div>

              {sec.lines.map((line, lineIdx) => {
                const isAdd = line.startsWith('+') && !line.startsWith('+++')
                const isDel = line.startsWith('-') && !line.startsWith('---')
                const isChunk = line.startsWith('@@')
                const isHeader =
                  line.startsWith('diff --git') ||
                  line.startsWith('index ') ||
                  line.startsWith('---') ||
                  line.startsWith('+++')

                return (
                  <div
                    key={lineIdx}
                    className={`flex items-start px-2 py-0.5 rounded-none ${
                      isAdd
                        ? 'bg-emerald-950/30 text-emerald-300'
                        : isDel
                        ? 'bg-red-950/30 text-red-300'
                        : isChunk
                        ? 'bg-zinc-800/40 text-zinc-300 font-semibold'
                        : isHeader
                        ? 'text-zinc-500 text-[11px]'
                        : 'text-zinc-300'
                    }`}
                  >
                    <span className="w-5 select-none text-zinc-600 shrink-0 text-center">
                      {isAdd ? '+' : isDel ? '-' : isChunk ? '@' : ' '}
                    </span>
                    <span className="whitespace-pre-wrap break-all flex-1">
                      {isAdd || isDel ? line.slice(1) : line}
                    </span>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
