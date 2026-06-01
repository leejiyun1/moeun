import type { CardBaseProps } from '@/types/cardProps'
import CardList from '@/components/common/cards/CardList'
import { useAuthStore } from '@/stores/authStore'

const RecommendedPackageSection = ({
  recommendedCards,
}: {
  recommendedCards: CardBaseProps[]
}) => {
  const { user } = useAuthStore()
  return (
    <section className="py-14 md:py-16">
      <div className="mx-auto w-full max-w-[1280px] px-5 sm:px-8 lg:px-10 xl:px-0">
        <div className="mb-12">
          <h2 className="mb-4 text-2xl font-bold text-[#333333] md:text-3xl">
            추천 패키지
          </h2>
          <p className="text-[#666666]">
            오직 {user?.user_info?.nickname || '게스트'}만의 취향을 반영한
            패키지
          </p>
        </div>
        <CardList type="default" cards={recommendedCards} />
      </div>
    </section>
  )
}

export default RecommendedPackageSection
