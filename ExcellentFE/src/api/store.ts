import { API_PATHS } from '@/constants/apiPaths'
import { axiosInstance } from '@/utils/axios'

export interface Store {
  id: number
  name: string
  address: string
  contact: string | null
}

interface StoreListResponse {
  results?: Store[]
}

export const storeApi = {
  list: async (): Promise<Store[]> => {
    const response = await axiosInstance.get<Store[] | StoreListResponse>(
      API_PATHS.STORES.LIST
    )
    return Array.isArray(response.data)
      ? response.data
      : (response.data.results ?? [])
  },
}
