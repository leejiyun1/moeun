import useUserPostOrder from '@/hooks/cart/useUserPostOrder'
import Button from '@/components/common/Button'
import ItemRowContent from '@/components/common/ItemRowContent'
import { useUserCart } from '@/hooks/cart/useUserCart'
import { Equal } from 'lucide-react'
import useCartItem from '@/hooks/cart/useCartItem'
import { useStores } from '@/hooks/store/useStores'
import { cartApi } from '@/api/productApi'
import { useMutation } from '@tanstack/react-query'

const Cart = () => {
  const { data, invalidateCart } = useUserCart()
  const { data: stores = [] } = useStores()
  const { postOrderMutation } = useUserPostOrder()
  const updatePickupMutation = useMutation({
    mutationFn: ({
      itemId,
      pickup,
    }: {
      itemId: number
      pickup: {
        pickup_store_id?: number | null
        pickup_date?: string | null
      }
    }) => cartApi.UPDATE(String(itemId), pickup),
    onSuccess: invalidateCart,
  })
  const { onCheckChange, checkedTotalPrice, checkedItems } = useCartItem({
    data,
    onQuantityChange: invalidateCart,
    quantity: data?.cart_items?.reduce(
      (total, item) => total + item.quantity,
      0
    ),
  })

  const selectedCartItems =
    data?.cart_items?.filter((item) => checkedItems.includes(item.id)) ?? []
  const hasMissingPickup = selectedCartItems.some(
    (item) => !item.pickup_store || !item.pickup_date
  )

  return (
    <div className="mt-25 flex flex-col items-center justify-center">
      <h1 className="text-[40px] font-bold text-[#333333]">장바구니</h1>
      <ItemRowContent
        type="cart"
        items={data?.cart_items || []}
        onQuantityChange={invalidateCart}
        checkedItems={checkedItems}
        onCheckChange={onCheckChange}
        stores={stores}
        onPickupChange={(itemId, pickup) =>
          updatePickupMutation.mutate({ itemId, pickup })
        }
      />
      {data?.cart_items && data.cart_items.length > 0 && (
        <>
          <div className="mt-25 h-20 w-320 bg-[#f2f2f2]">
            <div className="flex h-full w-full items-center justify-center gap-7">
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
            className="mt-12 mb-25"
            onClick={() => {
              if (checkedItems.length === 0) {
                alert('결제할 상품을 선택해주세요.')
                return
              }
              if (hasMissingPickup) {
                alert('선택한 상품의 픽업 매장과 날짜를 모두 입력해주세요.')
                return
              }
              postOrderMutation.mutate(checkedItems)
            }}
            disabled={postOrderMutation.isPending || updatePickupMutation.isPending}
          >
            {postOrderMutation.isPending ? '결제 처리 중...' : '결제하기'}
          </Button>
        </>
      )}
    </div>
  )
}

export default Cart
