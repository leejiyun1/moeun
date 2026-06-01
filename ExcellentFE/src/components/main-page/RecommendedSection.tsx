import CardList from '@/components/common/cards/CardList'
import type { CardBaseProps } from '@/types/cardProps'

const RecommendedSection = ({
  recommendedCards,
}: {
  recommendedCards: CardBaseProps[]
}) => {
  return (
    <section className="mb-24 py-16 md:mb-80 md:py-25">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12 text-left">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            추천 전통주
          </h2>
          <p className="text-[#666666]">한 잔 취향에서 엄선한 추천 전통주</p>
        </div>
        <CardList type="default" cards={recommendedCards} />
      </div>
    </section>
  )
}

export default RecommendedSection
