// S — Single Responsibility: language helpers only.
// Components import this hook — they never read lang from context directly.
import { useApp } from '../context/AppContext'

export function useLang() {
  const { lang, setLang } = useApp()
  const isAr = lang === 'ar'

  /** Translate: t('English text', 'نص عربي') */
  const t = (en, ar) => (isAr ? ar : en)

  /** Switch between en and ar */
  const switchLang = () => setLang(isAr ? 'en' : 'ar')

  return { lang, setLang, switchLang, t, isAr }
}
