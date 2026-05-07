import type { TasteScoreMap } from '@/types/tasteTypes'

export interface TastingReview {
  rating: number
}

export interface TastingSubmitData {
  order_item_id: number
  overall_rating: number
  positive_tags: string[]
  negative_tags: string[]
  comment?: string
  files?: File[] | null
}

export interface TasteProfile {
  id: number
  taste_scores: TasteScoreMap
  description: string
}
