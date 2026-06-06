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
    <div className="flex w-full flex-col gap-8 md:gap-[50px]">
      <div className="flex w-full flex-col gap-[10px]">
        <h2 className="text-[24px] font-bold text-[#333333] md:text-[32px]">
          {title}
        </h2>
        <div className="flex items-start justify-between gap-4 md:items-center">
          <h5 className="text-[15px] leading-6 text-[#666666] md:text-[18px]">
            {description}
          </h5>
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
