import type { CardBaseProps } from '@/types/cardProps'
import CardList from '@/components/common/cards/CardList'

const RegionalPackageSection = ({
  regionalCards,
}: {
  regionalCards: CardBaseProps[]
}) => {
  return (
    <section className="mb-24 py-16 md:mb-80 md:py-25">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12 text-left">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            지역 특산주 패키지
          </h2>
          <p className="text-[#666666]">
            대한민국 방방곡곡을 대표하는 전통주 패키지
          </p>
        </div>
        <CardList type="default" cards={regionalCards} />
      </div>
    </section>
  )
}

export default RegionalPackageSection
