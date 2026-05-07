import Button from '@/components/common/Button'
import Modal from '@/components/common/Modal'
import ReviewRatingSection from '@/components/common/review-modal/ReviewRatingSection'
import ReviewSummaryForm from '@/components/common/review-modal/ReviewSummaryForm'
import useTastingReview from '@/hooks/order/useTastingReview'
import { useAuthStore } from '@/stores/authStore'

interface TastingReviewModalProps {
  isOpen: boolean
  onClose: () => void
  orderItemId?: number
}

const TastingReviewModal = ({
  isOpen,
  onClose,
  orderItemId,
}: TastingReviewModalProps) => {
  const {
    review,
    updateReview,
    comment,
    setComment,
    handleFileChange,
    imagePreviews,
    handleSubmitAndClose,
  } = useTastingReview(orderItemId, onClose)

  const { user } = useAuthStore()

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="시음 후기 작성"
      isCloseable
      className="review-modal-scroll h-[900px] w-170 overflow-auto"
    >
      <div className="mt-5 flex flex-col items-center justify-center text-lg text-[#666666]">
        <p>제품이 {user?.user_info?.nickname}님의 취향에 맞으셨나요?</p>
        <p>시음하며 느낀 점을 간단히 기록해주세요.</p>
        <p>후기는 다른 분들이 전통주를 고를 때 참고됩니다.</p>
      </div>
      <div className="w-full">
        <ReviewRatingSection
          review={review}
          updateReview={updateReview}
        />
        <ReviewSummaryForm
          comment={comment}
          setComment={setComment}
          handleFileChange={handleFileChange}
          imagePreviews={imagePreviews}
        />
        <Button
          variant="VARIANT1"
          onClick={handleSubmitAndClose}
          className="mt-15"
        >
          소중한 시음 후기 등록하고 적립금 받기
        </Button>
      </div>
    </Modal>
  )
}

export default TastingReviewModal
