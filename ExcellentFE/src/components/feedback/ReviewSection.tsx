import ResetIcon from '@/assets/icons/feedback/reset.svg?react'
import CardList from '@/components/common/cards/CardList'
import Icon from '@/components/common/Icon'
import type { ReviewCardProps } from '@/types/cardProps'

interface ReviewSectionProps {
  title: string
  description: string
  cards: ReviewCardProps[]
  onReset: () => void
}

const ReviewSection = ({
  title,
  description,
  cards,
  onReset,
}: ReviewSectionProps) => {
  return (
    <div className="flex flex-col gap-[50px]">
      <div className="flex w-320 flex-col gap-[10px]">
        <h2 className="text-[32px] font-bold text-[#333333]">{title}</h2>
        <div className="flex items-center justify-between">
          <h5 className="text-[18px] text-[#666666]">{description}</h5>
          <button type="button" onClick={onReset}>
            <Icon icon={ResetIcon} size={40} />
          </button>
        </div>
      </div>
      <CardList type="review" cards={cards} />
    </div>
  )
}

export default ReviewSection
