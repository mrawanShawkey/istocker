// src/test/setup.js
// Runs before every test file.
// Extends expect with DOM matchers and wires up storage mocks.

import '@testing-library/jest-dom'

// ── localStorage / sessionStorage mock ──────────────────────────
// jsdom ships a partial implementation; this guarantees a clean
// in-memory store that is wiped between tests via afterEach.
const makeStorage = () => {
  let store = {}
  return {
    getItem: (k)    => store[k] ?? null,
    setItem: (k, v) => { store[k] = String(v) },
    removeItem: (k) => { delete store[k] },
    clear:      ()  => { store = {} },
    get length()    { return Object.keys(store).length },
    key: (i)        => Object.keys(store)[i] ?? null,
  }
}

Object.defineProperty(window, 'localStorage',   { value: makeStorage(), writable: true })
Object.defineProperty(window, 'sessionStorage', { value: makeStorage(), writable: true })

// Clear storage after every test so tests never bleed into each other
afterEach(() => {
  window.localStorage.clear()
  sessionStorage.clear()
})
