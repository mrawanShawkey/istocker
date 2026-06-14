// S — renders the 3 level tabs only.
// I — receives only levels, activeId, onSelect.
import { useLang } from '../../hooks/useLang'

export default function LevelTabs({ levels, activeId, onSelect }) {
  const { isAr } = useLang()
  return (
    <div className="edu-tabs">
      {levels.map(level => (
        <button
          key={level.id}
          className={`edu-tab${activeId === level.id ? ' edu-tab--active' : ''}`}
          onClick={() => onSelect(level.id)}
        >
          <span className="edu-tab-icon" aria-hidden="true">{level.icon}</span>
          <span>{isAr ? level.ar : level.en}</span>
        </button>
      ))}
    </div>
  )
}
