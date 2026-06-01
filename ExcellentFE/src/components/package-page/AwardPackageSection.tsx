import type { CardBaseProps } from '@/types/cardProps'
import CardList from '@/components/common/cards/CardList'

const AwardPackageSection = ({
  awardCards,
}: {
  awardCards: CardBaseProps[]
}) => {
  return (
    <section className="bg-[#f2f2f2] py-16 md:min-h-[704px] md:py-25">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            주류 대상 수상 5종 패키지
          </h2>
          <p className="text-[#666666]">수상 대상 수상 등급 패키지</p>
        </div>
        <CardList type="default" cards={awardCards} />
      </div>
    </section>
  )
}

export default AwardPackageSection
