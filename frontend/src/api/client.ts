/**
 * API client foundation.
 *
 * Thin wrapper around fetch that adds base URL management and consistent
 * error handling.
 */

import type { RehearsalResponse } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

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
  target_package: string
  target_version: string
  from_version?: string
}

export function startRehearsalFromUrl(payload: StartRehearsalUrlPayload): Promise<RehearsalResponse> {
  return apiClient.post<RehearsalResponse>('/api/rehearsals', payload)
}

export function startRehearsalFromZip(
  file: File,
  targetPackage: string,
  targetVersion: string,
  fromVersion?: string,
): Promise<RehearsalResponse> {
  const form = new FormData()
  form.append('file', file)
  form.append('target_package', targetPackage)
  form.append('target_version', targetVersion)
  if (fromVersion) form.append('from_version', fromVersion)
  return apiClient.postForm<RehearsalResponse>('/api/rehearsals/upload', form)
}

export function getRehearsalStatus(rehearsalId: string): Promise<RehearsalResponse> {
  return apiClient.get<RehearsalResponse>(`/api/rehearsals/${rehearsalId}`)
}
