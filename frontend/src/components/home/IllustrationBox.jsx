// S  — Single Responsibility: renders one illustration slot.
// O  — Open/Closed: accepts imgSrc to upgrade to real image with zero changes elsewhere.
// When imgSrc is provided → shows the real image.
// When not → shows a styled "Add image" placeholder that the developer can drop an image into.

export default function IllustrationBox({ emoji = '📊', label, imgSrc, altText }) {
  if (imgSrc) {
    return (
      <div className="illus-box illus-box--filled">
        <img
          src={imgSrc}
          alt={altText || label || 'illustration'}
          className="illus-img"
        />
      </div>
    )
  }

  return (
    <div className="illus-box illus-box--empty">
      <span className="illus-emoji" aria-hidden="true">{emoji}</span>
      <div className="illus-placeholder-tag">
        <span className="illus-placeholder-icon">🖼️</span>
        <span>{label || 'Add image here'}</span>
      </div>
    </div>
  )
}
