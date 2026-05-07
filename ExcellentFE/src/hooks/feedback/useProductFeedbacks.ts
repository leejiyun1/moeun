import { feedbackApi } from '@/api/feedback'
import type { Feedback } from '@/api/feedback/types'
import { useQuery } from '@tanstack/react-query'

export const useProductFeedbacks = (productId?: string | number) => {
  return useQuery<Feedback[]>({
    queryKey: ['product-feedbacks', productId],
    queryFn: () => feedbackApi.fetchProductFeedbacks(productId as string),
    enabled: Boolean(productId),
    staleTime: 5 * 60 * 1000,
  })
}
