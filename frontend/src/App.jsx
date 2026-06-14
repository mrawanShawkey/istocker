import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES }       from './constants/routes'
import { useApp }       from './context/AppContext'
import Navbar           from './components/layout/Navbar'
import Footer           from './components/layout/Footer'
import PrivateRoute     from './components/layout/PrivateRoute'
import Toast            from './components/ui/Toast'
import SignIn           from './pages/SignIn'
import Onboarding       from './pages/Onboarding'
import Home             from './pages/Home'
import Education        from './pages/Education'
import Market           from './pages/Market'
import Quiz             from './pages/Quiz'
import Result           from './pages/Result'
import Profile          from './pages/Profile'
import Settings         from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main>
        <Routes>
          {/* Public */}
          <Route path={ROUTES.SIGNIN}     element={<SignIn />} />
          <Route path={ROUTES.ONBOARDING} element={<Onboarding />} />

          {/* Protected */}
          <Route path={ROUTES.HOME}       element={<PrivateRoute><Home /></PrivateRoute>} />
          <Route path={ROUTES.EDUCATION}  element={<PrivateRoute><Education /></PrivateRoute>} />
          <Route path={ROUTES.MARKET}     element={<PrivateRoute><Market /></PrivateRoute>} />
          <Route path={ROUTES.QUIZ}       element={<PrivateRoute><Quiz /></PrivateRoute>} />
          <Route path={ROUTES.RESULT}     element={<PrivateRoute><Result /></PrivateRoute>} />
          <Route path={ROUTES.PROFILE}    element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path={ROUTES.SETTINGS}   element={<PrivateRoute><Settings /></PrivateRoute>} />

          <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
        </Routes>
      </main>
      <Footer />
      <Toast />
    </BrowserRouter>
  )
}
