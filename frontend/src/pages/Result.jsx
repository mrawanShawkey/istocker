import '../styles/result.css'
import { useState }     from 'react'
import { useNavigate }  from 'react-router-dom'
import { useApp }       from '../context/AppContext'
import { useLang }      from '../hooks/useLang'
import StockCard        from '../components/result/StockCard'
import RiskMetric       from '../components/result/RiskMetric'
import { RECOMMENDATIONS } from '../constants/data'
import { RISK_LABEL_AR, RISK_DESC, RISK_AI_TEXT, DEFAULT_RESULT, NEXT_STEPS } from '../constants/riskContent'

// Tooltip range data matching screenshot exactly
const CAPACITY_RANGES = {
  en: [
    { range:'0 → 30',   label:'Low financial capacity for risk'    },
    { range:'31 → 60',  label:'Moderate financial capacity'        },
    { range:'61 → 100', label:'High financial capacity'            },
  ],
  ar: [
    { range:'0 → 30',   label:'قدرة مالية منخفضة على المخاطرة'    },
    { range:'31 → 60',  label:'قدرة مالية معتدلة'                  },
    { range:'61 → 100', label:'قدرة مالية عالية'                   },
  ],
}
const TOLERANCE_RANGES = {
  en: [
    { range:'0 → 30',   label:'Conservative investor'  },
    { range:'31 → 60',  label:'Moderate investor'      },
    { range:'61 → 100', label:'Aggressive investor'    },
  ],
  ar: [
    { range:'0 → 30',   label:'مستثمر محافظ'           },
    { range:'31 → 60',  label:'مستثمر معتدل'           },
    { range:'61 → 100', label:'مستثمر قوي'             },
  ],
}
const LEVEL_RANGES = {
  en: [
    { range:'0 → 30',   label:'Low Risk Profile'       },
    { range:'31 → 50',  label:'Moderately Conservative'},
    { range:'51 → 70',  label:'Balanced Investor'      },
    { range:'71 → 85',  label:'Growth Investor'        },
    { range:'86 → 100', label:'Aggressive Investor'    },
  ],
  ar: [
    { range:'0 → 30',   label:'ملف مخاطر منخفض'        },
    { range:'31 → 50',  label:'محافظ إلى حد ما'        },
    { range:'51 → 70',  label:'مستثمر متوازن'          },
    { range:'71 → 85',  label:'مستثمر للنمو'           },
    { range:'86 → 100', label:'مستثمر قوي'             },
  ],
}


function normalizeResult(rawResult) {
  return {
    ...rawResult,
    label: rawResult.label || rawResult.riskCategory,
    labelAr: rawResult.riskCategoryAr,
    riskCapacity: rawResult.riskCapacity ?? rawResult.riskCapacityScore,
    riskTolerance: rawResult.riskTolerance ?? rawResult.riskToleranceScore,
    riskLevel: rawResult.riskLevel ?? rawResult.totalRiskScore,
    description: rawResult.description,
    descriptionAr: rawResult.descriptionAr,
    categoryScoreRange: rawResult.categoryScoreRange,
  }
}

function getResultDescription(result, label, lang) {
  if (lang === 'ar' && result.descriptionAr) return result.descriptionAr
  if (result.description) return result.description

  const fallback = RISK_DESC[label] || RISK_DESC['Conservative Investor']
  return fallback[lang] || fallback.en
}

function getResultAiText(label, lang) {
  const fallback = RISK_AI_TEXT[label] || RISK_AI_TEXT['Conservative Investor']
  return fallback[lang] || fallback.en
}

