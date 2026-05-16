import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { SearchFilters } from '@/types/search'

export const useSearchFilters = () => {
  const [searchParams] = useSearchParams()
  const [filters, setFilters] = useState<SearchFilters>({
    keyword: '',
    sweetness: [0],
    acidity: [0],
    body: [0],
    carbonation: [0],
    bitterness: [0],
    aroma: [0],
  })

  useEffect(() => {
    const queryParams = Object.fromEntries(searchParams.entries())

    setFilters({
      keyword: queryParams.search || '',
      sweetness: [Number(queryParams.sweetness) || 0],
      acidity: [Number(queryParams.acidity) || 0],
      body: [Number(queryParams.body) || 0],
      carbonation: [Number(queryParams.carbonation) || 0],
      bitterness: [Number(queryParams.bitterness) || 0],
      aroma: [Number(queryParams.aroma) || 0],
    })

    if (Object.keys(queryParams).length === 0) {
      setFilters({
        keyword: '',
        sweetness: [0],
        acidity: [0],
        body: [0],
        carbonation: [0],
        bitterness: [0],
        aroma: [0],
      })
    }
  }, [searchParams])

  const updateKeyword = (keyword: string) => {
    setFilters((prev) => ({ ...prev, keyword }))
  }

  const updateSliderValue = (key: keyof SearchFilters, value: number[]) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  return {
    filters,
    updateKeyword,
    updateSliderValue,
  }
}
