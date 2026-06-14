// S — Single Responsibility: shows selected stock name, sector badge, and description below the chart.
// I — receives only the selected company object and onClear callback.
import { useLang } from '../../hooks/useLang'

export default function StockInfoBar({ company, onClear }) {
  const { t, isAr } = useLang()

  if (!company) return null

  const name  = isAr ? company.nameAr : company.name
  const desc  = isAr ? company.descAr  : company.desc

  return (
    <div className="stock-info-bar">
      <div className="stock-info-top">
        <div className="stock-info-left">
          <span className="stock-info-label">{t('Selected Stock :', 'السهم المختار :')}</span>
          <span className="stock-info-name">{name}</span>
          <span className="stock-info-code">{company.code}</span>
          <span className="stock-info-sector">{company.sector}</span>
        </div>
        <button className="stock-info-clear" onClick={onClear}>
          {t('View Index', 'عرض المؤشر')}
        </button>
      </div>
      {desc && (
        <p className="stock-info-desc">
          <span className="stock-info-desc-label">{t('Description:', 'الوصف:')}</span>
          {' '}{desc}
        </p>
      )}
    </div>
  )
}