export default function Result() {
  const navigate = useNavigate()
  const { quizResult } = useApp()
  const { t, isAr, lang } = useLang()
  const [spin, setSpin] = useState(false)
  const [key,  setKey]  = useState(0)

  const result   = normalizeResult(quizResult || DEFAULT_RESULT)
  const label    = result.label || DEFAULT_RESULT.label
  const desc     = getResultDescription(result, label, lang)
  const aiText   = getResultAiText(label, lang)
  const recs     = RECOMMENDATIONS[label] || RECOMMENDATIONS['Conservative Investor']
  const steps    = isAr ? NEXT_STEPS.ar : NEXT_STEPS.en
  const now      = new Date().toLocaleDateString(isAr ? 'ar-EG' : 'en-GB')
  const labelDisp = isAr ? (result.labelAr || RISK_LABEL_AR[label] || label) : label

  function refresh() {
    setSpin(true); setTimeout(() => { setSpin(false); setKey(k=>k+1) }, 700)
  }

  return (
    <div className="result-wrap">

      {/* ── Risk Hero ── */}
      <div className="risk-hero">
        <h2>{t('Risk Profile', 'ملف تعريف المخاطر')}</h2>
        <div className="risk-badge">{labelDisp}</div>
        <p className="risk-hero-desc">{desc}</p>

        <div className="risk-metrics">
          <RiskMetric
            label={t('Risk Capacity', 'القدرة على المخاطرة')}
            value={result.riskCapacity}
            tooltip={isAr ? CAPACITY_RANGES.ar : CAPACITY_RANGES.en}
          />
          <RiskMetric
            label={t('Risk Tolerance', 'تحمل المخاطر')}
            value={result.riskTolerance}
            tooltip={isAr ? TOLERANCE_RANGES.ar : TOLERANCE_RANGES.en}
          />
          <RiskMetric
            label={t('Risk Level', 'مستوى المخاطر')}
            value={result.riskLevel}
            tooltip={isAr ? LEVEL_RANGES.ar : LEVEL_RANGES.en}
          />
        </div>
        <p className="risk-ai">{aiText}</p>
      </div>

      {/* ── Recommended Stocks ── */}
      <div className="rec-section">
        <div className="rec-section-head">
          <h2>{t('Recommended Stocks', 'الأسهم الموصى بها')}</h2>
          <button className={`refresh-btn${spin?' spinning':''}`} onClick={refresh}>
            <span className="refresh-spin">🔄</span> {t('Refresh Data', 'تحديث البيانات')}
          </button>
        </div>
        <p className="rec-sub">{t('Based on your answers, here are 3 stocks that match your profile','بناءً على إجاباتك، إليك 3 أسهم تتناسب مع ملفك')}</p>
        <div className="stock-grid" key={key}>
          {recs.map(s => <StockCard key={s.code} stock={s} />)}
        </div>
        <p className="updated-at">"{t('Last Updated','آخر تحديث')}: {now}"</p>
      </div>

      <button className="retest-btn" onClick={() => navigate('/quiz')}>{t('RETEST','إعادة الاختبار')}</button>

      {/* ── Security Alerts ── */}
      <div className="alerts-box">
        <div className="alerts-title">{t('🔴 SECURITY ALERTS & SAFETY BARRIERS','🔴 تنبيهات أمنية وحواجز أمان')}</div>
        <div className="alerts-grid">
          <div className="alert-card">
            <h4>{t('EMERGENCY FUNDS','صناديق الطوارئ')}</h4>
            <p>{t("Never invest money you'll need in the next six months. Only invest surplus funds.","لا تستثمر الأموال التي ستحتاجها في الأشهر الستة القادمة.")}</p>
          </div>
          <div className="alert-card">
            <h4>{t("DON'T CHASE THE COLOR GREEN",'لا تطارد اللون الأخضر')}</h4>
            <p>{t("Buying stocks at their peak due to FOMO is the fastest way to lose money.","شراء الأسهم في ذروتها هو أسرع طريقة للخسارة.")}</p>
          </div>
        </div>
      </div>

      {/* ── Next Steps ── */}
      <div className="next-steps">
        <h2>{t('NEXT STEPS :','الخطوات التالية:')}</h2>
        <ol className="steps-list">
          {steps.map((s,i) => <li key={i}>{s}</li>)}
        </ol>
      </div>
    </div>
  )
}
