import { API_PATHS, BASE_URL } from '@/constants/apiPaths'
import { axiosInstance } from '@/utils/axios'

export interface Store {
  id: number
  name: string
  address: string
  contact: string | null
}

interface StoreListResponse {
  next?: string | null
  results?: Store[]
}

const nextPath = (next: string | null | undefined) => {
  if (!next) return null

  const basePath = BASE_URL || ''
  if (basePath && next.startsWith(basePath)) {
    return next.slice(basePath.length) || '/'
  }

  try {
    const url = new URL(next)
    const pathname =
      basePath && url.pathname.startsWith(basePath)
        ? url.pathname.slice(basePath.length) || '/'
        : url.pathname

    return `${pathname}${url.search}`
  } catch {
    return next
  }
}

export const storeApi = {
  list: async (): Promise<Store[]> => {
    const stores: Store[] = []
    let url: string | null = API_PATHS.STORES.LIST

    while (url) {
      const response = await axiosInstance.get<Store[] | StoreListResponse>(url)

      if (Array.isArray(response.data)) {
        stores.push(...response.data)
        break
      }

      stores.push(...(response.data.results ?? []))
      url = nextPath(response.data.next)
    }

    return stores
  },
}
