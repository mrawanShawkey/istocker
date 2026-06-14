// S  — "Why use iStocker?" + "Don't Trust AI" section only.
// O  — ai-robot image injected via src prop; no logic changes needed.
import { useLang } from '../../hooks/useLang'

export default function WhySection() {
  const { t } = useLang()
  return (
    <div className="info-section">
      <div className="why-card">
        <h2>{t('Why use iStocker?', 'لماذا تستخدم iStocker؟')}</h2>
        <ul>
          <li>{t('Personalized stock recommendations',          'توصيات أسهم مخصصة')}</li>
          <li>{t('Based on data-driven analysis',               'مبنية على تحليل بيانات')}</li>
          <li>{t('Simple and easy for beginners',               'بسيطة وسهلة للمبتدئين')}</li>
          <li>{t('Helps reduce risky investment decisions',     'تساعد على تقليل قرارات الاستثمار المحفوفة بالمخاطر')}</li>
        </ul>
      </div>

      <div className="transparency-card">
        <div className="transparency-text">
          <h2>{t("Don't Trust AI Yet? See How It Works", 'لا تثق بالذكاء الاصطناعي بعد؟ انظر كيف يعمل')}</h2>
          <p>{t(
            "We believe transparency builds trust. That's why iStocker not only predicts stocks, but also explains how those predictions are made. Here's a simple overview of the process:",
            'نؤمن بأن الشفافية تبني الثقة. لهذا لا يكتفي iStocker بالتنبؤ بالأسهم بل يشرح أيضاً كيف تُصنع هذه التنبؤات.'
          )}</p>
          <p style={{ fontWeight: 600, marginBottom: '.4rem' }}>{t('Steps:', 'الخطوات:')}</p>
          <ol>
            <li>{t('User Assessment',          'تقييم المستخدم')}</li>
            <li>{t('Risk Profile Calculation', 'حساب ملف المخاطرة')}</li>
            <li>{t('Stock Matching',           'مطابقة الأسهم')}</li>
            <li>{t('AI Return Prediction',     'توقع العائد بالذكاء الاصطناعي')}</li>
            <li>{t('Top Opportunities Selected','اختيار أفضل الفرص')}</li>
          </ol>
        </div>

        {/* AI Robot image — fitted to the card */}
        <div className="ai-illus-box">
          <img
            src="/assets/ai-robot.png"
            alt="AI Robot"
            className="ai-illus-img"
          />
        </div>
      </div>
    </div>
  )
}
