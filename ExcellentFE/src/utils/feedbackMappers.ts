import type { Feedback } from '@/api/feedback/types'
import type { BestReviewCardProps, ReviewCardProps } from '@/types/cardProps'

export const mapToBestReviewCards = (
  data: Feedback[] | undefined
): BestReviewCardProps[] =>
  data?.map((item) => ({
    product_id: String(item.product_id),
    product_name: item.product_name ?? '',
    imgSrc: item.image_url || '',
    imgAlt: item.product_name ?? '모은 주류',
    review: item.comment ?? '',
    userId: item.masked_username ?? '',
    date: item.created_at ?? '',
    defaultRating: item.rating ?? 0,
    isLiked: item.is_liked,
  })) ?? []

export const mapToReviewCards = (
  data: Feedback[] | undefined,
  modalTitle: string
): ReviewCardProps[] =>
  data?.map((item) => ({
    id: String(item.id),
    product_id: String(item.product_id),
    product_name: item.product_name ?? '',
    imgSrc: item.image_url || undefined,
    imgAlt: item.product_name ?? '모은 주류',
    userId: item.masked_username,
    review: item.comment ?? undefined,
    defaultRating: item.rating,
    date: item.created_at,
    modalTitle,
  })) ?? []
