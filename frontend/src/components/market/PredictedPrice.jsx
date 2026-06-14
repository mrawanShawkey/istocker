// S — Single Responsibility: renders the predicted price badge only.
//     Used in both TickerCard and StockInfoPanel.
// I — receives only currentPrice and predictedPrice; nothing else.

export default function PredictedPrice({ currentPrice, predictedPrice }) {
  if (!predictedPrice) return null

  const diff    = predictedPrice - currentPrice
  const diffPct = ((diff / currentPrice) * 100)
  const isUp    = diff >= 0
  const sign    = isUp ? '+' : ''

  return (
    <div className="predicted-box">
      <div className="predicted-label">Predicted Price</div>
      <div className={`predicted-value ${isUp ? 'up' : 'down'}`}>
        {predictedPrice.toFixed(3)}{' '}
        <span className="predicted-change">
          ({sign}{diff.toFixed(2)} / {sign}{diffPct.toFixed(1)}%)
        </span>
      </div>
    </div>
  )
}
