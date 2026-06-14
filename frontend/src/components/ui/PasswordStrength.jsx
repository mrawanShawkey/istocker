// S — shows password strength checks. Used in SignUp only.
// I — receives only the password string and the confirm string.
import { useLang } from '../../hooks/useLang'

function check(pw, email, firstName) {
  return {
    hasLength:  pw.length >= 8,
    noPersonal: pw.length === 0 || (
      !pw.toLowerCase().includes((firstName||'').toLowerCase().slice(0,3)) &&
      !pw.toLowerCase().includes((email||'').split('@')[0].toLowerCase().slice(0,3))
    ),
    hasSpecial: /[\d!@#$%^&*_\-]/.test(pw),
  }
}

export default function PasswordStrength({ password, confirm, email, firstName }) {
  const { t } = useLang()
  if (!password) return null

  const { hasLength, noPersonal, hasSpecial } = check(password, email, firstName)
  const match = confirm.length > 0 && password === confirm

  const rules = [
    { ok: hasLength,  label: t('At least 8 characters',                    'على الأقل 8 أحرف')                      },
    { ok: noPersonal, label: t('Cannot contain your name or email address', 'لا يحتوي على اسمك أو بريدك الإلكتروني') },
    { ok: hasSpecial, label: t('Contains a number or symbol',               'يحتوي على رقم أو رمز')                  },
  ]

  const strong = hasLength && noPersonal && hasSpecial
  const strengthLabel = !password
    ? ''
    : !hasLength
    ? t('Weak', 'ضعيف')
    : strong
    ? t('Strong', 'قوي')
    : t('Medium', 'متوسط')

  return (
    <div className="pw-strength-wrap">
      <div className={`pw-strength-bar-row`}>
        <div className={`pw-strength-bar pw-strength-bar--${strong ? 'strong' : hasLength ? 'medium' : 'weak'}`} />
        <span className={`pw-strength-label pw-strength-label--${strong ? 'strong' : hasLength ? 'medium' : 'weak'}`}>
          {t('Password Strength :', 'قوة كلمة المرور :')} <strong>{strengthLabel}</strong>
        </span>
      </div>
      <div className="pw-checks">
        {rules.map((r, i) => (
          <div key={i} className={`pw-check${r.ok ? ' ok' : ''}`}>
            <span className="pw-check-icon">{r.ok ? '✓' : '✓'}</span>
            {r.label}
          </div>
        ))}
        {confirm.length > 0 && (
          <div className={`pw-check${match ? ' ok' : ' fail'}`}>
            <span className="pw-check-icon">{match ? '✓' : '✕'}</span>
            {t('Passwords match', 'كلمتا المرور متطابقتان')}
          </div>
        )}
      </div>
    </div>
  )
}
