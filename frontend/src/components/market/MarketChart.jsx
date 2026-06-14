// S — renders the Chart.js line chart. Knows nothing about which stock is selected.
// Receives data + color as props — fully controlled from outside (O principle).
import { useEffect, useRef } from 'react'
import { Chart } from 'chart.js/auto'

function buildGradient(ctx, color) {
  const rgb = color === '#ef4444' ? '239,68,68' : '16,185,129'
  const g = ctx.createLinearGradient(0, 0, 0, 300)
  g.addColorStop(0, `rgba(${rgb},0.2)`)
  g.addColorStop(1, `rgba(${rgb},0)`)
  return g
}

export default function MarketChart({ data, color }) {
  const canvasRef = useRef(null)
  const chartRef  = useRef(null)

  useEffect(() => {
    if (!canvasRef.current) return
    chartRef.current?.destroy()
    const ctx = canvasRef.current.getContext('2d')
    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.values,
          borderColor: color,
          borderWidth: 2.5,
          fill: true,
          backgroundColor: (c) => buildGradient(c.chart.ctx, color),
          tension: 0.45,
          pointRadius: 0,
          pointHoverRadius: 6,
          pointHoverBackgroundColor: color,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#10101c',
            borderColor: 'rgba(109,40,217,0.3)',
            borderWidth: 1,
            titleColor: '#9ca3af',
            bodyColor: '#fff',
            callbacks: { label: (c) => `EGP ${c.raw.toLocaleString()}` },
          },
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#6b7280', font: { size: 11 } } },
          y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#6b7280', font: { size: 11 }, callback: v => v >= 1000 ? (v/1000).toFixed(0)+'k' : v }, position: 'right' },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data, color])

  return <canvas ref={canvasRef} style={{ maxHeight: '320px' }} />
}
