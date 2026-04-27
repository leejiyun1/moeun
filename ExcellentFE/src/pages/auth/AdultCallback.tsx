import { ROUTE_PATHS } from '@/constants/routePaths'
import {
  useAdultAuthComplete,
  useAdultAuthToken,
} from '@/hooks/auth/useAdultAuth'
import { tokenStorage } from '@/utils/tokenStorage'
import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const AdultCallback = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const code = searchParams.get('code')
  const hasRunRef = useRef(false)

  const { mutateAsync: adultAuthToken, isPending } = useAdultAuthToken()
  const { mutateAsync: adultAuthComplete } = useAdultAuthComplete()

  useEffect(() => {
    if (hasRunRef.current) return
    hasRunRef.current = true

    const tempToken = tokenStorage.getTempToken()

    if (!code || !tempToken) {
      navigate(ROUTE_PATHS.ADULT_AUTH_MANUAL, { replace: true })
      return
    }

    const run = async () => {
      try {
        await adultAuthToken(code)
        await adultAuthComplete(tempToken)
      } catch {
        navigate(ROUTE_PATHS.ADULT_AUTH_MANUAL, { replace: true })
      }
    }
    run()
  }, [adultAuthComplete, adultAuthToken, code, navigate])

  if (isPending) {
    return <p>성인인증 중입니다...</p>
  }

  return null
}

export default AdultCallback
