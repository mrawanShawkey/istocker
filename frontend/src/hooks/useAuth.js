// S — Single Responsibility: authentication actions for components.
// Components call useAuth().signIn() — not authService directly.
// This is the anti-corruption layer between UI and service.
import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp }      from '../context/AppContext'
import { authService } from '../services/authService'
import { questionsService } from '../services/questionsService'
import { useToast }    from './useToast'
import { ROUTES }      from '../constants/routes'

export function useAuth() {
  const { user, setUser, draft, setDraft } = useApp()
  const navigate = useNavigate()
  const toast    = useToast()

  const signIn = useCallback(async (email, password) => {
    try {
      const result = await authService.signIn(email, password)
      setUser(result)
      navigate(ROUTES.HOME)
      return true
    } catch (error) {
      toast(error.message || 'Invalid email or password', 'error')
      return false
    }
  }, [setUser, navigate, toast])

  const register = useCallback(async (userData) => {
    try {
      await authService.register(userData)

      const safeDraft = {
        firstName: userData.firstName,
        lastName: userData.lastName,
        email: userData.email,
      }

      try {
        const profile = await authService.getProfile()
        setUser(profile)
      } catch {
        setUser(safeDraft)
      }

      setDraft(safeDraft)
      navigate(ROUTES.ONBOARDING)
      return true
    } catch (error) {
      toast(error.message || 'Unable to create account', 'error')
      return false
    }
  }, [setDraft, setUser, navigate, toast])

  const completeOnboarding = useCallback(async (responses) => {
    try {
      await questionsService.saveRegistrationResponses(responses)

      try {
        const profile = await authService.getProfile()
        setUser(profile)
      } catch {
        setUser(user || draft || null)
      }

      setDraft(null)
      navigate(ROUTES.HOME)
      return true
    } catch (error) {
      toast(error.message || 'Unable to save onboarding answers', 'error')
      return false
    }
  }, [user, draft, setUser, setDraft, navigate, toast])

  const signOut = useCallback(async () => {
    try {
      await authService.logout()
    } finally {
      setUser(null)
      navigate(ROUTES.SIGNIN)
    }
  }, [setUser, navigate])

  return { user, signIn, register, completeOnboarding, signOut }
}
