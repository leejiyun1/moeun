import { authApi } from '@/api/auth'
import { ERROR_MESSAGE } from '@/constants/message'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { useAuthStore } from '@/stores/authStore'
import type { DemoAdultVerificationRequest } from '@/types/auth'
import { getAxiosErrorMessage, showError } from '@/utils/feedbackUtils'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

export const useDemoAdultVerification = (
  redirectTo: string = ROUTE_PATHS.CART
) => {
  const { login } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (payload: DemoAdultVerificationRequest) =>
      authApi.demoAdultVerification(payload),

    onSuccess: async () => {
      await login()
      navigate(redirectTo, { replace: true })
    },

    onError: (error) => {
      showError(getAxiosErrorMessage(error) ?? ERROR_MESSAGE.ADULT_AUTH_FAILED)
    },
  })
}
