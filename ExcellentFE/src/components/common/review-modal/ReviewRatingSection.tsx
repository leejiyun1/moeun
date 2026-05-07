import StarRating from '@/components/common/StarRating'
import type { TastingReview } from '@/types/feedback'

interface ReviewRatingSectionProps {
  review: TastingReview
  updateReview: (field: keyof TastingReview, value: number) => void
}

const ReviewRatingSection = ({
  review,
  updateReview,
}: ReviewRatingSectionProps) => {
  return (
    <div className="mt-12 flex w-full flex-col items-center">
      <p className="text-lg font-bold text-[#333333]">전체 평점</p>
      <StarRating
        size={51}
        showRatingValue={false}
        className="mt-5"
        rating={review.rating}
        onChange={(value) => updateReview('rating', value)}
      />
    </div>
  )
}

export default ReviewRatingSection
