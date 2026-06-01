import type { CardBaseProps } from '@/types/cardProps'
import CardList from '@/components/common/cards/CardList'

const MakgeolliPackageSection = ({
  makgeolliCards,
}: {
  makgeolliCards: CardBaseProps[]
}) => {
  return (
    <section className="py-16 md:py-25">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12 text-left">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            막걸리 패키지
          </h2>
          <p className="text-[#666666]">막걸리 러버들을 위한 전용 패키지</p>
        </div>
        <CardList type="default" cards={makgeolliCards} />
      </div>
    </section>
  )
}

export default MakgeolliPackageSection
