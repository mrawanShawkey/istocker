// S  — "Model Accuracy" section only.
// O  — Open/Closed: chart is injected via ChartPlaceholder — adding a real chart
//      never requires changing this component.
import { useLang }        from '../../hooks/useLang'
import ChartPlaceholder   from './ChartPlaceholder'

function GaugeSvg() {
  return (
    <div className="gauge-box">
      <svg className="gauge-svg" viewBox="0 0 140 80">
        <path d="M10 75 A60 60 0 0 1 130 75" fill="none" stroke="#1e1e2e" strokeWidth="14" strokeLinecap="round"/>
        <path d="M10 75 A60 60 0 0 1 47 22"  fill="none" stroke="#ef4444" strokeWidth="14" strokeLinecap="round"/>
        <path d="M47 22 A60 60 0 0 1 93 22"  fill="none" stroke="#f59e0b" strokeWidth="14" strokeLinecap="round"/>
        <path d="M93 22 A60 60 0 0 1 130 75" fill="none" stroke="#10b981" strokeWidth="14" strokeLinecap="round"/>
        <line x1="70" y1="75" x2="95" y2="28" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
        <circle cx="70" cy="75" r="4" fill="white"/>
      </svg>
      <div className="gauge-labels"><span>Low</span><span>Middle</span><span>High</span></div>
    </div>
  )
}

export default function ModelAccuracySection({ chartImgSrc, chartComponent }) {
  const { t } = useLang()
  return (
    <div className="model-section">
      <h2>{t('Model Accuracy', 'دقة النموذج')}</h2>

      {/* To add the chart image: pass imgSrc="/assets/your-chart.png" to this component */}
      <ChartPlaceholder imgSrc={chartImgSrc} chartComponent={chartComponent} />

      <div className="model-how-card">
        <div>
          <h3>{t('How the Recommendation Model Works?', 'كيف يعمل نموذج التوصيات؟')}</h3>
          <p>{t(
            'Our recommendation engine uses a structured decision model that evaluates multiple factors, including:',
            'يستخدم محرك التوصيات لدينا نموذج قرار منظم يقيّم عدة عوامل، منها:'
          )}</p>
          <ul>
            <li>{t('Risk tolerance',     'تحمل المخاطر')}</li>
            <li>{t('Investment horizon', 'أفق الاستثمار')}</li>
            <li>{t('Financial goals',    'الأهداف المالية')}</li>
            <li>{t('Market trends',      'اتجاهات السوق')}</li>
          </ul>
          <p style={{ marginTop: '.75rem' }}>{t(
            'Based on these inputs, the system identifies stocks that align with your investment profile.',
            'بناءً على هذه المدخلات، يحدد النظام الأسهم المتوافقة مع ملفك الاستثماري.'
          )}</p>
        </div>
        <GaugeSvg />
      </div>
    </div>
  )
}
