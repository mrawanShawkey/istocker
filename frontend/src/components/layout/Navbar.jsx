import { NavLink } from 'react-router-dom'
import { useApp }  from '../../context/AppContext'
import { useLang } from '../../hooks/useLang'
import { ROUTES }  from '../../constants/routes'

const NAV_LINKS = [
  { id:'home',      route: ROUTES.HOME,      en:'Home',                ar:'الرئيسية'             },
  { id:'education', route: ROUTES.EDUCATION, en:'Educational Content', ar:'المحتوى التعليمي'     },
  { id:'market',    route: ROUTES.MARKET,    en:'Market Overview',     ar:'نظرة عامة على السوق' },
  { id:'profile',   route: ROUTES.PROFILE,   en:'My Profile',          ar:'حسابي'               },
]

export default function Navbar() {
  const { user } = useApp()
  const { lang, switchLang } = useLang()

  return (
    <nav className="navbar">
      {/* Logo always links to home page */}
      <NavLink to={ROUTES.HOME} className="logo-wrap">
        <img className="logo-img" src="/assets/logoo.png" alt="iStocker" />
      </NavLink>

      {user && (
        <div className="navbar-center">
          <div className="nav-pills">
            {NAV_LINKS.map(link => (
              <NavLink
                key={link.id}
                to={link.route}
                end={link.id === 'home'}
                className={({ isActive }) => 'nav-pill' + (isActive ? ' active' : '')}
              >
                {lang === 'ar' ? link.ar : link.en}
              </NavLink>
            ))}
          </div>
        </div>
      )}

      <div className="nav-right">
        <button className="lang-btn" onClick={switchLang}>
          {lang === 'en' ? '🌐 العربية' : '🌐 English'}
        </button>
      </div>
    </nav>
  )
}
