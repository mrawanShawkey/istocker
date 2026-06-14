// S — renders one ticker card with predicted price badge.
// I — receives only ticker, selected, onSelect.
import { useLang }       from '../../hooks/useLang'
import PredictedPrice    from './PredictedPrice'

export default function TickerCard({ ticker, selected, onSelect }) {
  const { isAr } = useLang()

  return (
    <div
      className={`ticker-card${selected ? ' selected' : ''}`}
      onClick={() => onSelect(ticker)}
    >
      {/* Company name */}
      <div className="ticker-name">{isAr ? ticker.nameAr : ticker.name}</div>

      {/* Current price — large */}
      <div className="ticker-price">{ticker.price.toFixed(3)}</div>

      {/* Change row with trend arrow icon */}
      <div className={`ticker-chg-row ticker-chg-row--${ticker.dir}`}>
        <span className="ticker-trend-icon" aria-hidden="true">
          {ticker.dir === 'up' ? '↗' : '↘'}
        </span>
        <span className={`ticker-chg ${ticker.dir}`}>
          {ticker.dir === 'up' ? '+' : ''}{ticker.chg.toFixed(2)}{' '}
          ({ticker.dir === 'up' ? '+' : ''}{ticker.pct.toFixed(2)}%)
        </span>
      </div>

      {/* Predicted price — matches screenshot box style */}
      <PredictedPrice
        currentPrice={ticker.price}
        predictedPrice={ticker.predictedPrice}
      />
    </div>
  )
}
