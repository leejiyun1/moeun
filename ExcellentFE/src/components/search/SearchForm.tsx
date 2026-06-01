import type { SearchFormProps } from '@/types/search'
import Input from '@/components/common/Input'

const SearchForm = ({
  keyword,
  onKeywordChange,
  onSearch,
}: SearchFormProps) => {
  const handleSearch = (e?: React.FormEvent | React.MouseEvent) => {
    if (e) e.preventDefault()
    onSearch(keyword)
  }
  return (
    <div className="flex flex-col items-center gap-8 px-5 md:gap-[50px]">
      <h1 className="mt-16 text-[32px] font-bold text-[#333] md:mt-25 md:text-[40px]">
        제품 검색
      </h1>
      <Input
        type="text"
        value={keyword}
        onChange={(e) => onKeywordChange(e.target.value)}
        variant="search"
        onSearch={handleSearch}
        placeholder="검색어를 입력하세요."
      />
    </div>
  )
}

export default SearchForm
