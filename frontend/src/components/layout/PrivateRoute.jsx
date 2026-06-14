// S — route protection only. Does not render any UI.
// O — wrap any element without modifying it.
import { Navigate } from 'react-router-dom'
import { useApp }   from '../../context/AppContext'
import { ROUTES }   from '../../constants/routes'

export default function PrivateRoute({ children }) {
  const { user } = useApp()
  return user ? children : <Navigate to={ROUTES.SIGNIN} replace />
}
