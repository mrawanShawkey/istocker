import { describe, it, expect, beforeEach } from 'vitest'
import { authService } from '../frontend/istocker-react/src/services/authService'
import { userStorage } from '../frontend/istocker-react/src/services/storageService'

beforeEach(() => {
  userStorage.remove()
})

// ── signIn ───────────────────────────────────────────────────────
describe('authService — signIn', () => {
  it('returns the user when credentials are correct', () => {
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })
    const result = authService.signIn('mona@test.com', 'Secret@8')
    expect(result).not.toBeNull()
    expect(result.email).toBe('mona@test.com')
  })

  it('returns null when email is wrong', () => {
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })
    expect(authService.signIn('wrong@test.com', 'Secret@8')).toBeNull()
  })

  it('returns null when password is wrong', () => {
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })
    expect(authService.signIn('mona@test.com', 'wrongpass')).toBeNull()
  })

  it('returns null when no user is stored', () => {
    expect(authService.signIn('mona@test.com', 'Secret@8')).toBeNull()
  })
})

// ── register ─────────────────────────────────────────────────────
describe('authService — register', () => {
  it('stores and returns the user', () => {
    const user = { email: 'mona@test.com', password: 'Secret@8', firstName: 'Mona' }
    const result = authService.register(user)
    expect(result).toEqual(user)
    expect(userStorage.get()).toEqual(user)
  })
})

// ── validatePassword ─────────────────────────────────────────────
describe('authService — validatePassword', () => {
  it('passes a strong password', () => {
    const { hasLength, hasSpecial } = authService.validatePassword('Secret@8')
    expect(hasLength).toBe(true)
    expect(hasSpecial).toBe(true)
  })

  it('fails when password is too short', () => {
    expect(authService.validatePassword('Ab@1').hasLength).toBe(false)
  })

  it('fails when password has no special char or digit', () => {
    expect(authService.validatePassword('abcdefgh').hasSpecial).toBe(false)
  })
})