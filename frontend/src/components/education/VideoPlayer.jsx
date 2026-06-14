// S — renders the video thumbnail + play button, then the iframe when clicked.
// O — supports any YouTube embed URL; adding local video support = one new prop.
import { useState } from 'react'
import { useLang }  from '../../hooks/useLang'

function getYouTubeId(url) {
  // Extracts video ID from a YouTube embed URL like https://www.youtube.com/embed/VIDEO_ID
  const parts = url.split('/embed/')
  return parts.length > 1 ? parts[1].split('?')[0] : null
}

export default function VideoPlayer({ lesson }) {
  const { isAr } = useLang()
  const [playing, setPlaying] = useState(false)
  const content  = isAr ? lesson.ar : lesson.en
  const ytId     = getYouTubeId(lesson.videoUrl)
  const thumbUrl = ytId
    ? `https://img.youtube.com/vi/${ytId}/hqdefault.jpg`
    : null

  return (
    <div className="video-player">
      <div className="video-frame-wrap">
        {playing ? (
          <iframe
            className="video-frame"
            src={`${lesson.videoUrl}?autoplay=1&rel=0`}
            title={content.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <div className="video-thumb" onClick={() => setPlaying(true)} role="button" tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && setPlaying(true)}>
            {thumbUrl && (
              <img
                src={thumbUrl}
                alt={content.title}
                className="video-thumb-img"
                onError={e => { e.target.style.display = 'none' }}
              />
            )}
            {/* dark overlay so the play button stands out */}
            <div className="video-thumb-overlay" />
            <div className="video-play-btn" aria-label="Play video">
              <svg viewBox="0 0 24 24" fill="currentColor" width="36" height="36">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <div className="video-duration">{lesson.duration}</div>
          </div>
        )}
      </div>
    </div>
  )
}
