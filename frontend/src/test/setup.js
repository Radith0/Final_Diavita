import '@testing-library/jest-dom'

// Polyfill IntersectionObserver for jsdom (needed by framer-motion)
class IntersectionObserver {
  constructor(callback) {
    this.callback = callback
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.IntersectionObserver = IntersectionObserver
