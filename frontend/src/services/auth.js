/**
 * Authentication service for user login/logout
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

const authApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Login user
 */
export const login = async (username, password) => {
  const response = await authApi.post('/auth/login', { username, password })

  if (response.data.token) {
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
  }

  return response.data
}

/**
 * Register new user
 */
export const register = async (username, email, password, role = 'normal') => {
  const response = await authApi.post('/auth/register', {
    username,
    email,
    password,
    role
  })
  return response.data
}

/**
 * Logout user
 */
export const logout = async () => {
  try {
    await authApi.post('/auth/logout')
  } finally {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

/**
 * Get current user info
 */
export const getCurrentUser = async () => {
  const response = await authApi.get('/auth/me')
  return response.data.user
}

/**
 * Check if user is logged in
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('token')
}

/**
 * Get stored user data
 */
export const getStoredUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

/**
 * Check if user is admin
 */
export const isAdmin = () => {
  const user = getStoredUser()
  return user && user.role === 'admin'
}

// Admin APIs

/**
 * Get all users (admin only)
 */
export const getAllUsers = async () => {
  const response = await authApi.get('/auth/users')
  return response.data
}

/**
 * Update user (admin only)
 */
export const updateUser = async (userId, updates) => {
  const response = await authApi.put(`/auth/users/${userId}`, updates)
  return response.data
}

/**
 * Delete user (admin only)
 */
export const deleteUser = async (userId) => {
  const response = await authApi.delete(`/auth/users/${userId}`)
  return response.data
}

// History APIs

/**
 * Get my history
 */
export const getMyHistory = async (page = 1, perPage = 50) => {
  const response = await authApi.get(`/history/my-history?page=${page}&per_page=${perPage}`)
  return response.data
}

/**
 * Get my statistics
 */
export const getMyStats = async () => {
  const response = await authApi.get('/history/stats')
  return response.data
}

/**
 * Get user history (admin only)
 */
export const getUserHistory = async (userId, page = 1, perPage = 50) => {
  const response = await authApi.get(`/history/users/${userId}/history?page=${page}&per_page=${perPage}`)
  return response.data
}

/**
 * Get all history (admin only)
 */
export const getAllHistory = async (page = 1, perPage = 50) => {
  const response = await authApi.get(`/history/all-history?page=${page}&per_page=${perPage}`)
  return response.data
}

export default authApi
