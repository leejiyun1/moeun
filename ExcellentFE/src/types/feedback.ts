import type { TasteScoreMap } from '@/types/tasteTypes'

export interface TastingReview {
  rating: number
  sweetness?: number
  acidity?: number
  body?: number
  carbonation?: number
  bitterness?: number
  aroma?: number
}

export interface TastingSubmitData {
  order_item_id: number
  overall_rating: number
  sweetness?: number
  acidity?: number
  body?: number
  carbonation?: number
  bitterness?: number
  aroma?: number
  comment?: string
  files?: File[] | null
}

export interface TasteProfile {
  id: number
  taste_scores: TasteScoreMap
  description: string
}
