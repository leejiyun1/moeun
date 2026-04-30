import { Link } from 'react-router-dom'
import type { CartItemRowProps } from '@/types/ItemRow/itemRows'
import PlusIcon from '@/assets/icons/cart/plus.svg?react'
import MinusIcon from '@/assets/icons/cart/minus.svg?react'
import Icon from '@/components/common/Icon'
import useCartItem from '@/hooks/cart/useCartItem'

const CartItemRow = ({
  id,
  detailId,
  img,
  name,
  quantity,
  price,
  pickupStoreId,
  pickupDate,
  pickupName,
  pickupAddress,
  pickupContact,
  stores = [],
  onPickupChange,
  onCheckChange,
  checked,
  onQuantityChange,
}: CartItemRowProps) => {
  const { localQuantity, onIncreaseQuantity, onDecreaseQuantity, isUpdating } =
    useCartItem({
      quantity: quantity || 0,
      id,
      onQuantityChange,
    })

  return (
    <div className="flex items-center border-b border-[#e1e1e1] py-5 text-center text-[#333333]">
      <div className="flex w-[40%] min-w-[250px] items-center gap-12">
        <input
          type="checkbox"
          checked={checked || false}
          onChange={(e) => onCheckChange?.(e.target.checked)}
          className="ml-12 h-5 w-5 accent-[#f2544b]"
        />
        <Link to={`/product/${detailId}`}>
          <img
            src={img || '상품 이미지'}
            alt={name || '상품 이름'}
            className="h-25 w-25 rounded border border-[#d9d9d9]"
          />
        </Link>
        <p className="text-left text-lg font-bold">{name || '상품 이름'}</p>
      </div>

      {/* 수량 조절 */}
      <div className="mx-auto inline-flex h-8 w-20 items-center justify-center gap-1 rounded-[5px] bg-[#f6f6f6]">
        <button aria-label="수량 감소" onClick={onDecreaseQuantity}>
          <Icon
            icon={MinusIcon}
            size={16}
            wrapperClassName={'rounded-[4px] bg-[#cccccc] cursor-not-allowed'}
          />
        </button>
        <span className="w-6 text-center">{localQuantity}</span>
        <button
          aria-label="수량 증가"
          onClick={onIncreaseQuantity}
          disabled={isUpdating}
        >
          <Icon
            icon={PlusIcon}
            size={16}
            wrapperClassName={'rounded-[4px] bg-[#000000] cursor-not-allowed'}
          />
        </button>
      </div>
      <div className="w-[15%] min-w-[80px] font-medium">
        {parseInt(String(price ?? '0'), 10).toLocaleString()}원
      </div>

      <div className="w-[25%] min-w-[150px] text-[#666666]">
        <select
          value={pickupStoreId ?? ''}
          onChange={(event) =>
            onPickupChange?.({
              pickup_store_id: event.target.value
                ? Number(event.target.value)
                : null,
            })
          }
          className="mb-2 w-full rounded border border-[#d9d9d9] px-3 py-2 text-sm text-[#333333]"
          aria-label={`${name} 픽업 매장 선택`}
        >
          <option value="">픽업 매장 선택</option>
          {stores.map((store) => (
            <option key={store.id} value={store.id}>
              {store.name}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={pickupDate ?? ''}
          onChange={(event) =>
            onPickupChange?.({ pickup_date: event.target.value || null })
          }
          className="mb-2 w-full rounded border border-[#d9d9d9] px-3 py-2 text-sm text-[#333333]"
          aria-label={`${name} 픽업 날짜 선택`}
        />
        {pickupName ? (
          <>
            <p className="text-sm">{pickupAddress}</p>
            <p className="text-sm">{pickupContact}</p>
          </>
        ) : (
          <p className="text-sm text-[#f2544b]">
            주문 전 픽업 정보를 선택해주세요.
          </p>
        )}
      </div>
    </div>
  )
}

export default CartItemRow
