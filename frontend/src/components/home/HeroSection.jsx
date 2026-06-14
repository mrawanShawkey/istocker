// S — Hero banner only. Matches screenshot: centered title + subtitle, no extra elements.
import { useLang } from '../../hooks/useLang'

export default function HeroSection() {
  const { t } = useLang()
  return (
    <section className="hero-section">
      <div className="hero-glow" aria-hidden="true" />
      <div className="hero-inner--centered">
        <h1 className="hero-title">
          {t('Your Journey to', 'رحلتك نحو')}<br />
          <em className="hero-title-accent">{t('Smart Investing', 'الاستثمار الذكي')}</em>
        </h1>
        <p className="hero-subtitle">
          {t(
            "No experience needed. We'll help you understand the stock market, calculate your investment profile, and recommend the perfect stocks for you.",
            'لا خبرة مطلوبة. سنساعدك على فهم سوق الأسهم وحساب ملفك الاستثماري والتوصية بأفضل الأسهم لك.'
          )}
        </p>
      </div>
    </section>
  )
}
