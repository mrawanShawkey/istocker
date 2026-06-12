// src/__tests__/PrivateRoute.test.jsx
// Tests that PrivateRoute:
//   • renders children when a user is logged in
//   • redirects to /signin when there is no user

import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'
import PrivateRoute from '../components/layout/PrivateRoute'
import { renderWithProviders } from '../tests/renderWithProviders'

// A tiny stand-in for a protected page
const SecretPage = () => <div>Secret content</div>
const SignInPage  = () => <div>Sign In Page</div>

// Helper: render the route tree with an optional logged-in user
function setup({ userOverride = null, initialRoute = '/secret' } = {}) {
  return renderWithProviders(
    <Routes>
      <Route path="/signin" element={<SignInPage />} />
      <Route
        path="/secret"
        element={
          <PrivateRoute>
            <SecretPage />
          </PrivateRoute>
        }
      />
    </Routes>,
    { initialEntries: [initialRoute], userOverride }
  )
}

describe('PrivateRoute', () => {
  it('renders children when a user is logged in', () => {
    setup({ userOverride: { email: 'mona@test.com' } })
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })

  it('does NOT render children when no user is logged in', () => {
    setup({ userOverride: null })
    expect(screen.queryByText('Secret content')).not.toBeInTheDocument()
  })

  it('redirects to /signin when there is no user', () => {
    setup({ userOverride: null })
    expect(screen.getByText('Sign In Page')).toBeInTheDocument()
  })

  it('does NOT redirect when a user is logged in', () => {
    setup({ userOverride: { email: 'mona@test.com' } })
    expect(screen.queryByText('Sign In Page')).not.toBeInTheDocument()
  })
})