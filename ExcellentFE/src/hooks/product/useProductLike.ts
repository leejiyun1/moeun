import { toggleProductLike } from '@/api/productApi'
import { useState } from 'react'

export const useProductLike = (
  productId?: string | number,
  initialLiked = false
) => {
  const [isLiked, setIsLiked] = useState(initialLiked)
  const [isPending, setIsPending] = useState(false)

  const toggleLike = async () => {
    if (!productId || isPending) return

    const previousLiked = isLiked
    setIsLiked((prev) => !prev)
    setIsPending(true)

    try {
      const result = await toggleProductLike(productId)
      setIsLiked(result.is_liked)
    } catch {
      setIsLiked(previousLiked)
    } finally {
      setIsPending(false)
    }
  }

  return {
    isLiked,
    isPending,
    toggleLike,
  }
}
