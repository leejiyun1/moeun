import { axiosInstance } from '@/utils/axios'
import type { Product } from '@/types/search'
import { API_PATHS } from '@/constants/apiPaths'

export interface ProductSearchResponse {
  count: number
  next: string | null
  previous: string | null
  results: Product[]
}

export type QueryParamValue =
  | string
  | number
  | Array<string | number>
  | undefined
  | null

export type SearchQueryParams = Record<string, QueryParamValue>

export async function fetchProducts(
  params?: SearchQueryParams
): Promise<ProductSearchResponse> {
  const filteredParams: Record<string, string | number | (string | number)[]> =
    {}
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        filteredParams[key] = value
      }
    })
  }

  const res = await axiosInstance.get(API_PATHS.SEARCHPRODUCTS.SEARCH, {
    params: filteredParams,
    paramsSerializer: (params) => {
      const entries: [string, string][] = []
      Object.entries(params).forEach(([key, val]) => {
        if (Array.isArray(val)) {
          val.forEach((v) => entries.push([`${key}[]`, String(v)]))
        } else {
          entries.push([key, String(val)])
        }
      })
      return new URLSearchParams(entries).toString()
    },
  })

  return res.data
}
