import type { ProductTag } from '@/types/product'

export interface SearchFilters {
  keyword: string
  sweetness: number[]
  acidity: number[]
  body: number[]
  carbonation: number[]
  bitterness: number[]
  aroma: number[]
}

export interface Product {
  id: string
  name: string
  product_type: 'individual' | 'package'
  price: number
  original_price?: number | null
  discount?: number
  discount_rate?: number
  final_price: number
  is_on_sale: boolean
  main_image_url: string
  brewery_name?: string | null
  alcohol_type?: string | null
  tags: ProductTag[]
  is_tasting_available: boolean
  view_count: number
  like_count: number
  is_liked?: boolean
  status: string
  created_at: string
}

export interface SearchFormProps {
  keyword: string
  onKeywordChange: (keyword: string) => void
  onSearch: (keyword: string) => void
}

export interface SearchResultsProps {
  data: Product[]
  isLoading: boolean
  isError: boolean
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export interface SliderGroupProps {
  filters: SearchFilters
  onSliderChange: (key: keyof SearchFilters, value: number[]) => void
}
