import { ROUTE_PATHS } from '@/constants/routePaths'
import { useAuthStore } from '@/stores/authStore'
import { Navigate, useLocation } from 'react-router-dom'

export const RequireAdmin = ({ children }: { children: React.ReactNode }) => {
  const { isLoggedIn, isAuthInitialized, user } = useAuthStore()
  const location = useLocation()

  if (!isAuthInitialized) {
    return null
  }

  if (!isLoggedIn) {
    const redirect = encodeURIComponent(location.pathname + location.search)

    return <Navigate to={`${ROUTE_PATHS.LOGIN}?redirect=${redirect}`} replace />
  }

  if (user?.user_info.role !== 'ADMIN') {
    return <Navigate to={ROUTE_PATHS.HOME} replace />
  }

  return children
}
