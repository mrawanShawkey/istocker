// S — Single Responsibility: all authentication HTTP calls live here.
// Pages call authService.signIn() — they don't know endpoint details.
import {
  apiClient,
  clearAuthTokens,
  getStoredRefreshToken,
  setAuthTokens,
} from './apiClient'

export const authService = {
  async login(credentials) {
    const response = await apiClient.post('/auth/login', credentials, { auth: false })
    setAuthTokens(response.data)
    return response
  },

  async signIn(email, password) {
    const response = await authService.login({ email, password })
    const profile = await authService.getProfile()
    return { ...profile, tokens: response.data }
  },

  async register(userData) {
    const response = await apiClient.post('/auth/register', {
      firstName: userData.firstName,
      lastName: userData.lastName,
      email: userData.email,
      password: userData.password,
    }, { auth: false })
    setAuthTokens(response.data)
    return response.data
  },

  async getProfile() {
    const response = await apiClient.get('/user/profile')
    return response.data
  },

  async changeEmail({ oldEmail, password, newEmail }) {
    const response = await apiClient.patch('/auth/change-email', {
      oldEmail,
      password,
      newEmail,
    })
    return response.data
  },

  async changePassword({ oldPassword, newPassword, rePassword }) {
    const response = await apiClient.patch('/auth/change-password', {
      oldPassword,
      newPassword,
      rePassword,
    })
    return response.data
  },

  async forgotPassword(email) {
    return apiClient.post('/auth/forgot-password', { email }, { auth: false })
  },

  async resetPassword({ code, email, newPassword, rePassword }) {
    return apiClient.post('/auth/reset-password', {
      code,
      email,
      newPassword,
      rePassword,
    }, { auth: false })
  },

  async logout() {
    const refreshToken = getStoredRefreshToken()

    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refreshToken })
      }
    } finally {
      clearAuthTokens()
    }
  },

  async deleteAccount() {
    const refreshToken = getStoredRefreshToken()

    await apiClient.delete('/auth/delete-account', {
      headers: refreshToken ? { 'Refresh-Token': refreshToken } : {},
    })

    clearAuthTokens()
  },

  validatePassword(pw) {
    return {
      hasLength: pw.length >= 8,
      hasSpecial: /[\d!@#$%^&*]/.test(pw),
    }
  },
}
