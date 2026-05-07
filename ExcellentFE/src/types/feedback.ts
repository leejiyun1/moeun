import type { TasteScoreMap } from '@/types/tasteTypes'

export interface TastingReview {
  rating: number
}

export interface TasteProfile {
  id: number
  taste_scores: TasteScoreMap
  description: string
}
