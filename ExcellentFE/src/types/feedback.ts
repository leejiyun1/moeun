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

export interface TasteProfile {
  id: number
  taste_scores: TasteScoreMap
  description: string
}
