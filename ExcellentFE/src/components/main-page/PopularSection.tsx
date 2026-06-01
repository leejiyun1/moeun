import CardList from '@/components/common/cards/CardList'
import type { CardBaseProps } from '@/types/cardProps'

const PopularSection = ({
  popularCards,
}: {
  popularCards: CardBaseProps[]
}) => {
  return (
    <section className="bg-[#f2f2f2] py-16 md:min-h-[704px] md:py-25">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            인기 패키지
          </h2>
          <p className="text-[#666666]">한 잔 취향 유저들의 Pick!</p>
        </div>
        <CardList type="default" cards={popularCards} carousel />
      </div>
    </section>
  )
}

export default PopularSection
