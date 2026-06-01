import { Minus, Plus } from 'lucide-react'
import DetailCard from '@/components/common/cards/DetailCard'
import StarRating from '@/components/common/StarRating'
import Button from '@/components/common/Button'
import type { ProductDetail } from '@/types/product'
import { cn } from '@/utils/cn'

interface DetailProductProps {
  data: ProductDetail
  quantity: number
  onIncreaseQuantity: () => void
  onDecreaseQuantity: () => void
  isDecreaseDisabled?: boolean
  onAddCart: () => void
  onPurchase: () => void
}

const DetailProduct = ({
  data,
  quantity,
  onIncreaseQuantity,
  onDecreaseQuantity,
  isDecreaseDisabled,
  onAddCart,
  onPurchase,
}: DetailProductProps) => {
  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
      <DetailCard
        id={data.id}
        className="mx-auto aspect-square h-auto w-full max-w-[560px]"
        imgSrc={
          Array.isArray(data.images)
            ? data.images.find((img) => img.is_main)?.image_url || ''
            : (data.images as unknown as string)
        }
        imgAlt={data.name}
        isLiked={data.is_liked}
      />

      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-4 border-b pb-4 md:grid-cols-2">
          <div className="md:ml-6">
            <h1 className="mb-3 text-[32px] leading-tight font-bold text-[#333333] md:text-[40px]">
              {data.name}
            </h1>
            <div className="flex items-center gap-3">
              <span className="flex h-[26px] w-[45px] items-center justify-center rounded-[5px] bg-[#ffe5e3] text-sm font-bold text-[#f2544b]">
                -{data.discount_rate}%
              </span>
              <span className="text-[29px] font-bold text-[#333333]">
                {data.price.toLocaleString()}원
              </span>
              {data.original_price !== null && (
                <span className="ml-2 text-sm text-gray-400 line-through">
                  {data.original_price.toLocaleString()}원
                </span>
              )}
            </div>
          </div>
          <div className="mb-3 flex items-center gap-2 md:mr-2 md:justify-end">
            <StarRating defaultRating={5} readOnly />
            <span className="mr-2 text-sm text-[#666666] underline">
              ({data.review_count}개의 리뷰)
            </span>
          </div>
        </div>

        <div className="mt-8 flex flex-col gap-6 border-b border-[#D9D9D9] pb-5">
          <div className="flex items-center">
            <div>수량</div>
            <div className="ml-10 inline-flex h-8 w-20 items-center justify-center rounded-[5px] bg-[#f6f6f6] md:ml-[110px]">
              <button
                aria-label="수량 감소"
                onClick={onDecreaseQuantity}
                disabled={isDecreaseDisabled}
                className={cn(
                  'flex h-[15px] w-[15px] cursor-pointer items-center justify-center rounded-[4px]',
                  isDecreaseDisabled
                    ? 'cursor-not-allowed bg-[#e1e1e1]'
                    : 'bg-[#e1e1e1]'
                )}
              >
                <Minus size={16} />
              </button>
              <span className="w-6 text-center">{quantity}</span>
              <button
                aria-label="수량 증가"
                onClick={onIncreaseQuantity}
                className="flex h-[15px] w-[15px] cursor-pointer items-center justify-center rounded-[4px] bg-[#000000] text-white"
              >
                <Plus size={16} />
              </button>
            </div>
          </div>

          <p className="rounded bg-[#fff7f6] px-4 py-3 text-sm text-[#f2544b]">
            픽업 매장과 날짜는 장바구니에서 선택할 수 있습니다.
          </p>
        </div>

        <div className="mt-6">
          <div className="mb-9 flex items-center justify-between">
            <span className="text-[#666666]">총 상품 금액</span>
            <span className="text-[30px] font-bold text-[#333333]">
              {(data.price * quantity).toLocaleString()}원
            </span>
          </div>

          <div className="flex flex-col gap-[10px] sm:flex-row">
            <Button variant="VARIANT12" className="w-full" onClick={onAddCart}>
              장바구니
            </Button>
            <Button variant="VARIANT13" className="w-full" onClick={onPurchase}>
              구매하기
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DetailProduct
