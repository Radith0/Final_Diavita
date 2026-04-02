/**
 * Analysis results service
 */
import authApi from './auth'

/**
 * Save analysis result
 */
export const saveAnalysisResult = async (resultData) => {
  const response = await authApi.post('/results/save', resultData)
  return response.data
}

/**
 * Get all my results
 */
export const getMyResults = async (page = 1, perPage = 10) => {
  const response = await authApi.get(`/results/my-results?page=${page}&per_page=${perPage}`)
  return response.data
}

/**
 * Get latest result
 */
export const getLatestResult = async () => {
  const response = await authApi.get('/results/latest')
  return response.data
}

/**
 * Get results summary with trends
 */
export const getResultsSummary = async () => {
  const response = await authApi.get('/results/summary')
  return response.data
}

/**
 * Get specific result by ID
 */
export const getResultById = async (resultId) => {
  const response = await authApi.get(`/results/${resultId}`)
  return response.data
}

/**
 * Delete result
 */
export const deleteResult = async (resultId) => {
  const response = await authApi.delete(`/results/${resultId}`)
  return response.data
}

export default {
  saveAnalysisResult,
  getMyResults,
  getLatestResult,
  getResultsSummary,
  getResultById,
  deleteResult
}
