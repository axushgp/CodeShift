/**
 * WorkflowStepper component.
 * Visual pipeline stepper showing:
 * Intake → Scan → Baseline → Analyze → Twin → Migrate → Verify → Diagnose → Finalize
 */

import type { RehearsalStage, RehearsalStatus } from '../types'

interface WorkflowStepperProps {
  currentStage?: RehearsalStage
  stage?: RehearsalStage
  status: RehearsalStatus
}

interface StepDef {
  key: string
  label: string
  associatedStages: RehearsalStage[]
}

const STEPS: StepDef[] = [
  { key: 'intake', label: 'Intake', associatedStages: ['INTAKE'] },
  { key: 'scan', label: 'Scan', associatedStages: ['SCANNING'] },
  { key: 'baseline', label: 'Baseline', associatedStages: ['BASELINING'] },
  { key: 'analyze', label: 'Analyze', associatedStages: ['ANALYZING'] },
  { key: 'twin', label: 'Twin', associatedStages: ['TWIN_CREATING'] },
  { key: 'migrate', label: 'Migrate', associatedStages: ['MIGRATING'] },
  { key: 'verify', label: 'Verify', associatedStages: ['VERIFYING'] },
  { key: 'diagnose', label: 'Diagnose', associatedStages: ['DIAGNOSING', 'REPAIRING'] },
  { key: 'finalize', label: 'Finalize', associatedStages: ['FINALIZING', 'COMPLETE'] },
]

export function WorkflowStepper({ currentStage: propStage, stage, status }: WorkflowStepperProps) {
  const currentStage = propStage || stage || 'INTAKE'
  const stageOrder: RehearsalStage[] = [
    'INTAKE',
    'SCANNING',
    'BASELINING',
    'ANALYZING',
    'TWIN_CREATING',
    'MIGRATING',
    'VERIFYING',
    'DIAGNOSING',
    'REPAIRING',
    'FINALIZING',
    'COMPLETE',
  ]

  const currentIndex = stageOrder.indexOf(currentStage)
  const isFailed = status === 'FAILED'
  const isReview = status === 'REQUIRES_HUMAN_REVIEW'
  const isComplete = status === 'COMPLETE'

  const getStepState = (step: StepDef) => {
    if (isComplete) {
      return 'completed'
    }

    const stepMinStageIdx = Math.min(...step.associatedStages.map((s) => stageOrder.indexOf(s)).filter((i) => i >= 0))
    const isCurrent = step.associatedStages.includes(currentStage)

    if (isCurrent) {
      if (isFailed) return 'failed'
      if (isReview) return 'requires_review'
      return 'running'
    }

    if (currentIndex >= 0 && stepMinStageIdx < currentIndex) {
      return 'completed'
    }

    if (isReview && (step.key === 'diagnose' || step.key === 'finalize')) {
      return step.key === 'diagnose' ? 'requires_review' : 'pending'
    }

    return 'pending'
  }

  return (
    <div className="w-full overflow-x-auto py-2">
      <nav aria-label="Progress" className="min-w-max">
        <ol className="flex items-center space-x-1 text-sm font-mono">
          {STEPS.map((step, idx) => {
            const state = getStepState(step)
            const isLast = idx === STEPS.length - 1

            return (
              <li key={step.key} className="flex items-center">
                <div className="flex items-center space-x-1.5">
                  {state === 'running' && (
                    <span className="flex items-center text-blue-400 space-x-1 font-semibold">
                      <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
                      <span className="text-white">{step.label}</span>
                    </span>
                  )}
                  {state === 'completed' && (
                    <span className="flex items-center text-zinc-300 space-x-1">
                      <span className="text-emerald-500 font-bold text-xs">✓</span>
                      <span>{step.label}</span>
                    </span>
                  )}
                  {state === 'failed' && (
                    <span className="flex items-center text-red-400 space-x-1 font-semibold">
                      <span className="font-bold text-xs">✕</span>
                      <span>{step.label}</span>
                    </span>
                  )}
                  {state === 'requires_review' && (
                    <span className="flex items-center text-amber-400 space-x-1 font-semibold">
                      <span className="font-bold text-xs">▲</span>
                      <span>{step.label}</span>
                    </span>
                  )}
                  {state === 'pending' && (
                    <span className="flex items-center text-zinc-600 space-x-1">
                      <span className="text-xs">○</span>
                      <span>{step.label}</span>
                    </span>
                  )}
                </div>

                {!isLast && (
                  <span className="mx-2 text-zinc-700 select-none text-xs">&rarr;</span>
                )}
              </li>
            )
          })}
        </ol>
      </nav>
    </div>
  )
}
