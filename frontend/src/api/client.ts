/**
 * API client foundation.
 *
 * Thin wrapper around fetch that adds base URL management and consistent
 * error handling.
 */

import type { RehearsalResponse } from '../types'

const BASE_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '')

export class ApiClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
    message: string
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BASE_URL}${path}`

  // Don't force Content-Type for FormData — browser sets it with boundary.
  const isFormData = options?.body instanceof FormData
  const headers: HeadersInit = isFormData
    ? { ...(options?.headers ?? {}) }
    : { 'Content-Type': 'application/json', ...(options?.headers ?? {}) }

  const response = await fetch(url, {
    headers,
    ...options,
  })

  if (!response.ok) {
    let body: unknown
    try {
      body = await response.json()
    } catch {
      body = null
    }
    throw new ApiClientError(
      response.status,
      body,
      `API request failed: ${response.status} ${response.statusText}`
    )
  }

  return response.json() as Promise<T>
}

export const apiClient = {
  get: <T>(path: string, options?: RequestInit): Promise<T> =>
    request<T>(path, { method: 'GET', ...options }),

  post: <T>(path: string, body?: unknown, options?: RequestInit): Promise<T> =>
    request<T>(path, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
      ...options,
    }),

  postForm: <T>(path: string, formData: FormData): Promise<T> =>
    request<T>(path, { method: 'POST', body: formData }),
}

// ── Rehearsal endpoints ──────────────────────────────────────────────────────

export interface StartRehearsalUrlPayload {
  repository_url: string
  target_package?: string
  target_version?: string
  from_version?: string
  discovery_id?: string
}

export function startRehearsalFromUrl(payload: StartRehearsalUrlPayload): Promise<RehearsalResponse> {
  return apiClient.post<RehearsalResponse>('/api/rehearsals', payload)
}

export function startRehearsalFromZip(
  file: File,
  targetPackage?: string,
  targetVersion?: string,
  fromVersion?: string,
  discoveryId?: string,
): Promise<RehearsalResponse> {
  const form = new FormData()
  form.append('file', file)
  if (targetPackage) form.append('target_package', targetPackage)
  if (targetVersion) form.append('target_version', targetVersion)
  if (fromVersion) form.append('from_version', fromVersion)
  if (discoveryId) form.append('discovery_id', discoveryId)
  return apiClient.postForm<RehearsalResponse>('/api/rehearsals/upload', form)
}

// ── Target Discovery & Migration Knowledge endpoints ─────────────────────────

export function discoverTargetsFromUrl(repositoryUrl: string): Promise<import('../types').DiscoveredTargets> {
  return apiClient.post<import('../types').DiscoveredTargets>('/api/migrations/discover', {
    repository_url: repositoryUrl,
  })
}

export function discoverTargetsFromZip(file: File): Promise<import('../types').DiscoveredTargets> {
  const form = new FormData()
  form.append('zip_file', file)
  return apiClient.postForm<import('../types').DiscoveredTargets>('/api/migrations/discover-zip', form)
}

export function getMigrationOptions(params: {
  rehearsalId?: string
  framework?: string
  version?: string
}): Promise<import('../types').DiscoveredTargets> {
  const query = new URLSearchParams()
  if (params.rehearsalId) query.set('rehearsal_id', params.rehearsalId)
  if (params.framework) query.set('framework', params.framework)
  if (params.version) query.set('version', params.version)
  return apiClient.get<import('../types').DiscoveredTargets>(`/api/migrations/options?${query.toString()}`)
}

export function getRehearsalStatus(rehearsalId: string): Promise<RehearsalResponse> {
  return apiClient.get<RehearsalResponse>(`/api/rehearsals/${rehearsalId}`)
}

export function getImplementationPrompt(rehearsalId: string): Promise<{ rehearsal_id: string; prompt: string }> {
  return apiClient.get<{ rehearsal_id: string; prompt: string }>(`/api/rehearsals/${rehearsalId}/implementation-prompt`)
}

export function getAgentPackDownloadUrl(rehearsalId: string): string {
  const base = BASE_URL.replace(/\/+$/, '')
  return `${base}/api/rehearsals/${rehearsalId}/agent-pack/download`
}

// ── Demo catalog endpoints ───────────────────────────────────────────────────

export function listDemos(): Promise<import('../types').DemoManifest[]> {
  return apiClient.get<import('../types').DemoManifest[]>('/api/demos')
}

export function getDemo(demoId: string): Promise<import('../types').DemoManifest> {
  return apiClient.get<import('../types').DemoManifest>(`/api/demos/${demoId}`)
}

export function launchDemo(demoId: string): Promise<RehearsalResponse> {
  return apiClient.post<RehearsalResponse>(`/api/demos/${demoId}/launch`)
}

export function approveRehearsal(rehearsalId: string): Promise<RehearsalResponse> {
  return apiClient.post<RehearsalResponse>(`/api/rehearsals/${rehearsalId}/approve`)
}

