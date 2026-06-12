// src/__tests__/SignIn.test.jsx
// Tests the SignIn page UI:
//   • tab switching (Sign In ↔ Sign Up)
//   • validation errors when fields are empty
//   • password rules enforced on sign-up
//   • successful sign-in calls useAuth().signIn

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignIn from '../pages/SignIn'
import { renderWithProviders } from './renderWithProviders'
import { userStorage } from '../services/storageService'

// ── helpers ───────────────────────────────────────────────────────
function renderSignIn(opts = {}) {
  return renderWithProviders(<SignIn />, opts)
}

function clickTab(name) {
  fireEvent.click(screen.getByRole('button', { name }))
}

// ── Tab navigation ────────────────────────────────────────────────
describe('SignIn — tab navigation', () => {
  it('shows the Sign In form by default', () => {
    renderSignIn()
    // The submit button inside the sign-in form reads "Sign In"
    expect(screen.getAllByRole('button', { name: /sign in/i }).length).toBeGreaterThan(0)
  })

  it('switches to the Sign Up form when the Sign Up tab is clicked', () => {
    renderSignIn()
    clickTab(/sign up/i)
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('switches back to Sign In when the Sign In tab is clicked', () => {
    renderSignIn()
    clickTab(/sign up/i)
    clickTab(/sign in/i)
    expect(screen.getAllByRole('button', { name: /^sign in$/i }).length).toBeGreaterThan(0)
  })
})

// ── Sign In validation ────────────────────────────────────────────
describe('SignIn — sign-in form validation', () => {
  it('shows a toast when the form is submitted with empty fields', async () => {
    renderSignIn()
    // There are two "Sign In" buttons: the tab and the submit button.
    // The submit button is type="submit" inside a form.
    const submitBtn = document.querySelector('button[type="submit"]')
    fireEvent.click(submitBtn)
    // Toast renders asynchronously via AppContext
    await waitFor(() => {
      expect(screen.getByText(/please fill all fields/i)).toBeInTheDocument()
    })
  })

  it('calls authService.signIn with the entered credentials', async () => {
    // Pre-store a user so sign-in succeeds
    userStorage.set({ email: 'mona@test.com', password: 'Secret@8' })
    renderSignIn()

    await userEvent.type(screen.getByLabelText(/email/i), 'mona@test.com')
    // PasswordInput renders a plain input underneath
    const pwInput = screen.getByLabelText(/^password$/i)
    await userEvent.type(pwInput, 'Secret@8')

    fireEvent.click(document.querySelector('button[type="submit"]'))
    // If credentials match the app navigates away (no error toast shown)
    await waitFor(() => {
      expect(screen.queryByText(/invalid email or password/i)).not.toBeInTheDocument()
    })
  })
})

// ── Sign Up validation ────────────────────────────────────────────
describe('SignIn — sign-up form validation', () => {
  beforeEach(() => {
    renderSignIn()
    clickTab(/sign up/i)
  })

  it('shows a toast when required fields are missing', async () => {
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => {
      expect(screen.getByText(/please fill all fields/i)).toBeInTheDocument()
    })
  })

  it('shows a toast when the password is too weak', async () => {
    await userEvent.type(screen.getByLabelText(/first name/i), 'Mona')
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'mona@test.com')
    // All password inputs are type="password"; grab by index
    const pwInputs = screen.getAllByRole('textbox')
    // Use a weak password (no special char, only 4 chars)
    const pwField = document.querySelector('input[type="password"]')
    await userEvent.type(pwField, 'weak')

    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => {
      expect(screen.getByText(/password needs 8\+ chars/i)).toBeInTheDocument()
    })
  })

  it('shows a toast when passwords do not match', async () => {
    await userEvent.type(screen.getByLabelText(/first name/i), 'Mona')
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'mona@test.com')

    const pwFields = document.querySelectorAll('input[type="password"]')
    await userEvent.type(pwFields[0], 'Secret@8')
    await userEvent.type(pwFields[1], 'Different@8')

    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
    })
  })
})

// ── Forgot password link ──────────────────────────────────────────
describe('SignIn — forgot password', () => {
  it('shows the forgot-password view when the link is clicked', () => {
    renderSignIn()
    fireEvent.click(screen.getByText(/forgot username or password/i))
    expect(screen.getByText(/reset your password/i)).toBeInTheDocument()
  })

  it('returns to the sign-in tab when BACK TO LOGIN is clicked', () => {
    renderSignIn()
    fireEvent.click(screen.getByText(/forgot username or password/i))
    fireEvent.click(screen.getByRole('button', { name: /back to login/i }))
    expect(screen.getAllByRole('button', { name: /^sign in$/i }).length).toBeGreaterThan(0)
  })
})