// S — renders quiz progress bar only.
import { useLang } from '../../hooks/useLang'

export default function QuizProgress({ current, total }) {
  const { t, isAr } = useLang()
  const pct = Math.round(((current + 1) / total) * 100)
  return (
    <div className="quiz-progress-wrap">
      <div className="quiz-meta">
        <span>{isAr ? `سؤال ${current+1} من ${total}` : `Question ${current+1} of ${total}`}</span>
        <span>{isAr ? `مكتمل بنسبة ${pct}%` : `${pct}% Complete`}</span>
      </div>
      <div className="quiz-prog-bar">
        <div className="quiz-prog-fill" style={{ width:`${pct}%` }} />
      </div>
    </div>
  )
}
