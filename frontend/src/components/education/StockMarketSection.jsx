// S — "Stock Market" educational card: tabs + video + lesson list.
// O — add new levels/lessons in educationContent.js; this component never changes.
// D — depends on LEVELS/LESSONS abstractions, not hardcoded content.
import { useState } from 'react'
import { useLang }  from '../../hooks/useLang'
import { LEVELS, LESSONS } from '../../constants/educationContent'
import LevelTabs  from './LevelTabs'
import VideoPlayer from './VideoPlayer'
import LessonList  from './LessonList'

export default function StockMarketSection() {
  const { t } = useLang()
  const [activeLevel,    setActiveLevel]    = useState('beginner')
  const [selectedLesson, setSelectedLesson] = useState(LESSONS.beginner[0])

  function handleLevelChange(levelId) {
    setActiveLevel(levelId)
    setSelectedLesson(LESSONS[levelId][0])
  }

  return (
    <section className="edu-section">
      <div className="edu-card">

        {/* Header */}
        <div className="edu-card-header">
          <h2 className="edu-card-title">{t('Stock Market', 'سوق الأسهم')}</h2>
          <p className="edu-card-sub">
            {t(
              'Everything you need to know to start your investing journey',
              'كل ما تحتاج معرفته لبدء رحلتك الاستثمارية'
            )}
          </p>
        </div>

        {/* Level tabs */}
        <LevelTabs
          levels={LEVELS}
          activeId={activeLevel}
          onSelect={handleLevelChange}
        />

        {/* Content area: video left, lessons right */}
        <div className="edu-content">
          <div className="edu-video-col">
            <VideoPlayer lesson={selectedLesson} key={selectedLesson.id} />
          </div>
          <div className="edu-list-col">
            <LessonList
              lessons={LESSONS[activeLevel]}
              selectedId={selectedLesson.id}
              onSelect={setSelectedLesson}
            />
          </div>
        </div>

      </div>
    </section>
  )
}
