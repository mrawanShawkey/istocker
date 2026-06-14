// S — renders one stock card. Used by Result page.
import { useLang } from '../../hooks/useLang'

const SECTOR_TAG = { 'Real Estate':'tag-re','Technology':'tag-tech','Finance':'tag-fin','Consumer':'tag-cons','Construction':'tag-cons' }

export default function StockCard({ stock }) {
  const { isAr } = useLang()
  return (
    <div className="stock-card">
      <div className={`stock-sector-tag ${SECTOR_TAG[stock.sector]||'tag-fin'}`}>{stock.sector}</div>
      <div className="stock-code">{stock.code}</div>
      <div className="stock-full-name">{isAr?(stock.nameAr||stock.name):stock.name}</div>
      <div className="stock-price-row">
        <div className="stock-price">EGP {stock.price.toFixed(2)}</div>
        <div className={`stock-chg ${stock.chg>=0?'up':'down'}`}>{stock.chg>=0?'▲':'▼'} {Math.abs(stock.chg).toFixed(2)}%</div>
      </div>
      {(stock.desc||stock.descAr) && <div className="stock-desc">{isAr?(stock.descAr||stock.desc):stock.desc}</div>}
    </div>
  )
}
