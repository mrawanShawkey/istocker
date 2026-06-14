// S — Quiz page: orchestrates question flow, enforces answer-before-continue.
import '../styles/quiz.css'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp }      from '../context/AppContext'
import { useLang }     from '../hooks/useLang'
import { useToast }    from '../hooks/useToast'
import { ROUTES }      from '../constants/routes'
import { questionsService } from '../services/questionsService'
import QuizProgress    from '../components/quiz/QuizProgress'
import QuizOptions     from '../components/quiz/QuizOptions'
import QuizSlider      from '../components/quiz/QuizSlider'

function sortOptions(options = []) {
  return [...options].sort((a, b) => a.optionNumber - b.optionNumber)
}

function getOptionText(option, isAr) {
  return isAr ? (option.optionTextAr || option.optionText) : option.optionText
}

function getQuestionText(question, isAr) {
  return isAr ? (question.questionTextAr || question.questionText) : question.questionText
}

function buildSliderQuestion(question, isAr) {
  const options = sortOptions(question.options)
  const labels = options.map(option => getOptionText(option, isAr)).filter(Boolean)
  const first = labels[0] || ''
  const middle = labels[Math.floor(labels.length / 2)] || first
  const last = labels[labels.length - 1] || middle

  return {
    l: first,
    m: middle,
    r: last,
  }
}

function optionIdToSliderIndex(question, optionId) {
  if (optionId == null) return null
  const options = sortOptions(question.options)
  const optionIndex = options.findIndex(option => option.optionId === optionId)
  if (optionIndex < 0) return null
  if (options.length <= 1) return 0
  return Math.round((optionIndex / (options.length - 1)) * 4)
}

function sliderIndexToOptionId(question, sliderIndex) {
  const options = sortOptions(question.options)
  if (options.length === 0) return null
  if (options.length === 1) return options[0].optionId
  const optionIndex = Math.round((sliderIndex / 4) * (options.length - 1))
  return options[optionIndex]?.optionId ?? null
}

function normalizeRiskProfile(profile) {
  return {
    ...profile,
    label: profile.riskCategory,
    riskCapacity: profile.riskCapacityScore,
    riskTolerance: profile.riskToleranceScore,
    riskLevel: profile.totalRiskScore,
  }
}

export default function Quiz() {
  const navigate = useNavigate()
  const { setQuizResult } = useApp()
  const { t, isAr } = useLang()
  const toast = useToast()
  const [cur, setCur] = useState(0)
  const [answers, setAnswers] = useState({})
  const [questions, setQuestions] = useState([])
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
      const data = await questionsService.getQuestionnaireQuestions()
      setQuestions(data || [])
      setAnswers({})
      setCur(0)
    } catch (err) {
      setError(err.message || t('Unable to load quiz questions', 'تعذر تحميل أسئلة الاختبار'))
    } finally {
      setLoading(false)
    }
  }

  const total = questions.length
  const q = questions[cur]
  const selectedOptionId = q ? answers[q.questionId] : null
  const hasAnswer = selectedOptionId != null

  function setAns(questionId, optionId) {
    setAnswers(prev => ({ ...prev, [questionId]: optionId }))
  }

  async function submitQuestionnaire() {
    if (questions.some(question => answers[question.questionId] == null)) {
      toast(t('Please answer all questions to continue', 'يرجى الإجابة على جميع الأسئلة للمتابعة'), 'error')
      return
    }

    const responses = questions.map(question => ({
      questionId: question.questionId,
      optionId: answers[question.questionId],
    }))

    setSubmitting(true)
    try {
      const result = await questionsService.saveQuestionnaireResponses(responses)
      setQuizResult(normalizeRiskProfile(result))
      navigate(ROUTES.RESULT)
    } catch (err) {
      toast(err.message || t('Unable to save quiz answers', 'تعذر حفظ إجابات الاختبار'), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  function goNext() {
    if (!q) return

    // Block navigation if no answer selected
    if (!hasAnswer) {
      toast(t('Please answer this question to continue', 'يرجى الإجابة على هذا السؤال للمتابعة'), 'error')
      return
    }

    if (cur === total - 1) {
      submitQuestionnaire()
    } else {
      setCur(c => c + 1)
    }
  }

  if (loading) {
    return (
      <div className="quiz-page">
        <div className="quiz-card">
          <p className="quiz-question">{t('Loading questions...', 'جارٍ تحميل الأسئلة...')}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="quiz-page">
        <div className="quiz-card">
          <p className="quiz-question">{error}</p>
          <button className="btn btn-primary" type="button" onClick={loadQuestions}>
            {t('Retry', 'إعادة المحاولة')}
          </button>
        </div>
      </div>
    )
  }

  if (!q) {
    return (
      <div className="quiz-page">
        <div className="quiz-card">
          <p className="quiz-question">{t('No questions available yet', 'لا توجد أسئلة متاحة حالياً')}</p>
        </div>
      </div>
    )
  }

  const options = sortOptions(q.options)
  const isScale = q.questionFormat === 'Scale'
  const selectedOptionIndex = options.findIndex(option => option.optionId === selectedOptionId)
  const sliderValue = optionIdToSliderIndex(q, selectedOptionId)

  return (
    <div className="quiz-page">
      <QuizProgress current={cur} total={total} />

      <div className="quiz-card">
        <p className="quiz-question">{getQuestionText(q, isAr)}</p>

        {!isScale
          ? (
            <QuizOptions
              options={options.map(option => getOptionText(option, isAr))}
              selected={selectedOptionIndex}
              onSelect={index => setAns(q.questionId, options[index]?.optionId)}
            />
          )
          : (
            <QuizSlider
              question={buildSliderQuestion(q, isAr)}
              value={sliderValue}
              onChange={index => setAns(q.questionId, sliderIndexToOptionId(q, index))}
            />
          )
        }

        {/* Unanswered warning */}
        {!hasAnswer && cur > 0 && (
          <p className="quiz-unanswered-hint">
            {t('⚠ Select an answer to continue', '⚠ اختر إجابة للمتابعة')}
          </p>
        )}
      </div>

      <div className="quiz-nav">
        <button
          className="btn btn-ghost"
          onClick={() => setCur(c => c - 1)}
          disabled={cur === 0 || submitting}
        >
          {t('← Back', '→ السابق')}
        </button>
        <button
          className={`btn btn-primary${!hasAnswer ? ' btn--disabled' : ''}`}
          onClick={goNext}
          disabled={submitting}
        >
          {submitting
            ? t('Saving...', 'جارٍ الحفظ...')
            : cur === total - 1 ? t('Finish', 'إنهاء') : t('Next →', 'التالي ←')
          }
        </button>
      </div>
    </div>
  )
}
