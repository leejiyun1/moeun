import Button from '@/components/common/Button'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { orderApi } from '@/api/order'
import { showError, showSuccess } from '@/utils/feedbackUtils'
import { useMutation } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const TossPaymentSuccess = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const paymentKey = searchParams.get('paymentKey') ?? ''
  const orderId = searchParams.get('orderId') ?? ''
  const amount = Number(searchParams.get('amount') ?? 0)

  const confirmMutation = useMutation({
    mutationFn: () =>
      orderApi.CONFIRM_TOSS_PAYMENT({
        paymentKey,
        orderId,
        amount,
      }),
    onSuccess: () => {
      showSuccess('토스 테스트 결제가 완료되었습니다.')
      navigate(ROUTE_PATHS.MYPAGE.ORDER_HISTORY, { replace: true })
    },
    onError: () => {
      showError('결제 승인 중 오류가 발생했습니다.')
    },
  })
  const { mutate: confirmPayment, isError } = confirmMutation

  useEffect(() => {
    if (!paymentKey || !orderId || !amount) {
      showError('결제 승인 정보가 올바르지 않습니다.')
      return
    }
    confirmPayment()
  }, [amount, confirmPayment, orderId, paymentKey])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-6 text-center text-[#333333]">
      <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
        Toss Payments
      </p>
      <h1 className="text-3xl font-bold">테스트 결제 승인 중입니다</h1>
      <p className="mt-4 max-w-[520px] leading-7 text-[#666666]">
        결제창 인증은 완료됐고, 서버에서 금액과 주문번호를 검증한 뒤 토스
        테스트 결제 승인 API를 호출하고 있습니다.
      </p>
      {isError && (
        <Button
          variant="VARIANT4"
          className="mt-8"
          onClick={() => navigate(ROUTE_PATHS.CART)}
        >
          장바구니로 돌아가기
        </Button>
      )}
    </main>
  )
}

export default TossPaymentSuccess
