import '../styles/settings.css'
import { useState }   from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp }    from '../context/AppContext'
import { useLang }   from '../hooks/useLang'
import { useToast }  from '../hooks/useToast'
import { ROUTES }    from '../constants/routes'
import { RISK_LABEL_AR, DEFAULT_RESULT, ONBOARDING_GROUPS } from '../constants/riskContent'

export default function Profile() {
  const navigate = useNavigate()
  const { user, setUser, quizResult } = useApp()
  const { t, isAr } = useLang()
  const toast  = useToast()
  const result = quizResult || DEFAULT_RESULT
  const fp     = user?.financialProfile || {}
  const [sel, setSel] = useState({ incomeSituation:fp.incomeSituation||'no_income', savingsDuration:fp.savingsDuration||'4_6', financialObligations:fp.financialObligations||'moderate', investedMoneyAccess:fp.investedMoneyAccess||'unlikely' })

  const initials = u => ((u?.firstName||'A')[0]+(u?.lastName||'A')[0]).toUpperCase()

  function save() { setUser({...user,financialProfile:sel}); toast(t('Changes saved!','تم حفظ التغييرات!'),'success') }

  return (
    <div className="profile-wrap">
      <div className="profile-hero">
        <div className="profile-hero-left">
          <div className="profile-avatar">{initials(user)}</div>
          <div>
            <div className="profile-name">{user?.firstName} {user?.lastName}</div>
            <div className="profile-meta">{t('Member since April 2026 · Profile last updated today','عضو منذ أبريل 2026 · آخر تحديث اليوم')}</div>
            <div className="profile-badge">{isAr?(RISK_LABEL_AR[result.label]||result.label):result.label}</div>
          </div>
        </div>
        <button className="profile-gear" onClick={()=>navigate(ROUTES.SETTINGS)}>⚙️</button>
      </div>

      <div className="risk-overview-card">
        <div className="risk-overview-title">📊 {t('Risk Overview','نظرة عامة على المخاطر')}</div>
        <div className="risk-metrics-row">
          {[[t('Risk Capacity','القدرة على المخاطرة'),result.riskCapacity],[t('Risk Tolerance','تحمل المخاطر'),result.riskTolerance],[t('Risk Level','مستوى المخاطر'),result.riskLevel]].map(([l,v])=>(
            <div key={l} className="risk-metric"><div className="risk-metric-label">{l}</div><div className="risk-metric-val">{v}</div></div>
          ))}
        </div>
        <div className="risk-overview-actions">
          <button className="risk-view-link" onClick={()=>navigate(ROUTES.RESULT)}>{t('View my Recommendations','عرض توصياتي')} ↗</button>
          <button className="risk-retake-link" onClick={()=>navigate(ROUTES.QUIZ)}>{t('Retake Quiz','إعادة الاختبار')}</button>
        </div>
      </div>

      <div className="edit-answers-card">
        <div className="edit-answers-head">
          <h3>✏️ {t('Edit Your Answers','تعديل إجاباتك')}</h3>
          <p>{t('Update your initial answers to tailor your investment profile','تحديث إجاباتك الأولية لتخصيص ملفك الاستثماري')}</p>
        </div>
        {ONBOARDING_GROUPS.map(g=>(
          <div key={g.key} className="answer-row-group">
            <div className="answer-section-title">{isAr?g.ar:g.en}</div>
            <div className="answer-inline-row">
              <div className="answer-question">{isAr?g.ar:g.en}</div>
              <select className="s-select s-select-inline" value={sel[g.key]} onChange={e=>setSel(s=>({...s,[g.key]:e.target.value}))}>
                {g.opts.map(([val,en,ar])=><option key={val} value={val}>{isAr?ar:en}</option>)}
              </select>
            </div>
          </div>
        ))}
      </div>
      <div className="profile-save-row">
        <button className="btn btn-primary" onClick={save}>{t('Save Changes','حفظ التغييرات')}</button>
      </div>
    </div>
  )
}
