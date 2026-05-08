import { ANONYMOUS, loadTossPayments } from '@tosspayments/tosspayments-sdk'
import { ROUTE_PATHS } from '@/constants/routePaths'
import type { ServerOrder } from '@/types/orderType'

const clientKey = import.meta.env.VITE_TOSS_PAYMENTS_CLIENT_KEY

export const requestTossTestPayment = async (order: ServerOrder) => {
  if (!clientKey) {
    throw new Error('토스페이먼츠 클라이언트 키가 설정되어 있지 않습니다.')
  }
  if (!order.payment?.merchant_uid) {
    throw new Error('결제 주문번호가 없습니다.')
  }

  const tossPayments = await loadTossPayments(clientKey)
  const payment = tossPayments.payment({ customerKey: ANONYMOUS })

  await payment.requestPayment({
    method: 'CARD',
    amount: {
      currency: 'KRW',
      value: order.total_price,
    },
    orderId: order.payment.merchant_uid,
    orderName: buildOrderName(order),
    successUrl: `${window.location.origin}${ROUTE_PATHS.TOSS_PAYMENT_SUCCESS}`,
    failUrl: `${window.location.origin}${ROUTE_PATHS.TOSS_PAYMENT_FAIL}`,
    customerName: order.user,
    card: {
      flowMode: 'DEFAULT',
    },
  })
}

const buildOrderName = (order: ServerOrder) => {
  const firstItem = order.items?.[0]
  if (!firstItem) {
    return `모은 주문 ${order.order_number}`
  }

  const extraCount = Math.max((order.items?.length ?? 1) - 1, 0)
  if (extraCount === 0) {
    return firstItem.product.name
  }

  return `${firstItem.product.name} 외 ${extraCount}건`
}
