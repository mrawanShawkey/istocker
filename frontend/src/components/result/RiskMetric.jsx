// S — renders one risk metric box with a hover tooltip showing score ranges.
// O — tooltip content passed as prop; no changes needed to add new tooltips.
import { useState } from 'react'

export default function RiskMetric({ label, value, tooltip }) {
  const [show, setShow] = useState(false)

  return (
    <div className="metric">
      <div className="metric-label">
        {label}
        <span
          className="metric-tip"
          onMouseEnter={() => setShow(true)}
          onMouseLeave={() => setShow(false)}
          onFocus={() => setShow(true)}
          onBlur={() => setShow(false)}
          tabIndex={0}
          aria-label="More info"
        >
          ?
          {show && tooltip && (
            <div className="metric-tooltip" onClick={e => e.stopPropagation()}>
              {tooltip.map((row, i) => (
                <div key={i} className="metric-tooltip-row">
                  <span className="metric-tooltip-range">{row.range}</span>
                  <span className="metric-tooltip-label">{row.label}</span>
                </div>
              ))}
            </div>
          )}
        </span>
      </div>
      <div className="metric-val">{value}</div>
    </div>
  )
}
