import Button from '@/components/common/Button'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { useNavigate, useSearchParams } from 'react-router-dom'

const TossPaymentFail = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const message = searchParams.get('message')
  const code = searchParams.get('code')

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-6 text-center text-[#333333]">
      <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
        Toss Payments
      </p>
      <h1 className="text-3xl font-bold">테스트 결제가 완료되지 않았습니다</h1>
      <p className="mt-4 max-w-[520px] leading-7 text-[#666666]">
        사용자가 결제를 취소했거나 결제창 인증 과정에서 오류가 발생했습니다.
        실제 주문으로 확정되지 않았습니다.
      </p>
      {(message || code) && (
        <p className="mt-5 rounded-[14px] bg-[#fff4f2] px-5 py-4 text-sm font-bold text-[#8a3a32]">
          {code ? `${code}: ` : ''}
          {message}
        </p>
      )}
      <Button
        variant="VARIANT4"
        className="mt-8"
        onClick={() => navigate(ROUTE_PATHS.CART)}
      >
        장바구니로 돌아가기
      </Button>
    </main>
  )
}

export default TossPaymentFail
