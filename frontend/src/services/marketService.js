import { apiClient } from './apiClient'

export const marketService = {
  async getMarketOverview() {
    const response = await apiClient.get('/market', { auth: false })
    return response.data
  },

  async getStockMarketData(ticker) {
    const normalizedTicker = String(ticker || '').trim()
    if (!normalizedTicker) {
      throw new Error('Ticker is required.')
    }

    const response = await apiClient.get(
      `/market/${encodeURIComponent(normalizedTicker)}`,
      { auth: false }
    )
    return response.data
  },
}
