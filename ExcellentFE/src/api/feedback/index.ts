import type { FeedbackRequest, FeedbackResponse } from '@/api/feedback/types'
import { API_PATHS } from '@/constants/apiPaths'
import { axiosInstance } from '@/utils/axios'

const createFormDataFromFeedback = (data: FeedbackRequest): FormData => {
  const formData = new FormData()

  const fields = {
    order_item: String(data.order_item_id),
    rating: String(Math.round(data.overall_rating)),
    comment: data.comment ?? '',
  }

  Object.entries(fields).forEach(([key, value]) => {
    formData.set(key, value)
  })

  if (data.files?.length) {
    Array.from(data.files).forEach((file) => {
      formData.append('image', file)
    })
  }

  return formData
}

export const feedbackApi = {
  submit: async (data: FeedbackRequest) => {
    const formData = createFormDataFromFeedback(data)

    const response = await axiosInstance.post(
      API_PATHS.FEEDBACK.SUBMIT,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  },

  fetchFeedbackByType: async (
    type: 'popular' | 'recent' | 'personalized'
  ): Promise<FeedbackResponse> => {
    let url = ''
    switch (type) {
      case 'popular':
        url = API_PATHS.FEEDBACK.POPULAR
        break
      case 'recent':
        url = API_PATHS.FEEDBACK.RECENT
        break
      case 'personalized':
        url = API_PATHS.FEEDBACK.PERSONALIZED
        break
    }

    const res = await axiosInstance.get<FeedbackResponse>(url)
    return res.data
  },
}
