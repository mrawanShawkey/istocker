// S — renders the scrollable list of lessons for the active level.
// I — receives only lessons, selectedId, onSelect.
import { useLang } from '../../hooks/useLang'

export default function LessonList({ lessons, selectedId, onSelect }) {
  const { isAr } = useLang()
  return (
    <div className="lesson-list">
      {lessons.map((lesson, i) => {
        const content  = isAr ? lesson.ar : lesson.en
        const isActive = lesson.id === selectedId
        return (
          <button
            key={lesson.id}
            className={`lesson-row${isActive ? ' lesson-row--active' : ''}`}
            onClick={() => onSelect(lesson)}
          >
            <div className="lesson-num">{i + 1}</div>
            <div className="lesson-info">
              <div className="lesson-title">{content.title}</div>
              <div className="lesson-dur">{lesson.duration}</div>
            </div>
            <div className="lesson-arrow">{isActive ? '▶' : '›'}</div>
          </button>
        )
      })}
    </div>
  )
}
