import { API_PATHS } from '@/constants/apiPaths'
import type {
  AdminBreweryListItem,
  AdminDrinkForPackage,
  AdminProductListItem,
  AdminProductQuery,
  CreateIndividualProductPayload,
  CreateIndividualProductResponse,
  CreatePackageProductPayload,
  CreatePackageProductResponse,
  CreatePackagePolicyPayload,
  CreateProductTagPayload,
  PackagePolicy,
  PaginatedResponse,
} from '@/types/admin'
import type { ProductTag } from '@/types/product'
import { axiosInstance } from '@/utils/axios'

const compactParams = (params?: AdminProductQuery) => {
  if (!params) return undefined

  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== '')
  )
}

export const adminApi = {
  getProducts: async (
    params?: AdminProductQuery
  ): Promise<PaginatedResponse<AdminProductListItem>> => {
    const response = await axiosInstance.get(API_PATHS.ADMIN.PRODUCTS, {
      params: compactParams(params),
    })
    return response.data
  },

  createIndividualProduct: async (
    payload: CreateIndividualProductPayload
  ): Promise<CreateIndividualProductResponse> => {
    const response = await axiosInstance.post(
      API_PATHS.ADMIN.PRODUCT_INDIVIDUAL_CREATE,
      payload
    )
    return response.data
  },

  createPackageProduct: async (
    payload: CreatePackageProductPayload
  ): Promise<CreatePackageProductResponse> => {
    const response = await axiosInstance.post(
      API_PATHS.ADMIN.PRODUCT_PACKAGE_CREATE,
      payload
    )
    return response.data
  },

  getBreweries: async (): Promise<PaginatedResponse<AdminBreweryListItem>> => {
    const response = await axiosInstance.get(API_PATHS.ADMIN.BREWERIES)
    return response.data
  },

  getDrinksForPackage: async (): Promise<PaginatedResponse<AdminDrinkForPackage>> => {
    const response = await axiosInstance.get(API_PATHS.ADMIN.DRINKS_FOR_PACKAGE)
    return response.data
  },

  getPackagePolicies: async (): Promise<PaginatedResponse<PackagePolicy>> => {
    const response = await axiosInstance.get(API_PATHS.ADMIN.PACKAGE_POLICIES)
    return response.data
  },

  createPackagePolicy: async (
    payload: CreatePackagePolicyPayload
  ): Promise<PackagePolicy> => {
    const response = await axiosInstance.post(
      API_PATHS.ADMIN.PACKAGE_POLICIES,
      payload
    )
    return response.data
  },

  getProductTags: async (): Promise<PaginatedResponse<ProductTag>> => {
    const response = await axiosInstance.get(API_PATHS.ADMIN.PRODUCT_TAGS)
    return response.data
  },

  createProductTag: async (
    payload: CreateProductTagPayload
  ): Promise<ProductTag> => {
    const response = await axiosInstance.post(
      API_PATHS.ADMIN.PRODUCT_TAGS,
      payload
    )
    return response.data
  },

  updateProductTag: async (
    tagId: number,
    payload: Partial<CreateProductTagPayload>
  ): Promise<ProductTag> => {
    const response = await axiosInstance.patch(
      API_PATHS.ADMIN.PRODUCT_TAG_DETAIL(tagId),
      payload
    )
    return response.data
  },
}
