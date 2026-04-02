import { describe, it, expect, beforeEach } from 'vitest'
import { isAuthenticated, getStoredUser, isAdmin } from '../services/auth'

describe('isAuthenticated', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns false when no token exists', () => {
    expect(isAuthenticated()).toBe(false)
  })

  it('returns true when token exists', () => {
    localStorage.setItem('token', 'some-jwt-token')
    expect(isAuthenticated()).toBe(true)
  })
})

describe('getStoredUser', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns null when no user stored', () => {
    expect(getStoredUser()).toBeNull()
  })

  it('returns parsed user object when stored', () => {
    const user = { id: 1, username: 'test', role: 'normal' }
    localStorage.setItem('user', JSON.stringify(user))
    expect(getStoredUser()).toEqual(user)
  })
})

describe('isAdmin', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns false when no user stored', () => {
    expect(isAdmin()).toBeFalsy()
  })

  it('returns false for normal user', () => {
    localStorage.setItem('user', JSON.stringify({ id: 1, role: 'normal' }))
    expect(isAdmin()).toBe(false)
  })

  it('returns true for admin user', () => {
    localStorage.setItem('user', JSON.stringify({ id: 1, role: 'admin' }))
    expect(isAdmin()).toBe(true)
  })
})
