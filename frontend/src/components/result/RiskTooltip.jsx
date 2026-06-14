// S — hover tooltip for risk metric question marks.
// Shows the range table from the screenshot on hover.
import { useState } from 'react'
import { useLang }  from '../../hooks/useLang'

// Table rows for each metric type
const RANGES = {
  capacity: [
    { range: '0 → 30',   en: 'Low financial capacity for risk',  ar: 'قدرة مالية منخفضة على المخاطرة'  },
    { range: '31 → 60',  en: 'Moderate financial capacity',       ar: 'قدرة مالية معتدلة'                },
    { range: '61 → 100', en: 'High financial capacity',           ar: 'قدرة مالية عالية'                 },
  ],
  tolerance: [
    { range: '0 → 30',   en: 'Conservative investor',  ar: 'مستثمر محافظ'   },
    { range: '31 → 60',  en: 'Moderate investor',      ar: 'مستثمر معتدل'   },
    { range: '61 → 100', en: 'Aggressive investor',    ar: 'مستثمر قوي'     },
  ],
  level: [
    { range: '0 → 30',   en: 'Low Risk Profile',       ar: 'ملف مخاطرة منخفض'    },
    { range: '31 → 50',  en: 'Moderately Conservative',ar: 'محافظ إلى حد ما'      },
    { range: '51 → 70',  en: 'Balanced Investor',      ar: 'مستثمر متوازن'        },
    { range: '71 → 85',  en: 'Growth Investor',        ar: 'مستثمر للنمو'         },
    { range: '86 → 100', en: 'Aggressive Investor',    ar: 'مستثمر قوي'           },
  ],
}

export default function RiskTooltip({ metricKey }) {
  const { isAr } = useLang()
  const [open, setOpen] = useState(false)
  const rows = RANGES[metricKey] || []

  return (
    <span
      className="metric-tip-wrap"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onClick={() => setOpen(o => !o)}
    >
      <span className="metric-tip">?</span>
      {open && (
        <div className="metric-tooltip">
          <table className="metric-tooltip-table">
            <tbody>
              {rows.map(r => (
                <tr key={r.range}>
                  <td className="metric-tooltip-range">{r.range}</td>
                  <td className="metric-tooltip-text">{isAr ? r.ar : r.en}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </span>
  )
}
