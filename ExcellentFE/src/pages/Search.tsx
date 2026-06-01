import SearchForm from '@/components/search/SearchForm'
import { useSearchFilters } from '@/hooks/useSearchFilters'
import { buildSearchParamsRecommended } from '@/utils/searchParams'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Button from '@/components/common/Button'
import SliderGroup from '@/components/search/SliderGroup'
import SearchResults from '@/components/search/SearchResults'
import { useProductSearch } from '@/hooks/useProductSearch'
import { usePagination } from '@/hooks/usePagination'
import { PAGE_SIZE } from '@/constants/search'
import type { Product } from '@/types/search'

const Search = () => {
  const [searchParams] = useSearchParams()
  const { filters, updateKeyword, updateSliderValue } = useSearchFilters()
  const navigate = useNavigate()

  const queryParams = Object.fromEntries(searchParams.entries())
  const hasQuery = Object.keys(queryParams).length > 0

  const { data, isLoading, isError } = useProductSearch(
    hasQuery ? queryParams : null
  )

  const productList: Product[] = (data?.results ?? []).map((item) => ({
    id: item.id,
    name: item.name,
    product_type: item.product_type,
    price: item.price,
    original_price: item.original_price ?? null,
    discount: item.discount ?? 0,
    discount_rate: item.discount_rate ?? 0,
    final_price: item.final_price,
    is_on_sale: item.is_on_sale,
    main_image_url: item.main_image_url,
    brewery_name: item.brewery_name ?? null,
    alcohol_type: item.alcohol_type ?? null,
    tags: item.tags ?? [],
    is_tasting_available: item.is_tasting_available,
    view_count: item.view_count,
    like_count: item.like_count,
    is_liked: item.is_liked,
    status: item.status,
    created_at: item.created_at,
  }))

  const { currentPage, totalPages, paginatedData, handlePageChange } =
    usePagination<Product>({
      items: productList,
      pageSize: PAGE_SIZE,
    })

  const handleKeywordSearch = (searchValue: string) => {
    const queryString = buildSearchParamsRecommended({
      ...filters,
      keyword: searchValue, // 이 부분은 buildSearchParamsRecommended 함수 내부에서 처리
    })
    navigate(`/search?${queryString}`)
  }

  // 🎛 상세 필터 적용
  const handleFilterSearch = () => {
    const queryString = buildSearchParamsRecommended({ ...filters })
    navigate(`/search?${queryString}`)
  }

  return (
    <div>
      <SearchForm
        keyword={filters.keyword}
        onKeywordChange={updateKeyword}
        onSearch={handleKeywordSearch}
      />
      <div className="mb-20 flex flex-col items-center px-5 md:mb-25">
        <div className="mb-[17px] flex w-full max-w-[1280px] flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-[24px] font-bold text-[#333333]">상세 검색</h2>
          <Button
            onClick={handleFilterSearch}
            variant="VARIANT7"
            className="h-[39px] w-full sm:w-[117px]"
          >
            필터 적용하기
          </Button>
        </div>

        <div className="flex min-h-[266px] w-full max-w-[1280px] items-center justify-center rounded-[6px] bg-[#F2F2F2] px-5 py-8 md:px-8">
          <SliderGroup filters={filters} onSliderChange={updateSliderValue} />
        </div>
      </div>

      <SearchResults
        data={paginatedData}
        isLoading={isLoading}
        isError={isError}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  )
}

export default Search
