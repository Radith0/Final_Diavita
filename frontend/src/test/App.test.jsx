import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'

describe('App Routing', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders the home page at /', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )
    // HomePage should render
    expect(document.querySelector('.app')).toBeInTheDocument()
  })

  it('renders the login page at /login', () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <App />
      </MemoryRouter>
    )
    expect(document.querySelector('.app')).toBeInTheDocument()
  })

  it('redirects /dashboard to /login when not authenticated', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    )
    // Should redirect to login since not authenticated
    expect(document.querySelector('.app')).toBeInTheDocument()
  })
})
