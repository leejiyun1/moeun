import BestReviewSection from '@/components/feedback/BestReviewSection'
import ReviewSection from '@/components/feedback/ReviewSection'
import { useFeedbackList } from '@/hooks/useFeedbackList'
import { mapToBestReviewCards, mapToReviewCards } from '@/utils/feedbackMappers'

export const Feedback = () => {
  const {
    popular,
    recent,
    personalized,
    refetchPersonalized,
    refetchRecent,
    isLoading,
    isError,
  } = useFeedbackList()

  if (isLoading) return <p>로딩중...</p>
  if (isError) return <p>데이터를 불러오는 데 실패했습니다.</p>

  return (
    <div>
      <BestReviewSection cards={mapToBestReviewCards(popular)} />

      <div className="m-auto my-25 flex flex-col items-center gap-25">
        <div className="m-auto my-25 flex flex-col items-center gap-25">
          <ReviewSection
            title="실시간 후기"
            description="한잔 취향을 이용한 고객님들의 실시간 후기"
            cards={mapToReviewCards(recent, '실시간 후기')}
            onReset={refetchRecent}
          />
          <ReviewSection
            title="나의 비슷한 취향 후기"
            description="나와 비슷한 취향의 고객님들의 후기"
            cards={mapToReviewCards(personalized, '나의 비슷한 취향 후기')}
            onReset={refetchPersonalized}
          />
        </div>
      </div>
    </div>
  )
}

export default Feedback
