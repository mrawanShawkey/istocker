import { apiClient } from './apiClient'

export const recommendationsService = {
  async getRecommendations() {
    const response = await apiClient.get('/recommendations')
    return response.data
  },
}
