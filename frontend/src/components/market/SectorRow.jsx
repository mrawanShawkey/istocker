// S — renders one sector performance row.
import { useLang } from '../../hooks/useLang'

export default function SectorRow({ sector }) {
  const { isAr } = useLang()
  return (
    <div className="sector-row">
      <div>
        <div className="sector-name">{isAr ? sector.nameAr : sector.name}</div>
        <div className="sector-stocks">Key stocks: {sector.stocks.join(', ')}</div>
      </div>
      <div className={`sector-pct ${sector.pct >= 0 ? 'up' : 'down'}`}>
        {sector.pct > 0 ? '+' : ''}{sector.pct.toFixed(2)}%
      </div>
    </div>
  )
}
