import { apiClient } from './apiClient'

export const userService = {
  async getSettings() {
    const response = await apiClient.get('/user/settings')
    return response.data
  },

  async updateProfile(modifications) {
    const response = await apiClient.patch('/user/profile', { modifications })
    return response.data
  },

  async updatePreferences(modifications) {
    const response = await apiClient.patch('/user/preferences', { modifications })
    return response.data
  },
}
