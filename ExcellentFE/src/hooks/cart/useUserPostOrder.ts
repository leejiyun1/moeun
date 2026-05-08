import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { orderApi } from '@/api/order'
import { showSuccess, showError } from '@/utils/feedbackUtils'
import { ROUTE_PATHS } from '@/constants/routePaths'
import axios from 'axios'
import { requestTossTestPayment } from '@/utils/tossPayments'

const useUserPostOrder = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const postOrderMutation = useMutation({
    mutationFn: async (itemIds: number[]) => {
      const order = await orderApi.CREATE_FROM_CART(itemIds)
      await requestTossTestPayment(order)
      return order
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['UserCart'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      showSuccess('토스 테스트 결제창으로 이동합니다.')
    },
    onError: (error) => {
      if (
        axios.isAxiosError(error) &&
        error.response?.data?.code === 'ADULT_VERIFICATION_REQUIRED'
      ) {
        const redirect = encodeURIComponent(ROUTE_PATHS.CART)
        navigate(`${ROUTE_PATHS.ADULT_VERIFICATION}?redirect=${redirect}`)
        return
      }

      showError('주문 처리 중 오류가 발생했습니다.')
    },
  })

  return {
    postOrderMutation,
  }
}

export default useUserPostOrder
