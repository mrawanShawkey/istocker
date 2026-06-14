// S — renders one "top mover" row. No other responsibility.
export default function MoverRow({ mover }) {
  return (
    <div className="mover-row">
      <div>
        <div className="mover-code">{mover.code}</div>
        <div className="mover-name">{mover.name}</div>
      </div>
      <div className="mover-r">
        <div className="mover-price">EGP {mover.price.toFixed(2)}</div>
        <div className={`mover-pct ${mover.dir}`}>
          {mover.dir === 'up' ? '▲' : '▼'} {Math.abs(mover.pct).toFixed(2)}%
        </div>
      </div>
    </div>
  )
}
