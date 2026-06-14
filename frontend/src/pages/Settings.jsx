import '../styles/settings.css'
import { useState }        from 'react'
import { useNavigate }     from 'react-router-dom'
import { useApp }          from '../context/AppContext'
import { useLang }         from '../hooks/useLang'
import { useToast }        from '../hooks/useToast'
import PasswordInput       from '../components/ui/PasswordInput'
import DeleteModal         from '../components/ui/DeleteModal'
import { ROUTES }          from '../constants/routes'

export default function Settings() {
  const navigate = useNavigate()
  const { user, setUser, lang, setLang } = useApp()
  const { t, isAr } = useLang()
  const toast = useToast()
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const [f, setF] = useState({
    name: `${user?.firstName||''} ${user?.lastName||''}`.trim(),
    email: user?.email||'', pwCur:'', pwNew:'', pwCf:'',
    emailNotif: user?.preferences?.emailNotif ?? false,
  })
  const [showPw, setShowPw] = useState({ cur:false, new:false, cf:false })
  const [lpOpen, setLpOpen] = useState(false)
  const up = k => e => setF(p => ({ ...p, [k]: e.target.type==='checkbox' ? e.target.checked : e.target.value }))

  function save() {
    const [firstName,...rest] = f.name.trim().split(' ')
    setUser({ ...user, firstName, lastName:rest.join(' '), email:f.email, preferences:{ language:lang, emailNotif:f.emailNotif } })
    toast(t('Changes saved successfully!','تم حفظ التغييرات بنجاح!'), 'success')
  }

  function logout() { setUser(null); navigate(ROUTES.SIGNIN) }

  function confirmDelete() {
    setUser(null)
    navigate(ROUTES.SIGNIN)
  }

  return (
    <div className="settings-wrap">
      {/* Delete confirmation modal */}
      {showDeleteModal && (
        <DeleteModal
          onConfirm={confirmDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}

      <div className="settings-page-title">
        <span style={{fontSize:'1.45rem'}}>⚙️</span>
        <h1>{t('Settings','الإعدادات')}</h1>
      </div>
      <p className="settings-page-sub">{t('Manage your account preferences and notification settings','إدارة تفضيلات حسابك وإعدادات الإشعارات')}</p>

      {/* Profile Information */}
      <div className="settings-card">
        <div className="settings-card-head"><div className="settings-card-head-left">
          <h3>👤 {t('Profile Information','معلومات الملف الشخصي')}</h3>
          <p>{t('Update your personal information','تحديث معلوماتك الشخصية')}</p>
        </div></div>
        <div className="mb-2"><div className="s-label">{t('Name','الاسم')}</div>
          <div className="s-input-wrap"><input className="s-input s-input-with-icon" value={f.name} onChange={up('name')}/><span className="s-input-icon">✏️</span></div>
        </div>
        <div><div className="s-label">{t('Email','البريد الإلكتروني')}</div>
          <div className="s-input-wrap"><input className="s-input s-input-with-icon" type="email" value={f.email} onChange={up('email')}/><span className="s-input-icon">✏️</span></div>
        </div>
      </div>

      {/* Change Password */}
      <div className="settings-card glow-card">
        <div className="settings-card-head"><div className="settings-card-head-left">
          <h3>🔒 {t('Change Password','تغيير كلمة المرور')}</h3>
          <p>{t('Update your password for enhanced account security','تحديث كلمة المرور لتعزيز أمان الحساب')}</p>
        </div></div>
        <div className="mb-2">
          <div className="pw-label-row">
            <div className="s-label">{t('Current Password','كلمة المرور الحالية')}</div>
            <a className="forgot-link" href="#">{t('Forgot password?','نسيت كلمة المرور؟')}</a>
          </div>
          <PasswordInput value={f.pwCur} onChange={up('pwCur')} />
        </div>
        <div className="mb-2"><div className="s-label">{t('New Password','كلمة المرور الجديدة')}</div>
          <PasswordInput value={f.pwNew} onChange={up('pwNew')} placeholder={t('New password','كلمة مرور جديدة')} />
        </div>
        <div><div className="s-label">{t('Confirm New Password','تأكيد كلمة المرور الجديدة')}</div>
          <PasswordInput value={f.pwCf} onChange={up('pwCf')} placeholder={t('Confirm','تأكيد')} />
        </div>
      </div>

      {/* Preferences */}
      <div className="settings-card">
        <div className="settings-card-head"><div className="settings-card-head-left">
          <h3>🎛️ {t('Preferences','التفضيلات')}</h3>
          <p>{t('Manage your language and app preferences','إدارة تفضيلات اللغة والتطبيق')}</p>
        </div></div>
        <div className="pref-row">
          <span className="pref-label">{t('Select Language','اختر اللغة')}</span>
          <div style={{position:'relative'}}>
            <button className="lang-picker-btn" onClick={()=>setLpOpen(o=>!o)}>
              {lang==='en'?'🇬🇧 English':'🇸🇦 العربية'} ▾
            </button>
            {lpOpen && (
              <div className="lang-picker-menu open">
                <div className="lang-opt" onClick={()=>{setLang('en');setLpOpen(false)}}>🇬🇧 English</div>
                <div className="lang-opt" onClick={()=>{setLang('ar');setLpOpen(false)}}>🇸🇦 العربية</div>
              </div>
            )}
          </div>
        </div>
        <div className="pref-row">
          <div>
            <div className="pref-label">{t('Email Notifications','إشعارات البريد الإلكتروني')}</div>
            <div className="pref-sub">{t('Receive updates via email','استلام التحديثات عبر البريد')}</div>
          </div>
          <label className="toggle"><input type="checkbox" checked={f.emailNotif} onChange={up('emailNotif')}/><span className="toggle-track"/></label>
        </div>
      </div>

      {/* Privacy & Security */}
      <div className="settings-card">
        <div className="settings-card-head"><div className="settings-card-head-left">
          <h3>🛡️ {t('Privacy & Security','الخصوصية والأمان')}</h3>
          <p>{t('Manage your privacy and security settings','إدارة إعدادات الخصوصية والأمان')}</p>
        </div></div>
        <p className="privacy-text">{t("We collect minimal data to provide personalised recommendations. Your data is never sold to third parties.","نجمع الحد الأدنى من البيانات لتقديم توصيات مخصصة. لن يتم بيع بياناتك.")}</p>
        <div className="danger-zone-col">
          <button className="btn btn-ghost btn-sm" onClick={logout}>{t('Log Out','تسجيل الخروج')}</button>
          {/* Opens custom modal instead of window.confirm */}
          <button className="btn btn-danger btn-danger-full" onClick={() => setShowDeleteModal(true)}>
            {t('Delete Account','حذف الحساب')}
          </button>
        </div>
      </div>

      <div className="settings-save-row">
        <button className="btn btn-primary" onClick={save}>{t('Save Changes','حفظ التغييرات')}</button>
      </div>
    </div>
  )
}
