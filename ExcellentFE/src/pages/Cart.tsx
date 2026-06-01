import useUserPostOrder from '@/hooks/cart/useUserPostOrder'
import Button from '@/components/common/Button'
import ItemRowContent from '@/components/common/ItemRowContent'
import { useUserCart } from '@/hooks/cart/useUserCart'
import { Equal } from 'lucide-react'
import useCartItem from '@/hooks/cart/useCartItem'
import { useStores } from '@/hooks/store/useStores'
import { useState } from 'react'

const Cart = () => {
  const { data, invalidateCart } = useUserCart()
  const { data: stores = [] } = useStores()
  const { postOrderMutation } = useUserPostOrder()
  const [pickupStoreId, setPickupStoreId] = useState<number | null>(null)
  const [pickupDate, setPickupDate] = useState('')
  const { onCheckChange, checkedTotalPrice, checkedItems } = useCartItem({
    data,
    onQuantityChange: invalidateCart,
    quantity: data?.cart_items?.reduce(
      (total, item) => total + item.quantity,
      0
    ),
  })

  const hasMissingPickup = !pickupStoreId || !pickupDate

  return (
    <div className="mt-16 flex flex-col items-center justify-center px-5 md:mt-25">
      <h1 className="text-[32px] font-bold text-[#333333] md:text-[40px]">
        장바구니
      </h1>
      <ItemRowContent
        type="cart"
        items={data?.cart_items || []}
        onQuantityChange={invalidateCart}
        checkedItems={checkedItems}
        onCheckChange={onCheckChange}
      />
      {data?.cart_items && data.cart_items.length > 0 && (
        <>
          <section className="mt-12 w-full max-w-[1280px] rounded-2xl border border-[#e1e1e1] bg-white px-5 py-6 text-[#333333] md:px-10 md:py-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold">수령 정보</h2>
              <p className="mt-2 text-sm text-[#666666]">
                이번 주문 전체에 적용할 픽업 매장과 날짜를 선택해주세요.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <label className="flex flex-col gap-2 text-sm font-medium">
                픽업 매장
                <select
                  value={pickupStoreId ?? ''}
                  onChange={(event) =>
                    setPickupStoreId(
                      event.target.value ? Number(event.target.value) : null
                    )
                  }
                  className="h-12 rounded border border-[#d9d9d9] px-4 text-[#333333]"
                >
                  <option value="">픽업 매장 선택</option>
                  {stores.map((store) => (
                    <option key={store.id} value={store.id}>
                      {store.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-2 text-sm font-medium">
                픽업 날짜
                <input
                  type="date"
                  value={pickupDate}
                  onChange={(event) => setPickupDate(event.target.value)}
                  className="h-12 rounded border border-[#d9d9d9] px-4 text-[#333333]"
                />
              </label>
            </div>
          </section>
          <div className="mt-16 min-h-20 w-full max-w-[1280px] bg-[#f2f2f2] md:mt-25">
            <div className="flex h-full w-full flex-col items-center justify-center gap-4 px-5 py-5 md:flex-row md:gap-7 md:py-0">
              <div className="text-[#333333]">
                상품금액 합계
                <span className="ml-3 text-2xl font-bold">
                  {checkedTotalPrice.toLocaleString()}원
                </span>
              </div>
              <div className="flex h-7 w-7 items-center justify-center rounded-[50%] bg-[#f2544b] text-center text-lg font-bold text-[#ffffff]">
                <Equal size={15} strokeWidth={4} />
              </div>
              <div className="text-[#333333]">
                총 결제 금액
                <span className="ml-3 text-2xl font-bold">
                  {checkedTotalPrice.toLocaleString()}원
                </span>
              </div>
            </div>
          </div>
          <Button
            variant="VARIANT4"
            className="mt-12 mb-25 w-full max-w-35"
            onClick={() => {
              if (checkedItems.length === 0) {
                alert('결제할 상품을 선택해주세요.')
                return
              }
              if (hasMissingPickup) {
                alert('이번 주문의 픽업 매장과 날짜를 모두 입력해주세요.')
                return
              }
              postOrderMutation.mutate({
                item_ids: checkedItems,
                fulfillment_method: 'PICKUP',
                pickup_store_id: pickupStoreId,
                pickup_date: pickupDate,
              })
            }}
            disabled={postOrderMutation.isPending}
          >
            {postOrderMutation.isPending
              ? '테스트 결제 처리 중...'
              : '테스트 결제하기'}
          </Button>
        </>
      )}
    </div>
  )
}

export default Cart
