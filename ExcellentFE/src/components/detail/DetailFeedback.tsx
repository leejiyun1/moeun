import StarRating from '@/components/common/StarRating'
import { useProductFeedbacks } from '@/hooks/feedback/useProductFeedbacks'

interface DetailFeedbackProps {
  productId: string
  reviewCount: number
}

const DetailFeedback = ({ productId, reviewCount }: DetailFeedbackProps) => {
  const { data: feedbacks = [], isLoading, isError } = useProductFeedbacks(productId)

  return (
    <div className="mb-[100px]">
      <div className="flex items-center justify-between border-b pb-5">
        <h3 className="text-lg font-bold">상품 후기</h3>
        <span className="text-sm text-[#666666]">총 {reviewCount}개</span>
      </div>

      {isLoading && (
        <div className="mt-[35px] rounded-[10px] bg-[#f7f7f7] py-12 text-center text-[#666666]">
          후기를 불러오는 중입니다.
        </div>
      )}

      {isError && (
        <div className="mt-[35px] rounded-[10px] bg-[#fff7f6] py-12 text-center text-[#f2544b]">
          후기를 불러오지 못했습니다.
        </div>
      )}

      {!isLoading && !isError && feedbacks.length === 0 && (
        <div className="mt-[35px] rounded-[10px] bg-[#f7f7f7] py-12 text-center text-[#666666]">
          아직 등록된 상품 후기가 없습니다.
        </div>
      )}

      {!isLoading && !isError && feedbacks.length > 0 && (
        <div className="mt-[35px] flex flex-col gap-5">
          {feedbacks.map((feedback) => (
            <article
              key={feedback.id}
              className="rounded-[14px] border border-[#e5e5e5] bg-white p-6"
            >
              <div className="mb-4 flex items-start justify-between gap-4">
                <div>
                  <div className="mb-2 flex items-center gap-3">
                    <StarRating
                      readOnly
                      defaultRating={feedback.rating}
                      size={18}
                      showRatingValue={false}
                    />
                    <span className="text-sm text-[#888888]">
                      {feedback.created_at.slice(0, 10)}
                    </span>
                  </div>
                  <p className="font-bold text-[#333333]">
                    {feedback.masked_username}
                  </p>
                </div>
                {feedback.image_url && (
                  <img
                    src={feedback.image_url}
                    alt={`${feedback.product_name} 후기 이미지`}
                    className="h-22 w-22 rounded-[10px] object-cover"
                  />
                )}
              </div>
              <p className="whitespace-pre-line text-[#555555]">
                {feedback.comment ?? ''}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default DetailFeedback
