// S — displays toast notifications. Nothing else.
import { useEffect, useState } from 'react'
import { useApp } from '../../context/AppContext'

export default function Toast() {
  const { toast } = useApp()
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!toast) return
    setVisible(true)
    const t = setTimeout(() => setVisible(false), 3800)
    return () => clearTimeout(t)
  }, [toast])

  if (!toast) return null
  return (
    <div className={`toast toast-${toast.type}${visible ? ' show' : ''}`}>
      <div className="toast-inner">
        <span className="toast-icon">{toast.type === 'success' ? '✓' : '✕'}</span>
        <span className="toast-msg">{toast.msg}</span>
      </div>
    </div>
  )
}
