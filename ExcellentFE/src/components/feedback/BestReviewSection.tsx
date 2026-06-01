import CardList from '@/components/common/cards/CardList'
import type { BestReviewCardProps } from '@/types/cardProps'

interface BestReviewSectionProps {
  cards: BestReviewCardProps[]
}

const BestReviewSection = ({ cards }: BestReviewSectionProps) => {
  return (
    <div className="flex h-220 w-full flex-col items-center bg-[#F2F2F2] px-60 py-34">
      <h1 className="mb-[60px] text-[40px] font-bold text-[#333333]">
        나와 취향이 닮은 사람의 후기
      </h1>
      <div>
        <CardList
          type="best"
          cards={cards}
          carousel
          slidesToShow={1}
          gap="200px"
        />
      </div>
    </div>
  )
}

export default BestReviewSection
