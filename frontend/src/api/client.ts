/**
 * API client foundation.
 *
 * Thin wrapper around fetch that adds base URL management and consistent
 * error handling. Later sessions extend this with rehearsal endpoints.
 */

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
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
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
}
