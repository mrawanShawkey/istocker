import { apiClient } from './apiClient'

const QUESTION_TYPES = new Set(['Registration', 'Questionnaire'])

function assertQuestionType(type) {
  if (!QUESTION_TYPES.has(type)) {
    throw new Error('Question type must be Registration or Questionnaire.')
  }
}

export const questionsService = {
  async getQuestions(type) {
    assertQuestionType(type)
    const response = await apiClient.get(`/questions/?type=${encodeURIComponent(type)}`)
    return response.data
  },

  async getRegistrationQuestions() {
    return questionsService.getQuestions('Registration')
  },

  async getQuestionnaireQuestions() {
    return questionsService.getQuestions('Questionnaire')
  },

  async saveResponses(type, responses) {
    assertQuestionType(type)
    const response = await apiClient.post(
      `/questions/responses?type=${encodeURIComponent(type)}`,
      { responses }
    )
    return response.data
  },

  async saveRegistrationResponses(responses) {
    return questionsService.saveResponses('Registration', responses)
  },

  async saveQuestionnaireResponses(responses) {
    return questionsService.saveResponses('Questionnaire', responses)
  },

  async updateResponses(modifications) {
    const response = await apiClient.patch('/questions/responses', { modifications })
    return response.data
  },
}
