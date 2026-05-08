import { API_PATHS } from '@/constants/apiPaths'
import { axiosInstance } from '@/utils/axios'
import type { PaginatedResponse, ServerOrder } from '@/types/orderType'

export const orderApi = {
  list: async (): Promise<PaginatedResponse<ServerOrder>> => {
    const response = await axiosInstance.get(API_PATHS.ORDER.LIST)
    return response.data as PaginatedResponse<ServerOrder>
  },
  CREATE_FROM_CART: async (itemIds: number[]) => {
    const response = await axiosInstance.post(
      API_PATHS.ORDER.CREATE_FROM_CART,
      { item_ids: itemIds, fulfillment_method: 'PICKUP' }
    )
    return response.data as ServerOrder
  },
  CONFIRM_TEST_PAYMENT: async (orderId: number) => {
    const response = await axiosInstance.post(
      API_PATHS.ORDER.CONFIRM_TEST_PAYMENT(orderId),
      { payment_key: `test_payment_${orderId}_${Date.now()}` }
    )
    return response.data as ServerOrder
  },
  CONFIRM_TOSS_PAYMENT: async (payload: {
    paymentKey: string
    orderId: string
    amount: number
  }) => {
    const response = await axiosInstance.post(
      API_PATHS.ORDER.CONFIRM_TOSS_PAYMENT,
      payload
    )
    return response.data as ServerOrder
  },
}
