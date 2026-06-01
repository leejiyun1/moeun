import CardList from '@/components/common/cards/CardList'
import Pagination from '@/components/common/Pagination'
import type { CardBaseProps } from '@/types/cardProps'
import type { SearchResultsProps } from '@/types/search'

const SearchResults = ({
  data,
  isLoading,
  isError,
  currentPage,
  totalPages,
  onPageChange,
}: SearchResultsProps) => {
  const productCards: CardBaseProps[] = data.map((product) => ({
    id: product.id,
    productType: product.product_type === 'package' ? 'PACKAGE' : 'PRODUCT',
    imgSrc: product.main_image_url,
    imgAlt: product.name,
    title: product.name,
    subtitle: product.brewery_name ?? undefined,
    price: product.price,
    isLiked: product.is_liked,
  }))

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center text-lg font-medium">로딩 중...</div>
    }

    if (isError) {
      return (
        <div className="text-center text-lg font-medium text-red-600">
          에러가 발생했습니다.
        </div>
      )
    }

    return (
      <div>
        <CardList type="default" cards={productCards} />

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
          className="mt-20"
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center px-5 sm:px-8 lg:px-10 xl:px-0">
      <div className="w-full max-w-[1280px]">
        <h2 className="mb-[19px] text-[24px] font-bold text-[#333333]">
          검색 결과
        </h2>
        <hr className="mb-5 w-full border-2 border-[#000000]" />
      </div>
      <div className="mb-25 flex w-full max-w-[1280px] flex-col gap-20">
        {renderContent()}
      </div>
    </div>
  )
}

export default SearchResults
