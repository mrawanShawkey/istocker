// S — shows selected stock name, description, and predicted price below the chart.
// I — receives only selected company object and onClear callback.
import { useLang }     from '../../hooks/useLang'
import PredictedPrice  from './PredictedPrice'

export default function StockInfoPanel({ selected, onClear }) {
  const { t, isAr } = useLang()
  if (!selected) return null

  const name = isAr ? selected.nameAr : selected.name
  const desc = isAr ? (selected.descAr || selected.desc) : selected.desc

  return (
    <div className="stock-info-panel">
      <div className="stock-info-top">
        <div className="stock-info-left">
          <span className="stock-info-label">{t('Selected Stock :', 'السهم المختار :')}</span>
          {selected.code && <span className="stock-info-code">{selected.code}</span>}
          <span className="stock-info-name">{name}</span>
        </div>
        <button className="stock-info-clear-btn" onClick={onClear}>
          {t('View Index', 'عرض المؤشر')}
        </button>
      </div>

      {/* Predicted price row in panel */}
      {selected.predictedPrice && (
        <div className="stock-info-predicted">
          <PredictedPrice
            currentPrice={selected.price}
            predictedPrice={selected.predictedPrice}
          />
        </div>
      )}

      {desc && (
        <p className="stock-info-desc">
          <span className="stock-info-desc-label">{t('Description:', 'الوصف:')}</span>{' '}{desc}
        </p>
      )}
    </div>
  )
}
