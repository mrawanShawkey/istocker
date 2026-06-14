// S — Single Responsibility: horizontal scrollable slider of all EGX30 ticker cards.
//     Arrow buttons + drag scroll. Does not own selection state.
// O — Open/Closed: card appearance controlled by TickerCard; this only handles layout.
// I — receives companies[], selectedCode, onSelect. Nothing else.

import { useRef } from 'react'
import { useLang } from '../../hooks/useLang'
import TickerCard  from './TickerCard'

export default function TickerSlider({ companies, selectedCode, onSelect }) {
  const { t } = useLang()
  const trackRef = useRef(null)

  // Scroll left / right by one card-width
  function scroll(dir) {
    const track = trackRef.current
    if (!track) return
    const cardW = track.querySelector('.ticker-card')?.offsetWidth || 260
    track.scrollBy({ left: dir * (cardW + 16), behavior: 'smooth' })
  }

  // Mouse drag to scroll
  const drag = useRef({ active: false, startX: 0, scrollLeft: 0 })
  function onMouseDown(e) {
    drag.current = { active: true, startX: e.pageX - trackRef.current.offsetLeft, scrollLeft: trackRef.current.scrollLeft }
    trackRef.current.style.cursor = 'grabbing'
  }
  function onMouseMove(e) {
    if (!drag.current.active) return
    e.preventDefault()
    const x    = e.pageX - trackRef.current.offsetLeft
    const walk = x - drag.current.startX
    trackRef.current.scrollLeft = drag.current.scrollLeft - walk
  }
  function onMouseUp() {
    drag.current.active = false
    if (trackRef.current) trackRef.current.style.cursor = 'grab'
  }

  return (
    <div className="ticker-slider-wrap">

      {/* Left arrow */}
      <button
        className="ticker-slider-arrow ticker-slider-arrow--left"
        onClick={() => scroll(-1)}
        aria-label={t('Scroll left', 'يسار')}
      >
        ‹
      </button>

      {/* Scrollable track */}
      <div
        className="ticker-slider-track"
        ref={trackRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        {companies.map(company => (
          <div key={company.code} className="ticker-slider-item">
            <TickerCard
              ticker={company}
              selected={selectedCode === company.code || selectedCode === company.name}
              onSelect={onSelect}
            />
          </div>
        ))}
      </div>

      {/* Right arrow */}
      <button
        className="ticker-slider-arrow ticker-slider-arrow--right"
        onClick={() => scroll(1)}
        aria-label={t('Scroll right', 'يمين')}
      >
        ›
      </button>

    </div>
  )
}
