// S — Left panel of auth pages: background image + overlay + branding.
// O — Open/Closed: swap the image by changing AUTH_BG_IMAGE only.
//     No other file needs to change.

const AUTH_BG_IMAGE = '/assets/auth-bg.png'

const HEIGHTS = [55, 80, 40, 95, 65, 75, 50, 88, 60, 70, 45, 100, 55, 80, 40, 90, 65]

export default function AuthBars() {
  return (
    <div className="auth-visual">
      {/* Background photo — fills the panel, dark overlay keeps text readable */}
      <img
        src={AUTH_BG_IMAGE}
        alt="iStocker background"
        className="auth-bg-photo"
      />

      {/* Dark gradient overlay on top of photo */}
      <div className="auth-visual-overlay" />

      {/* Animated chart bars — sit above overlay */}
      <div className="auth-bars">
        {HEIGHTS.map((h, i) => (
          <div key={i} className="auth-chart-bar" style={{ height: `${h}%` }} />
        ))}
      </div>

      {/* Branding — sits above everything */}
      <div className="auth-visual-content">
        <div className="auth-visual-top">
          <img src="/assets/logoo.png" alt="iStocker" className="auth-visual-logo" />
          <span className="auth-visual-brand">iStocker</span>
        </div>
        <div className="auth-visual-bottom">
          <h2>Smart Investing<br />Starts Here</h2>
          <p>Personalized stock recommendations built for the Egyptian market.</p>
        </div>
      </div>
    </div>
  )
}
