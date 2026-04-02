/**
 * Health plans service
 */
import authApi from './auth'

/**
 * Create new health plan
 */
export const createPlan = async (planData) => {
  const response = await authApi.post('/plans/create', planData)
  return response.data
}

/**
 * Get all my plans
 */
export const getMyPlans = async () => {
  const response = await authApi.get('/plans/my-plans')
  return response.data
}

/**
 * Get primary (active) plan
 */
export const getPrimaryPlan = async () => {
  const response = await authApi.get('/plans/primary')
  return response.data
}

/**
 * Set plan as primary
 */
export const setPrimaryPlan = async (planId) => {
  const response = await authApi.put(`/plans/${planId}/set-primary`)
  return response.data
}

/**
 * Update plan progress
 */
export const updateProgress = async (planId, progress) => {
  const response = await authApi.put(`/plans/${planId}/progress`, { progress })
  return response.data
}

/**
 * Add checkpoint to plan
 */
export const addCheckpoint = async (planId, checkpointData) => {
  const response = await authApi.post(`/plans/${planId}/checkpoint`, { checkpoint_data: checkpointData })
  return response.data
}

/**
 * Get specific plan
 */
export const getPlan = async (planId) => {
  const response = await authApi.get(`/plans/${planId}`)
  return response.data
}

/**
 * Update plan
 */
export const updatePlan = async (planId, updates) => {
  const response = await authApi.put(`/plans/${planId}`, updates)
  return response.data
}

/**
 * Delete plan
 */
export const deletePlan = async (planId) => {
  const response = await authApi.delete(`/plans/${planId}`)
  return response.data
}

export default {
  createPlan,
  getMyPlans,
  getPrimaryPlan,
  setPrimaryPlan,
  updateProgress,
  addCheckpoint,
  getPlan,
  updatePlan,
  deletePlan
}
