// S — handles Sign In, Sign Up, and Forgot Password as three steps.
import '../styles/auth.css'
import { useState }        from 'react'
import { useLang }         from '../hooks/useLang'
import { useAuth }         from '../hooks/useAuth'
import { useToast }        from '../hooks/useToast'
import { authService }     from '../services/authService'
import AuthBars            from '../components/ui/AuthBars'
import PasswordInput       from '../components/ui/PasswordInput'
import PasswordStrength    from '../components/ui/PasswordStrength'

// ── Forgot password: 3-step flow ────────────────────────────────
function ForgotPassword({ onBack }) {
  const { t } = useLang()
  const toast  = useToast()
  const [step,      setStep]      = useState(1)
  const [email,     setEmail]     = useState('')
  const [code,      setCode]      = useState(['','','','','',''])
  const [newPw,     setNewPw]     = useState('')
  const [retryPw,   setRetryPw]   = useState('')
  const [countdown, setCountdown] = useState(0)

  function submitEmail(e) {
    e.preventDefault()
    if (!email) { toast(t('Enter your email','أدخل بريدك الإلكتروني'),'error'); return }
    const user = JSON.parse(localStorage.getItem('ist_user')||'null')
    if (!user || user.email !== email) {
      toast(t('No account found with that email','لا يوجد حساب بهذا البريد الإلكتروني'),'error'); return
    }
    toast(t('Verification code sent to your email','تم إرسال رمز التحقق إلى بريدك'),'success')
    setStep(2)
    startCountdown()
  }

  function startCountdown() {
    setCountdown(40)
    const timer = setInterval(() => {
      setCountdown(c => { if (c <= 1) { clearInterval(timer); return 0 } return c - 1 })
    }, 1000)
  }

  function handleCodeChange(i, val) {
    const cleaned = val.replace(/\D/,'').slice(-1)
    const next = [...code]; next[i] = cleaned; setCode(next)
    if (cleaned && i < 5) document.getElementById(`otp-${i+1}`)?.focus()
  }
  function handleCodeKey(i, e) {
    if (e.key === 'Backspace' && !code[i] && i > 0) document.getElementById(`otp-${i-1}`)?.focus()
  }
  function submitCode(e) {
    e.preventDefault()
    if (code.some(c => !c)) { toast(t('Enter all 6 digits','أدخل جميع الأرقام الستة'),'error'); return }
    setStep(3)
  }

  function submitNewPw(e) {
    e.preventDefault()
    const { hasLength, hasSpecial } = authService.validatePassword(newPw)
    if (!hasLength || !hasSpecial) {
      toast(t('Password must be 8+ chars with a number or symbol','كلمة المرور يجب 8+ أحرف مع رقم أو رمز'),'error'); return
    }
    if (newPw !== retryPw) { toast(t('Passwords do not match','كلمتا المرور غير متطابقتين'),'error'); return }
    const user = JSON.parse(localStorage.getItem('ist_user')||'null')
    if (user) { user.password = newPw; localStorage.setItem('ist_user', JSON.stringify(user)) }
    toast(t('Password updated! Please sign in.','تم تحديث كلمة المرور! يرجى تسجيل الدخول.'),'success')
    onBack()
  }

  return (
    <div className="forgot-wrap">
      <div className="forgot-steps">
        <span className={`forgot-step-label${step===1?' active':''}`}>{t('Email','البريد')}</span>
        <span className="forgot-step-sep">›</span>
        <span className={`forgot-step-label${step===2?' active':''}`}>{t('VERIFICATION','التحقق')}</span>
        <span className="forgot-step-sep">›</span>
        <span className={`forgot-step-label${step===3?' active':''}`}>{t('New password','كلمة المرور الجديدة')}</span>
      </div>

      {step === 1 && (
        <div className="forgot-card">
          <h2 className="forgot-title">{t('Reset your password','إعادة تعيين كلمة المرور')}</h2>
          <p className="forgot-sub">{t('Type in your registered email address to reset password','أدخل بريدك الإلكتروني المسجل لإعادة تعيين كلمة المرور')}</p>
          <form onSubmit={submitEmail} className="auth-form">
            <div className="auth-field">
              <label htmlFor="forgot-email">{t('Email Address *','البريد الإلكتروني *')}</label>
              <input id="forgot-email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary forgot-next-btn">
              {t('NEXT →','التالي ←')}
            </button>
            <button type="button" className="btn btn-ghost forgot-back-btn" onClick={onBack}>
              {t('BACK TO LOGIN','العودة لتسجيل الدخول')}
            </button>
          </form>
        </div>
      )}

      {step === 2 && (
        <div className="forgot-card">
          <button className="forgot-back-arrow" onClick={()=>setStep(1)}>← {t('Back','رجوع')}</button>
          <h2 className="forgot-title">{t('Enter verification code','أدخل رمز التحقق')}</h2>
          <p className="forgot-sub">
            {t('The verification code has been sent to email','تم إرسال رمز التحقق إلى البريد الإلكتروني')}{' '}
            <strong>{email}</strong>
          </p>
          <form onSubmit={submitCode} className="auth-form">
            <div className="otp-boxes">
              {code.map((c,i) => (
                <input
                  key={i}
                  id={`otp-${i}`}
                  className="otp-box"
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={c}
                  onChange={e => handleCodeChange(i, e.target.value)}
                  onKeyDown={e => handleCodeKey(i, e)}
                />
              ))}
            </div>
            <div className="otp-resend">
              {countdown > 0
                ? <span>{t(`Resend after ${countdown} seconds`,`إعادة الإرسال بعد ${countdown} ثانية`)}</span>
                : <button type="button" className="otp-resend-btn" onClick={startCountdown}>{t('Resend code','إعادة الإرسال')}</button>
              }
            </div>
            <button type="submit" className="btn btn-primary forgot-next-btn">{t('VERIFY','تحقق')}</button>
          </form>
        </div>
      )}

      {step === 3 && (
        <div className="forgot-card">
          <h2 className="forgot-title">{t('Reset your password','إعادة تعيين كلمة المرور')}</h2>
          <p className="forgot-sub">{t('Type in your new password','أدخل كلمة المرور الجديدة')}</p>
          <form onSubmit={submitNewPw} className="auth-form">
            <div className="auth-field">
              <label htmlFor="new-pw">{t('New password *','كلمة المرور الجديدة *')}</label>
              <PasswordInput id="new-pw" value={newPw} onChange={e=>setNewPw(e.target.value)} />
            </div>
            <div className="auth-field">
              <label htmlFor="retry-pw">{t('Retry new password *','تأكيد كلمة المرور الجديدة *')}</label>
              <PasswordInput id="retry-pw" value={retryPw} onChange={e=>setRetryPw(e.target.value)} />
            </div>
            <PasswordStrength password={newPw} confirm={retryPw} email={email} firstName="" />
            <button type="submit" className="btn btn-primary forgot-next-btn">{t('NEXT →','التالي ←')}</button>
            <button type="button" className="btn btn-ghost forgot-back-btn" onClick={onBack}>
              {t('BACK TO LOGIN','العودة لتسجيل الدخول')}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

// ── Main SignIn component ────────────────────────────────────────
export default function SignIn() {
  const { t } = useLang()
  const { signIn, register } = useAuth()
  const toast  = useToast()
  const [tab,   setTab]   = useState('signin')
  const [f,     setF]     = useState({ firstName:'', lastName:'', email:'', password:'', confirm:'' })
  const up = k => e => setF(p => ({ ...p, [k]: e.target.value }))

  function handleSignIn(e) {
    e.preventDefault()
    if (!f.email || !f.password) { toast(t('Please fill all fields','يرجى ملء جميع الحقول'),'error'); return }
    signIn(f.email, f.password)
  }

  function handleSignUp(e) {
    e.preventDefault()
    if (!f.firstName || !f.email || !f.password) { toast(t('Please fill all fields','يرجى ملء جميع الحقول'),'error'); return }
    const { hasLength, hasSpecial } = authService.validatePassword(f.password)
    if (!hasLength || !hasSpecial) { toast(t('Password needs 8+ chars with a number or symbol','كلمة المرور تحتاج 8+ أحرف مع رقم أو رمز'),'error'); return }
    if (f.password !== f.confirm) { toast(t('Passwords do not match','كلمتا المرور غير متطابقتين'),'error'); return }
    register({ firstName: f.firstName, lastName: f.lastName, email: f.email, password: f.password })
  }

  if (tab === 'forgot') {
    return (
      <div className="auth-page">
        <AuthBars />
        <div className="auth-box">
          <div className="auth-logo"><img src="/assets/logoo.png" alt="iStocker" style={{height:'40px'}} /></div>
          <ForgotPassword onBack={() => setTab('signin')} />
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <AuthBars />
      <div className="auth-box">
        <div className="auth-logo"><img src="/assets/logoo.png" alt="iStocker" style={{height:'40px'}} /></div>

        <div className="auth-tabs">
          <button className={`auth-tab${tab==='signin'?' active':''}`} onClick={()=>setTab('signin')}>{t('Sign In','تسجيل الدخول')}</button>
          <button className={`auth-tab${tab==='signup'?' active':''}`} onClick={()=>setTab('signup')}>{t('Sign Up','إنشاء حساب')}</button>
        </div>

        {tab === 'signin' ? (
          <form onSubmit={handleSignIn} className="auth-form">
            <div className="auth-field">
              <label htmlFor="signin-email">{t('Email','البريد الإلكتروني')}</label>
              <input id="signin-email" type="email" value={f.email} onChange={up('email')} />
            </div>
            <div className="auth-field">
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <label htmlFor="signin-password">{t('Password','كلمة المرور')}</label>
                <button type="button" className="forgot-link-inline" onClick={()=>setTab('forgot')}>
                  {t('Forgot username or password?','نسيت اسم المستخدم أو كلمة المرور؟')}
                </button>
              </div>
              <PasswordInput id="signin-password" value={f.password} onChange={up('password')} />
            </div>
            <button type="submit" className="btn btn-primary" style={{width:'100%'}}>{t('Sign In','تسجيل الدخول')}</button>
          </form>
        ) : (
          <form onSubmit={handleSignUp} className="auth-form">
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'1rem'}}>
              <div className="auth-field">
                <label htmlFor="signup-firstname">{t('First Name','الاسم الأول')}</label>
                <input id="signup-firstname" value={f.firstName} onChange={up('firstName')} />
              </div>
              <div className="auth-field">
                <label htmlFor="signup-lastname">{t('Last Name','الاسم الأخير')}</label>
                <input id="signup-lastname" value={f.lastName} onChange={up('lastName')} />
              </div>
            </div>
            <div className="auth-field">
              <label htmlFor="signup-email">{t('Enter your E-mail','أدخل بريدك الإلكتروني')}</label>
              <input id="signup-email" type="email" value={f.email} onChange={up('email')} />
            </div>
            <div className="auth-field">
              <label htmlFor="signup-password">{t('Password','كلمة المرور')}</label>
              <PasswordInput id="signup-password" value={f.password} onChange={up('password')} />
              <PasswordStrength password={f.password} confirm={f.confirm} email={f.email} firstName={f.firstName} />
            </div>
            <div className="auth-field">
              <label htmlFor="signup-confirm">{t('Confirm Password','تأكيد كلمة المرور')}</label>
              <PasswordInput id="signup-confirm" value={f.confirm} onChange={up('confirm')} />
            </div>
            <button type="submit" className="btn btn-primary" style={{width:'100%'}}>{t('Create Account','إنشاء الحساب')}</button>
          </form>
        )}
      </div>
    </div>
  )
}