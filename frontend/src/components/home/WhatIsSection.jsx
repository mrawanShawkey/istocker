// S  — "What is iStocker?" section only.
import { useLang }     from '../../hooks/useLang'
import IllustrationBox from './IllustrationBox'

export default function WhatIsSection() {
  const { t } = useLang()
  return (
    <div id="what-is" className="info-section">
      <div className="info-row">
        <div className="info-text">
          <h2>{t('What is iStocker?', 'ما هو iStocker؟')}</h2>
          <p>{t(
            'iStocker is an intelligent stock recommendation platform designed to help investors make better decisions. Instead of randomly choosing stocks, our system analyzes your preferences, financial goals, and risk tolerance to suggest investment opportunities that suit you.',
            'iStocker هو منصة توصيات أسهم ذكية مصممة لمساعدة المستثمرين على اتخاذ قرارات أفضل. بدلاً من اختيار الأسهم عشوائياً، يحلل نظامنا تفضيلاتك وأهدافك المالية ومستوى مخاطرتك لاقتراح الفرص الاستثمارية المناسبة لك.'
          )}</p>
        </div>
        {/*
          TO ADD IMAGE: replace the line below with:
          <IllustrationBox imgSrc="/assets/what-is.png" altText="What is iStocker" />
        */}
        <IllustrationBox imgSrc="/assets/what-is.png" altText="What is iStocker" />
      </div>
    </div>
  )
}
