import { axiosInstance } from '@/utils/axios'
import { API_PATHS } from '@/constants/apiPaths'
import type { ProductDetail } from '@/types/product'
import type { CartResponse } from '@/types/cart'

export interface AddCartPayload {
  product_id: string
  quantity: number
  pickup_store_id?: number | null
  pickup_date?: string | null
}

export interface UpdateCartPayload {
  quantity?: number
  pickup_store_id?: number | null
  pickup_date?: string | null
}

export interface ProductLikeResponse {
  is_liked: boolean
  like_count: number
}

export const mainProductApi = {
  MonthProducts: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.MONTH)
    return response.data
  },
  PopularProducts: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.POPULAR)
    return response.data
  },
  RecommendedProducts: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.RECOMMENDED)
    return response.data
  },
  FeaturedPackages: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.FEATURED)
    return response.data
  },
  AwardPackages: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.AWARD)
    return response.data
  },
  MakgeolliPackages: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.MAKGEOLLI)
    return response.data
  },
  RegionalPackages: async () => {
    const response = await axiosInstance.get(API_PATHS.PRODUCTS.REGIONAL)
    return response.data
  },
}

export const cartApi = {
  ADD: async (payload: AddCartPayload) => {
    const response = await axiosInstance.post(API_PATHS.CART.ADD, payload)
    return response.data
  },
  GET: async (): Promise<CartResponse> => {
    const response = await axiosInstance.get<CartResponse>(API_PATHS.CART.GET)
    return response.data
  },
  DELETE: async (id: string) => {
    const response = await axiosInstance.delete(API_PATHS.CART.DELETE(id))
    return response.data
  },
  UPDATE: async (id: string, payload: UpdateCartPayload) => {
    const response = await axiosInstance.patch(API_PATHS.CART.UPDATE(id), payload)
    return response.data
  },
}

export const getProductDetail = async (id: string): Promise<ProductDetail> => {
  const response = await axiosInstance.get(API_PATHS.PRODUCTS.DETAIL(id))
  return response.data
}

export const toggleProductLike = async (
  id: string | number
): Promise<ProductLikeResponse> => {
  const response = await axiosInstance.post(API_PATHS.PRODUCTS.LIKE(id))
  return response.data
}
