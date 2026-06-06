import CardList from '@/components/common/cards/CardList'
import type { BestReviewCardProps } from '@/types/cardProps'

interface BestReviewSectionProps {
  cards: BestReviewCardProps[]
}

const BestReviewSection = ({ cards }: BestReviewSectionProps) => {
  return (
    <div className="flex w-full flex-col items-center bg-[#F2F2F2] px-5 py-14 sm:px-8 md:px-10 md:py-20 xl:min-h-220 xl:px-40 xl:py-34 2xl:px-60">
      <h1 className="mb-10 text-center text-[26px] leading-9 font-bold text-[#333333] md:mb-[60px] md:text-[34px] xl:text-[40px]">
        나와 취향이 닮은 사람의 후기
      </h1>
      <div className="w-full">
        <CardList
          type="best"
          cards={cards}
          carousel
          slidesToShow={1}
          gap="clamp(24px, 8vw, 200px)"
        />
      </div>
    </div>
  )
}

export default BestReviewSection
