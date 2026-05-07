export interface FeedbackRequest {
  order_item_id: number
  overall_rating: number
  comment?: string
  files: File[] | null
}

export interface Feedback {
  id: number
  product_id?: string
  order_item: number | string
  rating: number
  comment?: string | null
  image_url?: string
  product_name: string
  masked_username: string
  has_image?: boolean
  view_count?: number
  is_liked?: boolean
  created_at: string
  updated_at?: string
}

export type FeedbackResponse = Feedback[]
