// S  — Single Responsibility: owns the model accuracy chart slot only.
// O  — Open/Closed: pass `chartComponent` prop to inject a real chart later,
//      or pass `imgSrc` to drop in a screenshot — this component never needs editing.
// When nothing is passed → shows a styled empty placeholder with instructions.

export default function ChartPlaceholder({ chartComponent, imgSrc }) {
  if (chartComponent) return <div className="chart-placeholder">{chartComponent}</div>

  if (imgSrc) {
    return (
      <div className="chart-placeholder chart-placeholder--filled">
        <img src={imgSrc} alt="Model accuracy chart" className="chart-img" />
      </div>
    )
  }

  return (
    <div className="chart-placeholder chart-placeholder--empty">
      <div className="chart-ph-icon">📊</div>
      <div className="chart-ph-text">
        <strong>Model Accuracy Chart</strong>
        <span>Add your chart image here</span>
        <code>{'<ChartPlaceholder imgSrc="/assets/chart.png" />'}</code>
      </div>
    </div>
  )
}
