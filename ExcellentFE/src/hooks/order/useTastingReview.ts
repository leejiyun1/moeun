import { useState } from 'react'
import useSubmitFeedback from '@/hooks/order/useSubmitFeedback'
import type { TastingReview } from '@/types/feedback'
import type { FeedbackRequest } from '@/api/feedback/types'

const INITIAL_REVIEW_STATE: TastingReview = {
  rating: 0,
}

const MAX_IMAGES = 3

const useTastingReview = (orderItemId?: number, onClose?: () => void) => {
  const [review, setReview] = useState<TastingReview>(INITIAL_REVIEW_STATE)
  const [files, setFiles] = useState<File[]>([])
  const [imagePreviews, setImagePreviews] = useState<string[]>([])
  const [comment, setComment] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const mutation = useSubmitFeedback()

  const updateReview = (field: keyof TastingReview, value: number) => {
    setReview((prev) => ({ ...prev, [field]: value }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
    if (!selectedFiles) return

    const fileArray = Array.from(selectedFiles)
    const totalCount = imagePreviews.length + fileArray.length

    if (totalCount > MAX_IMAGES) {
      alert(`최대 ${MAX_IMAGES}개의 이미지만 업로드할 수 있습니다.`)
      return
    }

    setFiles((prevFiles) => {
      const newFiles = [...prevFiles, ...fileArray]
      return newFiles
    })

    fileArray.forEach((file) => {
      const reader = new FileReader()
      reader.onload = () => {
        setImagePreviews((prev) => [...prev, reader.result as string])
      }
      reader.readAsDataURL(file)
    })
    e.target.value = ''
  }

  const validateReview = (): boolean => {
    return review.rating > 0 && comment.trim().length > 0
  }

  const createSubmitData = (): FeedbackRequest => {
    return {
      order_item_id: Number(orderItemId ?? 0),
      overall_rating: review.rating,
      comment,
      files: files.length > 0 ? files : null,
    }
  }

  const resetForm = () => {
    setReview(INITIAL_REVIEW_STATE)
    setFiles([])
    setImagePreviews([])
    setComment('')
  }

  const openModal = () => setIsOpen(true)

  const closeModal = () => {
    setIsOpen(false)
    resetForm()
  }

  const handleSubmit = () => {
    if (!validateReview()) {
      /* TODO: ux적으로 좋지 않음 추후 개선 필요 */
      alert('평점과 후기를 입력해주세요.')
      return false
    }

    if (!orderItemId) {
      alert('유효하지 않은 주문 항목입니다.')
      return false
    }

    const submitData = createSubmitData()
    mutation.mutate(submitData)
    resetForm()
    closeModal()
    return true
  }

  const handleSubmitAndClose = () => {
    if (handleSubmit()) {
      onClose?.()
    }
  }

  return {
    review,
    comment,
    isOpen,
    imagePreviews,
    maxImages: MAX_IMAGES,
    updateReview,
    handleFileChange,
    setComment,
    openModal,
    closeModal,
    handleSubmit,
    handleSubmitAndClose,
  }
}

export default useTastingReview
