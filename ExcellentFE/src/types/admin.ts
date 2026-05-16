import type {
  ProductDetail,
  ProductTag,
  ProductTagGroup,
} from '@/types/product'

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type AdminProductStatus = 'ACTIVE' | 'INACTIVE' | 'OUT_OF_STOCK'
export type AdminProductType = 'individual' | 'package'
export type PackagePolicyStatus = 'ACTIVE' | 'INACTIVE'
export type PackageAllowedItemScope =
  | 'ALL_PRODUCTS'
  | 'SINGLE_PRODUCTS'
  | 'PACKAGE_PRODUCTS'
  | 'ALLOWED_SET'
export type PackageDiscountType = 'NONE' | 'FIXED_AMOUNT'
export interface AdminProductListItem {
  id: string
  name: string
  product_type: AdminProductType
  price: number
  original_price: number | null
  discount: number | null
  discount_rate: number
  final_price: number
  is_on_sale: boolean
  main_image_url: string | null
  brewery_name: string | null
  alcohol_type: string | null
  tags: ProductTag[]
  is_tasting_available: boolean
  view_count: number
  like_count: number
  status: AdminProductStatus
  created_at: string
}

export interface AdminBreweryListItem {
  id: number
  name: string
  region: string | null
  image_url: string | null
  product_count: number
}

export interface AdminDrinkForPackage {
  id: number
  name: string
  brewery: {
    id: number
    name: string
    region: string | null
  }
  alcohol_type: string
  abv: number
  main_image: string | null
  price: number | null
  is_tasting_available: boolean
}

export interface PackagePolicyAllowedProduct {
  id: string
  name: string
  price: number
  status: AdminProductStatus
  is_tasting_available: boolean
  main_image: string | null
}

export interface PackagePolicy {
  id: number
  name: string
  status: PackagePolicyStatus
  min_items: number
  max_items: number
  allow_duplicate_items: boolean
  allowed_item_scope: PackageAllowedItemScope
  discount_type: PackageDiscountType
  discount_value: number
  allowed_products: PackagePolicyAllowedProduct[]
  created_at: string
  updated_at: string
}

export interface AdminProductQuery {
  search?: string
  status?: AdminProductStatus | ''
  ordering?: string
}

export interface CreatePackagePolicyPayload {
  name: string
  status: PackagePolicyStatus
  min_items: number
  max_items: number
  allow_duplicate_items: boolean
  allowed_item_scope: PackageAllowedItemScope
  discount_type: PackageDiscountType
  discount_value: number
  allowed_product_ids?: string[]
}

export interface DrinkCreatePayload {
  name: string
  brewery_id: number
  ingredients: string
  alcohol_type: string
  abv: number
  volume_ml: number
  sweetness_level: number
  acidity_level: number
  body_level: number
  carbonation_level: number
  bitterness_level: number
  aroma_level: number
}

export type CreateIndividualProductPayload = FormData

export interface PackageItemCreatePayload {
  drink_id: number
  quantity: number
  sort_order: number
}

export type CreatePackageProductPayload = FormData

export type CreateIndividualProductResponse = ProductDetail
export type CreatePackageProductResponse = ProductDetail

export interface CreateProductTagPayload {
  name: string
  group: ProductTagGroup
  description: string
  is_active: boolean
  sort_order: number
}
