// S — Delete account confirmation modal only.
// Matches screenshot exactly: red 3D alert triangle, title, description, two buttons.
import { useLang } from '../../hooks/useLang'

export default function DeleteModal({ onConfirm, onCancel }) {
  const { t } = useLang()
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>

        {/* 3D-style red alert triangle — matches screenshot */}
        <div className="modal-alert-icon">
          <svg viewBox="0 0 80 72" width="90" height="80" xmlns="http://www.w3.org/2000/svg">
            {/* Shadow layer */}
            <polygon points="40,6 76,68 4,68" fill="#7b0000" opacity="0.35" transform="translate(2,4)"/>
            {/* Dark red back face */}
            <polygon points="40,6 76,68 4,68" fill="#8b1a1a"/>
            {/* Bright red front face */}
            <polygon points="40,4 74,66 6,66" fill="#e03030"/>
            {/* Highlight shine top-left */}
            <polygon points="40,4 16,60 40,52" fill="#f05050" opacity="0.5"/>
            {/* Exclamation mark */}
            <rect x="37" y="22" width="6" height="22" rx="3" fill="white"/>
            <circle cx="40" cy="54" r="4" fill="white"/>
            {/* ALERT text */}
            <rect x="24" y="59" width="32" height="12" rx="3" fill="#c0392b"/>
            <text x="40" y="69" textAnchor="middle" fill="white"
              fontSize="7.5" fontWeight="800" fontFamily="Arial" letterSpacing="1.5">ALERT</text>
          </svg>
        </div>

        <h2 className="modal-title">{t('Delete Account', 'حذف الحساب')}</h2>
        <p className="modal-desc">
          {t('You are going to delete your', 'أنت على وشك حذف')}{' '}
          <span className="modal-accent">{t('"Account"', '"حسابك"')}</span>
        </p>

        <div className="modal-actions">
          <button className="modal-btn modal-btn--keep" onClick={onCancel}>
            {t('No , keep it', 'لا ، احتفظ به')}
          </button>
          <button className="modal-btn modal-btn--delete" onClick={onConfirm}>
            {t('Yes , Delete!', 'نعم ، احذف!')}
          </button>
        </div>
      </div>
    </div>
  )
}
