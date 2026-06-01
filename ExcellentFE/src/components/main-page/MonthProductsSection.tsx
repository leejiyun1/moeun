import CardList from '@/components/common/cards/CardList'
import type { CardBaseProps } from '@/types/cardProps'

const MonthProductsSection = ({
  monthCards,
}: {
  monthCards: CardBaseProps[]
}) => {
  return (
    <section className="py-14 md:py-16">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="flex flex-col items-start gap-8 lg:flex-row">
          <div className="w-full shrink-0 lg:w-80">
            <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
              이달의 전통주
            </h2>
            <p className="text-[#666666]">
              한 잔 취향이 추천하는 테스트를 통해
            </p>
            <p className="text-[#666666]">입맛에 맞는 술 찾아보세요</p>
          </div>
          <CardList type="default" cards={monthCards} columns={3} />
        </div>
      </div>
    </section>
  )
}

export default MonthProductsSection
