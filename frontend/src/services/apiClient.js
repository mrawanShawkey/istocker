import { STORAGE_KEYS } from '../constants/storage'

// Vite only exposes client-side env vars prefixed with VITE_.
// This is only the backend base URL, not a secret.
// Use the build-time `VITE_API_BASE_URL` when present. Otherwise:
// - in development: use local backend `http://localhost:5000`
// - in production: fall back to the secure Render URL to avoid mixed-content.
const DEFAULT_LOCAL = 'http://localhost:5000'
const DEFAULT_PROD = 'https://istocker-3.onrender.com'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.MODE === 'development' ? DEFAULT_LOCAL : DEFAULT_PROD)

export function getStoredAccessToken() {
  return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
}

export function getStoredRefreshToken() {
  return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
}

function setAccessToken(token) {
  token
    ? localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
    : localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
}

export function setAuthTokens(tokens = {}) {
  if (tokens.accessToken) localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.accessToken)
  if (tokens.refreshToken) localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken)
}

export function clearAuthTokens() {
  localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
  localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
}

function makeApiError(response, payload, fallback = 'Request failed.') {
  const error = new Error(payload?.message || fallback)
  error.status = response.status
  error.code = payload?.code
  error.payload = payload
  return error
}

async function parseJson(response) {
  if (response.status === 204) return null
  const text = await response.text()
  return text ? JSON.parse(text) : null
}

async function request(path, options = {}, retry = true) {
  const headers = {
    Accept: 'application/json',
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...options.headers,
  }

  const token = options.authToken || getStoredAccessToken()
  if (token && options.auth !== false) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })
  const payload = await parseJson(response)

  if (response.status === 401 && payload?.code === 'TOKEN_EXPIRED' && retry) {
    const originalError = makeApiError(response, payload, 'Authentication failed.')
    const refreshToken = getStoredRefreshToken()

    if (!refreshToken) {
      clearAuthTokens()
      throw originalError
    }

    try {
      const refreshPayload = await request('/auth/refresh', {
        method: 'POST',
        authToken: refreshToken,
      }, false)
      const newAccessToken = refreshPayload?.data?.newAccessToken

      if (!newAccessToken) {
        clearAuthTokens()
        throw originalError
      }

      setAccessToken(newAccessToken)
      return request(path, options, false)
    } catch (error) {
      clearAuthTokens()
      throw error || originalError
    }
  }

  if (!response.ok || payload?.success === false) {
    throw makeApiError(response, payload)
  }

  return payload
}

export const apiClient = {
  get: (path, options) => request(path, { ...options, method: 'GET' }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
  patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
  delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
}

export { API_BASE_URL }
