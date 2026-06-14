// S — Single Responsibility: owns global app state and exposes setters.
// It does NOT contain business logic — that lives in services.
import { createContext, useContext, useState, useCallback } from 'react'
import { userStorage, langStorage, draftStorage, resultStorage } from '../services/storageService'
import { langService } from '../services/langService'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [user, setUserState]           = useState(() => userStorage.get())
  const [lang, setLangState]           = useState(() => langStorage.get())
  const [draft, setDraftState]         = useState(() => draftStorage.get())
  const [quizResult, setResultState]   = useState(() => resultStorage.get())
  const [toast, setToast]              = useState(null)

  // Apply lang side-effects on mount
  useState(() => langService.apply(lang))

  const setUser = useCallback((u) => {
    setUserState(u)
    u ? userStorage.set(u) : userStorage.remove()
  }, [])

  const setLang = useCallback((l) => {
    setLangState(l)
    langStorage.set(l)
    langService.apply(l)
  }, [])

  const setDraft = useCallback((d) => {
    setDraftState(d)
    d ? draftStorage.set(d) : draftStorage.remove()
  }, [])

  const setQuizResult = useCallback((r) => {
    setResultState(r)
    resultStorage.set(r)
  }, [])

  const showToast = useCallback((msg, type = 'success') => {
    setToast({ msg, type, id: Date.now() })
  }, [])

  return (
    <AppContext.Provider value={{
      user, setUser,
      lang, setLang,
      draft, setDraft,
      quizResult, setQuizResult,
      toast, showToast,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used inside <AppProvider>')
  return ctx
}
