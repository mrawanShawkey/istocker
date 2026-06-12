// src/__tests__/useAuth.test.jsx
// Integration tests for the useAuth hook.
// We render a tiny test component that exposes the hook's return values
// and action buttons — then assert the side-effects.

import { describe, it, expect } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { userStorage } from '../services/storageService'
import { renderWithProviders } from '../tests/renderWithProviders'

// ── tiny helpers that exercise the hook ──────────────────────────

function LocationDisplay() {
  const loc = useLocation()
  return <div data-testid="location">{loc.pathname}</div>
}

function TestSignIn({ email, password }) {
  const { signIn } = useAuth()
  return (
    <>
      <LocationDisplay />
      <button onClick={() => signIn(email, password)}>signIn</button>
    </>
  )
}

function TestRegister({ userData }) {
  const { register } = useAuth()
  return (
    <>
      <LocationDisplay />
      <button onClick={() => register(userData)}>register</button>
    </>
  )
}

function TestSignOut() {
  const { signOut, user } = useAuth()
  return (
    <>
      <LocationDisplay />
      <div data-testid="user">{user ? user.email : 'no-user'}</div>
      <button onClick={signOut}>signOut</button>
    </>
  )
}

// A fake home / onboarding page so router doesn't 404
const HomePage       = () => <div>Home</div>
const OnboardingPage = () => <div>Onboarding</div>
const SignInPage     = () => <div>Sign In</div>

// ── signIn ────────────────────────────────────────────────────────
describe('useAuth — signIn', () => {
  it('navigates to / when credentials are correct', async () => {
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })

    renderWithProviders(
      <Routes>
        <Route path="/signin" element={<TestSignIn email="mona@test.com" password="Secret@8" />} />
        <Route path="/"       element={<HomePage />} />
      </Routes>,
      { initialEntries: ['/signin'] }
    )

    fireEvent.click(screen.getByText('signIn'))
    await waitFor(() => {
      expect(screen.getByText('Home')).toBeInTheDocument()
    })
  })

  it('shows an error toast and does NOT navigate when credentials are wrong', async () => {
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })

    renderWithProviders(
      <Routes>
        <Route path="/signin" element={<TestSignIn email="mona@test.com" password="wrong" />} />
        <Route path="/"       element={<HomePage />} />
      </Routes>,
      { initialEntries: ['/signin'] }
    )

    fireEvent.click(screen.getByText('signIn'))
    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument()
    })
    // Still on /signin
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
  })
})

// ── register ──────────────────────────────────────────────────────
describe('useAuth — register', () => {
  it('navigates to /onboarding after register is called', async () => {
    const userData = { firstName: 'Mona', email: 'mona@test.com', password: 'Secret@8' }

    renderWithProviders(
      <Routes>
        <Route path="/signin"     element={<TestRegister userData={userData} />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
      </Routes>,
      { initialEntries: ['/signin'] }
    )

    fireEvent.click(screen.getByText('register'))
    await waitFor(() => {
      expect(screen.getByText('Onboarding')).toBeInTheDocument()
    })
  })
})

// ── signOut ───────────────────────────────────────────────────────
describe('useAuth — signOut', () => {
  it('clears the user and navigates to /signin', async () => {
    const storedUser = { email: 'mona@test.com', password: 'Secret@8' }

    renderWithProviders(
      <Routes>
        <Route path="/"       element={<TestSignOut />} />
        <Route path="/signin" element={<SignInPage />} />
      </Routes>,
      { initialEntries: ['/'], userOverride: storedUser }
    )

    // User is logged in
    expect(screen.getByTestId('user').textContent).toBe('mona@test.com')

    fireEvent.click(screen.getByText('signOut'))

    await waitFor(() => {
      expect(screen.getByText('Sign In')).toBeInTheDocument()
    })
  })

  it('removes the user from localStorage on sign-out', async () => {
    const storedUser = { email: 'mona@test.com', password: 'Secret@8' }

    renderWithProviders(
      <Routes>
        <Route path="/"       element={<TestSignOut />} />
        <Route path="/signin" element={<SignInPage />} />
      </Routes>,
      { initialEntries: ['/'], userOverride: storedUser }
    )

    fireEvent.click(screen.getByText('signOut'))

    await waitFor(() => screen.getByText('Sign In'))
    expect(userStorage.get()).toBeNull()
  })
})

// ── user state reflected in hook ──────────────────────────────────
describe('useAuth — user state', () => {
  it('exposes the stored user when one exists', () => {
    const storedUser = { email: 'mona@test.com' }

    renderWithProviders(
      <Routes>
        <Route path="/" element={<TestSignOut />} />
      </Routes>,
      { initialEntries: ['/'], userOverride: storedUser }
    )

    expect(screen.getByTestId('user').textContent).toBe('mona@test.com')
  })

  it('exposes null when no user is stored', () => {
    renderWithProviders(
      <Routes>
        <Route path="/" element={<TestSignOut />} />
      </Routes>,
      { initialEntries: ['/'] }
    )

    expect(screen.getByTestId('user').textContent).toBe('no-user')
  })
})
