/**
 * API service for diabetes detection backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Analyze retinal image only
 */
export const analyzeRetinal = async (imageFile) => {
  const formData = new FormData()
  formData.append('image', imageFile)

  const response = await api.post('/retinal/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

  return response.data
}

/**
 * Predict risk from lifestyle data only
 */
export const predictLifestyle = async (lifestyleData) => {
  const response = await api.post('/lifestyle/predict', lifestyleData)
  return response.data
}

/**
 * Complete end-to-end analysis (recommended)
 */
export const analyzeComplete = async (imageFile, lifestyleData) => {
  const formData = new FormData()
  formData.append('image', imageFile)
  formData.append('lifestyle_data', JSON.stringify(lifestyleData))

  const response = await api.post('/advice/complete-analysis', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

  return response.data
}

/**
 * Generate advice from existing risk data
 */
export const generateAdvice = async (riskData) => {
  const response = await api.post('/advice/generate', riskData)
  return response.data
}

/**
 * Create what-if simulations
 */
export const createSimulations = async (simulationData) => {
  const response = await api.post('/simulation/create', simulationData)
  return response.data
}

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await axios.get('http://localhost:5000/health')
  return response.data
}

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    throw error
  }
)

export default api
