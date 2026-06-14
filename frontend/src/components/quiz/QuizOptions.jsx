// S — renders multiple-choice options only.
export default function QuizOptions({ options, selected, onSelect }) {
  return (
    <div className="opts">
      {options.map((opt, i) => (
        <button key={i} className={`opt${selected===i?' sel':''}`} onClick={() => onSelect(i)}>{opt}</button>
      ))}
    </div>
  )
}
