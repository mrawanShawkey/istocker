// S — Market page: composes market components. Zero business logic here.
import '../styles/market.css'
import { useState }      from 'react'
import { useLang }       from '../hooks/useLang'
import TickerSlider      from '../components/market/TickerSlider'
import MarketChart       from '../components/market/MarketChart'
import StockInfoPanel    from '../components/market/StockInfoPanel'
import MoverRow          from '../components/market/MoverRow'
import SectorRow         from '../components/market/SectorRow'
import EGX30Table        from '../components/market/EGX30Table'
import { INDEX_CHART }   from '../constants/chartData'
import { EGX30_COMPANIES, EGX30_CHARTS } from '../constants/egx30Data'
import { STATIC_MARKET } from '../constants/data'

export default function Market() {
  const { t, isAr } = useLang()
  const [selected, setSelected] = useState(null)

  // Merge static ticker cards into EGX30 list so slider has all 30
  // EGX30_COMPANIES is the source of truth; static tickers are already included
  const allCompanies = EGX30_COMPANIES

  const chartData  = selected ? (EGX30_CHARTS[selected.code] || INDEX_CHART) : INDEX_CHART
  const chartColor = selected ? (selected.dir === 'up' ? '#10b981' : '#ef4444') : '#10b981'
  const chartTitle = selected
    ? (isAr ? selected.nameAr : selected.name)
    : t('EGX 30 Today', 'مؤشر EGX 30 اليوم')
  const chartSub   = selected
    ? t("Today's Performance", 'الأداء اليوم')
    : t('Daily Performance', 'الأداء خلال اليوم')

  return (
    <div className="market-wrap">

      <div className="section-head">
        <h1>{t('Market ', 'نظرة عامة على ')}<em>{t('Overview', 'السوق')}</em></h1>
        <p>{t('Stay updated with real-time Egyptian market data', 'ابقَ على اطلاع دائم ببيانات السوق المصري')}</p>
      </div>

      {/* ── Scrollable ticker slider — all 30 EGX companies ── */}
      <TickerSlider
        companies={allCompanies}
        selectedCode={selected?.code || null}
        onSelect={setSelected}
      />

      {/* ── Chart ── */}
      <div className="chart-section">
        <div className="chart-header">
          <div className="chart-header-left">
            <h2>{chartTitle}</h2>
            <p>{chartSub}</p>
          </div>
        </div>
        <div className="chart-box">
          <MarketChart
            key={selected?.code || 'idx'}
            data={chartData}
            color={chartColor}
          />
        </div>
        <StockInfoPanel selected={selected} onClear={() => setSelected(null)} />
      </div>

      {/* ── EGX 30 table ── */}
      <div className="egx30-section-header">
        <h2>{t('EGX 30 — Daily Performance', 'EGX 30 — الأداء اليومي')}</h2>
        <p>{t('Click any company to view its intraday chart above', 'انقر على أي شركة لعرض مخطط أدائها اليومي أعلاه')}</p>
      </div>
      <EGX30Table
        companies={allCompanies}
        selectedCode={selected?.code || null}
        onSelect={setSelected}
      />

      {/* ── Bottom: movers + sectors ── */}
      <div className="two-col" style={{ marginTop:'2rem' }}>
        <div className="market-box">
          <div className="market-box-head">
            <h3>{t('Top Movers','أفضل الشركات')}</h3>
            <p>{t('Most active today','أكثر الأسهم نشاطاً')}</p>
          </div>
          {STATIC_MARKET.movers.map(m => <MoverRow key={m.code} mover={m} />)}
        </div>
        <div className="market-box">
          <div className="market-box-head">
            <h3>{t('Sector Performance','أداء القطاعات')}</h3>
            <p>{t('By sector today','القطاعات اليوم')}</p>
          </div>
          {STATIC_MARKET.sectors.map(s => <SectorRow key={s.name} sector={s} />)}
        </div>
      </div>

    </div>
  )
}
