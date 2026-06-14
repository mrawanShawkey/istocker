import { Link }    from 'react-router-dom'
import { useApp }  from '../../context/AppContext'
import { useLang } from '../../hooks/useLang'
import { ROUTES }  from '../../constants/routes'

const FOOTER_LINKS = [
  { id:'home',      route: ROUTES.HOME,      en:'Home',                ar:'الرئيسية'             },
  { id:'education', route: ROUTES.EDUCATION, en:'Educational Content', ar:'المحتوى التعليمي'     },
  { id:'market',    route: ROUTES.MARKET,    en:'Market Overview',     ar:'نظرة عامة على السوق' },
  { id:'profile',   route: ROUTES.PROFILE,   en:'My Profile',          ar:'حسابي'               },
]

export default function Footer() {
  const { user } = useApp()
  const { t, lang } = useLang()

  return (
    <footer className="footer">
      {/* Logo always links to home page */}
      <Link to={ROUTES.HOME} className="logo-wrap">
        <img className="logo-img logo-img-sm" src="/assets/logoo.png" alt="iStocker" />
      </Link>

      {user && (
        <nav className="footer-nav">
          {FOOTER_LINKS.map(link => (
            <Link key={link.id} to={link.route}>
              {lang === 'ar' ? link.ar : link.en}
            </Link>
          ))}
        </nav>
      )}

      <span className="footer-copy">
        {t('I-Stocker© 2026. All rights reserved.', 'جميع الحقوق محفوظة لشركة I-Stocker© 2026.')}
      </span>
    </footer>
  )
}
