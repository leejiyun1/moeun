import type { SliderVariant } from '@/constants/sliderColors'
import type { SearchFilters } from '@/types/search'

export const PAGE_SIZE = 8

export const SLIDER_CONFIGS = [
  { filterKey: 'sweetness', variant: 'sweetness', label: '단\u00A0\u00A0\u00A0\u00A0맛' },
  { filterKey: 'acidity', variant: 'acidity', label: '산\u00A0\u00A0\u00A0\u00A0미' },
  { filterKey: 'body', variant: 'body', label: '바디감' },
  { filterKey: 'carbonation', variant: 'carbonation', label: '탄산감' },
  { filterKey: 'bitterness', variant: 'bitter', label: '쓴\u00A0\u00A0\u00A0\u00A0맛' },
  { filterKey: 'aroma', variant: 'aroma', label: '풍\u00A0\u00A0\u00A0\u00A0미' },
] as const satisfies readonly {
  filterKey: Extract<
    keyof SearchFilters,
    'sweetness' | 'acidity' | 'body' | 'carbonation' | 'bitterness' | 'aroma'
  >
  variant: SliderVariant
  label: string
}[]

export type SliderConfig = (typeof SLIDER_CONFIGS)[number]
