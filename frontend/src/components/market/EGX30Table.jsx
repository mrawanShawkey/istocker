// S — Single Responsibility: searchable/filterable/sortable table of all EGX30 companies.
//     Clicking a row fires onSelect(company) — it does not own the chart.
// O — Open/Closed: columns, sorting, filtering all self-contained; Market page never changes.
// I — Interface Segregation: receives only companies, selectedCode, onSelect.

import { useState, useMemo } from 'react'
import { useLang } from '../../hooks/useLang'
import { EGX30_SECTORS } from '../../constants/egx30Data'

const COLUMNS = [
  { key: 'code',   en: 'Code',   ar: 'الرمز',    align: 'left'  },
  { key: 'name',   en: 'Company',ar: 'الشركة',   align: 'left'  },
  { key: 'price',  en: 'Price',  ar: 'السعر',    align: 'right' },
  { key: 'chg',    en: 'Change', ar: 'التغيير',  align: 'right' },
  { key: 'pct',    en: '%',      ar: '%',         align: 'right' },
  { key: 'open',   en: 'Open',   ar: 'الافتتاح', align: 'right' },
  { key: 'high',   en: 'High',   ar: 'الأعلى',   align: 'right' },
  { key: 'low',    en: 'Low',    ar: 'الأدنى',   align: 'right' },
  { key: 'sector', en: 'Sector', ar: 'القطاع',   align: 'left'  },
]

export default function EGX30Table({ companies, selectedCode, onSelect }) {
  const { t, isAr } = useLang()
  const [search,      setSearch]      = useState('')
  const [sector,      setSector]      = useState('All')
  const [sortKey,     setSortKey]     = useState('code')
  const [sortDir,     setSortDir]     = useState('asc')

  // Filter + sort — computed only when dependencies change
  const rows = useMemo(() => {
    let list = [...companies]
    // filter by search
    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter(c =>
        c.code.toLowerCase().includes(q) ||
        c.name.toLowerCase().includes(q)  ||
        (c.nameAr && c.nameAr.includes(q))
      )
    }
    // filter by sector
    if (sector !== 'All') {
      list = list.filter(c => c.sector === sector)
    }
    // sort
    list.sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey]
      if (typeof av === 'string') return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av)
      return sortDir === 'asc' ? av - bv : bv - av
    })
    return list
  }, [companies, search, sector, sortKey, sortDir])

  function handleSort(key) {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const sortIcon = (key) => {
    if (sortKey !== key) return <span className="sort-icon sort-icon--inactive">⇅</span>
    return <span className="sort-icon sort-icon--active">{sortDir === 'asc' ? '↑' : '↓'}</span>
  }

  return (
    <div className="egx-table-section">

      {/* ── Controls: search + sector filter ── */}
      <div className="egx-controls">
        <div className="egx-search-wrap">
          <span className="egx-search-icon">🔍</span>
          <input
            className="egx-search"
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder={t('Search company or code…', 'ابحث عن شركة أو رمز…')}
          />
          {search && (
            <button className="egx-search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>

        <div className="egx-sector-pills">
          {EGX30_SECTORS.map(s => (
            <button
              key={s}
              className={`egx-sector-pill${sector === s ? ' active' : ''}`}
              onClick={() => setSector(s)}
            >
              {s === 'All' ? t('All Sectors', 'جميع القطاعات') : s}
            </button>
          ))}
        </div>
      </div>

      {/* ── Results count ── */}
      <div className="egx-count">
        {t(`${rows.length} of ${companies.length} companies`, `${rows.length} من ${companies.length} شركة`)}
        {selectedCode && (
          <button className="egx-deselect" onClick={() => onSelect(null)}>
            {t('× Clear selection', '× إلغاء التحديد')}
          </button>
        )}
      </div>

      {/* ── Scrollable table ── */}
      <div className="egx-table-wrap">
        <table className="egx-table">
          <thead>
            <tr>
              {COLUMNS.map(col => (
                <th
                  key={col.key}
                  className={`egx-th egx-th--${col.align}`}
                  onClick={() => handleSort(col.key)}
                >
                  <span>{isAr ? col.ar : col.en}</span>
                  {sortIcon(col.key)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={COLUMNS.length} className="egx-empty">
                  {t('No companies match your search', 'لا توجد شركات تطابق بحثك')}
                </td>
              </tr>
            ) : (
              rows.map(company => (
                <tr
                  key={company.code}
                  className={`egx-row${selectedCode === company.code ? ' egx-row--active' : ''}`}
                  onClick={() => onSelect(company)}
                >
                  <td className="egx-td egx-td--code">{company.code}</td>
                  <td className="egx-td egx-td--name">
                    <div className="egx-company-name">{isAr ? company.nameAr : company.name}</div>
                  </td>
                  <td className="egx-td egx-td--right egx-td--price">
                    EGP {company.price.toFixed(2)}
                  </td>
                  <td className={`egx-td egx-td--right ${company.dir}`}>
                    {company.chg > 0 ? '+' : ''}{company.chg.toFixed(2)}
                  </td>
                  <td className={`egx-td egx-td--right ${company.dir}`}>
                    <span className={`egx-pct-badge egx-pct-badge--${company.dir}`}>
                      {company.dir === 'up' ? '▲' : '▼'} {Math.abs(company.pct).toFixed(2)}%
                    </span>
                  </td>
                  <td className="egx-td egx-td--right egx-td--muted">{company.open.toFixed(2)}</td>
                  <td className="egx-td egx-td--right up">{company.high.toFixed(2)}</td>
                  <td className="egx-td egx-td--right down">{company.low.toFixed(2)}</td>
                  <td className="egx-td">
                    <span className="egx-sector-tag">{company.sector}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  )
}
