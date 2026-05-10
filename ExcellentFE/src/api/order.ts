import { API_PATHS } from '@/constants/apiPaths'
import { axiosInstance } from '@/utils/axios'
import type { PaginatedResponse, ServerOrder } from '@/types/orderType'

export interface CreateOrderFromCartPayload {
  item_ids: number[]
  package_draft_ids?: number[]
  fulfillment_method: 'PICKUP' | 'DELIVERY' | 'UNDECIDED'
  pickup_store_id?: number | null
  pickup_date?: string | null
}

export const orderApi = {
  list: async (): Promise<PaginatedResponse<ServerOrder>> => {
    const response = await axiosInstance.get(API_PATHS.ORDER.LIST)
    return response.data as PaginatedResponse<ServerOrder>
  },
  CREATE_FROM_CART: async (payload: CreateOrderFromCartPayload) => {
    const response = await axiosInstance.post(
      API_PATHS.ORDER.CREATE_FROM_CART,
      payload
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
