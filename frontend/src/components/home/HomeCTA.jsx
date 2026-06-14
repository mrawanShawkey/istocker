// S — bottom CTA only. Matches screenshot: "Ready to Start..." + Take Quiz button.
import { useNavigate } from 'react-router-dom'
import { useLang }     from '../../hooks/useLang'
import { ROUTES }      from '../../constants/routes'

export default function HomeCTA() {
  const { t }    = useLang()
  const navigate = useNavigate()
  return (
    <div className="home-cta">
      <h2>{t('Ready to Start Your Investment Journey?', 'هل أنت مستعد لبدء رحلتك الاستثمارية؟')}</h2>
      <p>{t(
        'Take our quick questionnaire to receive personalized stock recommendations.',
        'أجب على استبياننا السريع للحصول على توصيات أسهم مخصصة.'
      )}</p>
      <button className="btn btn-primary" onClick={() => navigate(ROUTES.QUIZ)}>
        {t('Take Quiz', 'ابدأ الاختبار')}
      </button>
    </div>
  )
}
