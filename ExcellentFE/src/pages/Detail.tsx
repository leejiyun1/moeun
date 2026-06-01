import DetailProduct from '@/components/detail/DetailProduct'
import DetailInformation from '@/components/detail/DetailInformation'
import DetailFeedback from '@/components/detail/DetailFeedback'
import { useDetailPage } from '@/hooks/home/useDetailPage'

const Detail = () => {
  const {
    data,
    isLoading,
    error,
    localQuantity,
    onIncreaseQuantity,
    onDecreaseQuantity,
    handleAddToCart,
    handlePurchase,
  } = useDetailPage()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        로딩 중...
      </div>
    )
  }
  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        오류 발생: {error.message}
      </div>
    )
  }
  if (!data) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        상품 정보를 찾을 수 없습니다.
      </div>
    )
  }

  return (
    <div className="mx-auto mt-16 flex w-full max-w-[1280px] flex-col gap-16 px-5 sm:px-8 md:mt-25 md:gap-25 lg:px-10 xl:px-0">
      <DetailProduct
        data={data}
        quantity={localQuantity}
        onIncreaseQuantity={onIncreaseQuantity}
        onDecreaseQuantity={onDecreaseQuantity}
        onAddCart={handleAddToCart}
        onPurchase={handlePurchase}
      />

      <DetailInformation data={data} />

      <div>
        <div className="border-b-2 pb-5 text-lg font-bold">
          구매 및 수령 방식
        </div>
        <div className="mt-[35px] flex min-h-40 w-full items-center justify-center bg-[#f2f2f2] px-5 text-center">
          <span className="font-semibold">수도권 픽업 가능한 상품입니다.</span>
        </div>
      </div>

      <DetailFeedback productId={data.id} reviewCount={data.review_count} />
    </div>
  )
}

export default Detail
