import '../styles/auth.css'
import { useEffect, useState } from 'react'
import { useLang }  from '../hooks/useLang'
import { useAuth }  from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { useNavigate } from 'react-router-dom'
import { ROUTES }   from '../constants/routes'
import { questionsService } from '../services/questionsService'
import AuthBars from '../components/ui/AuthBars'

export default function Onboarding() {
  const { completeOnboarding } = useAuth()
  const { t, isAr } = useLang()
  const toast  = useToast()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [sel, setSel] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  async function loadQuestions() {
    setLoading(true)
    setError('')
    try {
      const data = await questionsService.getRegistrationQuestions()
      setQuestions(data || [])
      setSel({})
    } catch (err) {
      if (err.status === 401) {
        navigate(ROUTES.SIGNIN)
        return
      }
      setError(err.message || t('Unable to load onboarding questions', 'تعذر تحميل أسئلة التسجيل'))
    } finally {
      setLoading(false)
    }
  }

  async function submit() {
    if (questions.length === 0) {
      toast(t('No questions available yet', 'لا توجد أسئلة متاحة حالياً'), 'error')
      return
    }

    if (questions.some(q => !sel[q.questionId])) {
      toast(t('Please answer all questions','يرجى الإجابة على جميع الأسئلة'),'error')
      return
    }

    const responses = questions.map(q => ({
      questionId: q.questionId,
      optionId: sel[q.questionId],
    }))

    setSubmitting(true)
    try {
      await completeOnboarding(responses)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <AuthBars />
      <div className="auth-box" style={{maxWidth:'560px',overflowY:'auto',maxHeight:'90vh'}}>
        <h2 style={{fontFamily:'var(--font-en)',fontSize:'1.5rem',fontWeight:800,marginBottom:'.35rem'}}>{t('One Last Step!','خطوة أخيرة!')}</h2>
        <p style={{color:'var(--gray)',fontSize:'.85rem',marginBottom:'1.5rem'}}>{t("Tell us about your financial situation to personalise your experience.","أخبرنا عن وضعك المالي لنخصص تجربتك.")}</p>

        {loading && (
          <p style={{color:'var(--gray)',fontSize:'.9rem',marginBottom:'1.5rem'}}>
            {t('Loading questions...', 'جارٍ تحميل الأسئلة...')}
          </p>
        )}

        {!loading && error && (
          <div style={{marginBottom:'1.5rem'}}>
            <p style={{color:'var(--danger)',fontSize:'.9rem',marginBottom:'.75rem'}}>{error}</p>
            <button className="btn btn-ghost" type="button" onClick={loadQuestions}>
              {t('Retry', 'إعادة المحاولة')}
            </button>
          </div>
        )}

        {!loading && !error && questions.map(q => (
          <div key={q.questionId} style={{marginBottom:'1.25rem'}}>
            <div style={{fontSize:'.8rem',fontWeight:700,color:'var(--white)',marginBottom:'.5rem'}}>
              {isAr ? (q.questionTextAr || q.questionText) : q.questionText}
            </div>
            <div className="chip-group">
              {(q.options || []).map(opt => (
                <button
                  key={opt.optionId}
                  className={`chip${sel[q.questionId]===opt.optionId?' on':''}`}
                  type="button"
                  onClick={() => setSel(s => ({ ...s, [q.questionId]: opt.optionId }))}
                >
                  {isAr ? (opt.optionTextAr || opt.optionText) : opt.optionText}
                </button>
              ))}
            </div>
          </div>
        ))}

        <button
          className="btn btn-primary"
          style={{width:'100%',marginTop:'.5rem'}}
          onClick={submit}
          disabled={loading || !!error || submitting}
        >
          {submitting ? t('Saving...', 'جارٍ الحفظ...') : t('Get Started →','ابدأ الآن ←')}
        </button>
      </div>
    </div>
  )
}
