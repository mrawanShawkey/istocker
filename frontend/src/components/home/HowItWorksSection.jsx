// S  — "How it works?" section. Composes StepBlocks; owns no state.
// O  — Adding a new step = one StepBlock line. Existing steps never change.
// I  — Each StepBlock receives only what it needs: number, imgSrc, children.
// D  — Depends on IllustrationBox abstraction, not on any specific image.

import { useLang }     from '../../hooks/useLang'
import StepBlock       from './StepBlock'
import IllustrationBox from './IllustrationBox'

export default function HowItWorksSection() {
  const { t } = useLang()
  return (
    <div className="steps-section">
      <h2 className="steps-section-title">{t('How it works?', 'كيف يعمل؟')}</h2>

      {/* Step 1 — text left, image right */}
      <StepBlock stepNumber={1} imgSrc="/assets/step1.png" altText="Sign up step" flip={false}>
        <p>{t(
          'When you sign up for the first time, iStocker asks you a few quick questions about your investment background and financial goals. These initial questions help us start building your investment profile.',
          'عند تسجيلك لأول مرة، يطرح عليك iStocker بعض الأسئلة السريعة حول خلفيتك الاستثمارية وأهدافك المالية. هذه الأسئلة الأولية تساعدنا في بناء ملفك الاستثماري.'
        )}</p>
      </StepBlock>

      {/* Step 2 — QUIZ word left, text right (no image for step 2) */}
      <div className="step-row">
        <div className="quiz-word">QUIZ</div>
        <div className="step-body">
          <div className="step-number-label">Step 2 :</div>
          <p>{t(
            'After logging in, you will take a short assessment inside the platform. This assessment works like a small Q/A designed to understand:',
            'بعد تسجيل الدخول، ستجري تقييماً قصيراً داخل المنصة. هذا التقييم مصمم لفهم:'
          )}</p>
          <ul>
            <li>{t('Your financial goals',              'أهدافك المالية')}</li>
            <li>{t('Your investment experience',        'خبرتك الاستثمارية')}</li>
            <li>{t('Your reaction to market risks',     'تعاملك مع مخاطر السوق')}</li>
            <li>{t('Your preferred investment horizon', 'أفق استثمارك المفضل')}</li>
          </ul>
          <p style={{ marginTop: '.6rem' }}>{t(
            'Your answers help the system understand your investor behavior.',
            'تساعد إجاباتك النظام على فهم سلوكك كمستثمر.'
          )}</p>
        </div>
      </div>

      {/* Step 3 — text left, image right */}
      <StepBlock stepNumber={3} imgSrc="/assets/step3.png" altText="Risk score calculation" flip={false}>
        <p>{t(
          'Based on your answers, the system calculates a Risk Score that represents your investment profile. This score places you in one of three investor categories:',
          'بناءً على إجاباتك، يحسب النظام درجة المخاطرة التي تمثل ملفك الاستثماري. تضعك هذه الدرجة في إحدى فئات المستثمرين الثلاث:'
        )}</p>
        <ul>
          <li>{t('Conservative – prefers lower risk and stable returns',         'محافظ – يفضل المخاطرة المنخفضة والعوائد الثابتة')}</li>
          <li>{t('Moderate – balanced approach between risk and growth',          'معتدل – نهج متوازن بين المخاطرة والنمو')}</li>
          <li>{t('Aggressive – willing to accept higher risk for higher returns', 'قوي – يقبل مخاطرة أعلى مقابل عوائد محتملة أكبر')}</li>
        </ul>
      </StepBlock>

      {/* Step 4 — image left, text right */}
      <div className="step-row step-row--flip">
        <IllustrationBox imgSrc="/assets/step4.png" altText="Stock database" />
        <div className="step-body">
          <div className="step-number-label">Step 4 :</div>
          <p>{t(
            'Our database already contains stocks that are categorized according to their risk level. Once your risk category is determined, the system automatically retrieves stocks that match your investment profile. For example, a Moderate investor will receive stocks that are labeled as Moderate risk.',
            'قاعدة بياناتنا تحتوي بالفعل على أسهم مصنفة وفق مستوى مخاطرتها. بمجرد تحديد فئة مخاطرتك، يسترجع النظام تلقائياً الأسهم المتوافقة مع ملفك الاستثماري.'
          )}</p>
        </div>
      </div>

      {/* Step 5 — text left, image right */}
      <StepBlock stepNumber={5} imgSrc="/assets/step5.png" altText="AI prediction model" flip={false}>
        <p>{t(
          'After the matching process, the selected stocks are passed to our AI prediction model. The model analyzes historical financial data and market patterns to predict the expected return of each stock over the next year.',
          'بعد عملية المطابقة، تُمرَّر الأسهم المختارة إلى نموذج التنبؤ بالذكاء الاصطناعي. يحلل النموذج البيانات المالية التاريخية وأنماط السوق للتنبؤ بالعائد المتوقع لكل سهم خلال العام القادم.'
        )}</p>
      </StepBlock>

      {/* Step 6 — image left, text right */}
      <div className="step-row step-row--flip">
        <IllustrationBox imgSrc="/assets/step6.png" altText="Top stocks selected" />
        <div className="step-body">
          <div className="step-number-label">Step 6 :</div>
          <p>{t(
            'Finally, the system compares the predicted returns and selects the top stocks with the highest expected return. These stocks are then presented to you as your personalized investment suggestions.',
            'أخيراً، يقارن النظام العوائد المتوقعة ويختار أفضل الأسهم ذات العائد المتوقع الأعلى. ثم تُعرض عليك هذه الأسهم كاقتراحاتك الاستثمارية المخصصة.'
          )}</p>
        </div>
      </div>
    </div>
  )
}
