import { adminApi } from '@/api/admin'
import { ADMIN_QUERY_KEYS } from '@/constants/admin'
import { useQuery } from '@tanstack/react-query'
import AdminPageShell from './AdminPageShell'

const priceFormatter = new Intl.NumberFormat('ko-KR')

const orderStatusLabel: Record<string, string> = {
  PENDING_PAYMENT: '결제 대기',
  PENDING: '주문 완료',
  CONFIRMED: '주문 확인',
  READY: '준비 완료',
  COMPLETED: '완료',
  CANCELLED: '취소',
}

const paymentStatusLabel: Record<string, string> = {
  READY: '결제 대기',
  PAID: '결제 완료',
  FAILED: '결제 실패',
  CANCELLED: '결제 취소',
  REFUNDED: '환불 완료',
}

const fulfillmentLabel: Record<string, string> = {
  PICKUP: '매장 수령',
  DELIVERY: '배송',
  UNDECIDED: '미정',
}

const AdminOrders = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.ORDERS],
    queryFn: adminApi.getOrders,
  })

  return (
    <AdminPageShell
      title="주문 관리"
      description="현재 주문은 테스트 결제 기준으로만 처리합니다. 실제 판매 전환 시 결제 PG와 수령 정책을 이 구조에 연결합니다."
    >
      <section className="rounded-[20px] border border-[#d9d9d9] bg-white">
        <div className="flex items-center justify-between border-b border-[#eeeeee] px-5 py-4">
          <h2 className="text-xl font-bold">주문 목록</h2>
          <span className="text-sm text-[#888888]">총 {data?.count ?? 0}건</span>
        </div>

        {isLoading && (
          <p className="p-8 text-center text-[#666666]">주문을 불러오는 중입니다.</p>
        )}
        {isError && (
          <p className="p-8 text-center text-[#f2544b]">
            주문 목록을 불러오지 못했습니다.
          </p>
        )}
        {!isLoading && !isError && data?.results.length === 0 && (
          <p className="p-8 text-center text-[#666666]">주문이 없습니다.</p>
        )}
        {!isLoading && !isError && Boolean(data?.results.length) && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] border-collapse text-left">
              <thead className="bg-[#fafafa] text-sm text-[#666666]">
                <tr>
                  <th className="px-5 py-4">주문번호</th>
                  <th className="px-5 py-4">고객</th>
                  <th className="px-5 py-4">금액</th>
                  <th className="px-5 py-4">주문 상태</th>
                  <th className="px-5 py-4">결제 상태</th>
                  <th className="px-5 py-4">수령 방식</th>
                  <th className="px-5 py-4">구분</th>
                  <th className="px-5 py-4">일시</th>
                </tr>
              </thead>
              <tbody>
                {data?.results.map((order) => (
                  <tr key={order.id} className="border-t border-[#eeeeee] text-sm">
                    <td className="px-5 py-4 font-bold">{order.order_number}</td>
                    <td className="px-5 py-4 text-[#666666]">{order.user}</td>
                    <td className="px-5 py-4 font-bold">
                      {priceFormatter.format(order.total_price)}원
                    </td>
                    <td className="px-5 py-4">
                      {orderStatusLabel[order.status] ?? order.status}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-[#fff4f2] px-3 py-1 font-bold text-[#8a3a32]">
                        {paymentStatusLabel[order.payment_status] ??
                          order.payment_status}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      {fulfillmentLabel[order.fulfillment_method] ??
                        order.fulfillment_method}
                    </td>
                    <td className="px-5 py-4">
                      {order.is_test_order ? '테스트 주문' : '실제 주문'}
                    </td>
                    <td className="px-5 py-4 text-[#888888]">
                      {order.created_at.slice(0, 16).replace('T', ' ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AdminPageShell>
  )
}

export default AdminOrders
