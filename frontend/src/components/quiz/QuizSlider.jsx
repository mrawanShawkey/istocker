// S — renders a slider that snaps to exactly 5 labelled positions.
// The 5 labels are built from the question's l / m / r anchors.
// Scoring value stored is 0-4 (step index), matching opts scoring.

import { useLang } from '../../hooks/useLang'

// Build the 5 specific labels for each question from its anchors
function buildSteps(l, m, r) {
  return [
    { index: 0, label: l },
    { index: 1, label: `${l} / ${m}` },
    { index: 2, label: m },
    { index: 3, label: `${m} / ${r}` },
    { index: 4, label: r },
  ]
}

export default function QuizSlider({ question, value, onChange }) {
  const { isAr } = useLang()

  // Arabic: visually reverse left/right
  const steps = isAr
    ? buildSteps(question.r, question.m, question.l)
    : buildSteps(question.l, question.m, question.r)

  const current = value ?? null  // null means untouched
  const pct     = current === null ? 0 : (current / 4) * 100

  function handleChange(e) {
    // Snap to nearest of 5 positions: 0, 1, 2, 3, 4
    const raw     = Number(e.target.value)          // 0-100
    const snapped = Math.round((raw / 100) * 4)     // 0-4
    onChange(snapped)
  }

  return (
    <div className="quiz-slider-wrap">

      {/* The real draggable slider — snaps to 5 positions */}
      <div className="quiz-slider-track-area">
        <input
          type="range"
          className="quiz-slider"
          min="0"
          max="100"
          step="25"                          /* 5 stops: 0, 25, 50, 75, 100 */
          value={current === null ? 0 : current * 25}
          style={{ '--pct': `${pct}%` }}
          onChange={handleChange}
          onMouseDown={() => { if (current === null) onChange(2) }} /* default to middle on first touch */
          onTouchStart={() => { if (current === null) onChange(2) }}
        />
        {/* 5 tick marks below the track */}
        <div className="quiz-slider-ticks">
          {steps.map((s) => (
            <div
              key={s.index}
              className={`quiz-tick${current === s.index ? ' quiz-tick--active' : ''}`}
              onClick={() => onChange(s.index)}
            />
          ))}
        </div>
      </div>

      {/* 5 labels below the ticks */}
      <div className="quiz-slider-labels">
        {steps.map((s) => (
          <span
            key={s.index}
            className={`quiz-slider-label${current === s.index ? ' quiz-slider-label--active' : ''}`}
            onClick={() => onChange(s.index)}
          >
            {s.label}
          </span>
        ))}
      </div>

      {/* Selected option highlight box */}
      {current !== null && (
        <div className="quiz-slider-selected">
          <span className="quiz-slider-selected-icon">✓</span>
          {steps[current]?.label}
        </div>
      )}
    </div>
  )
}
