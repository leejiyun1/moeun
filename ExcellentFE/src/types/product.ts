// 양조장 정보
export interface BreweryInfo {
  id: number
  name: string
  region: string | null
  homepage_url?: string | null
}

// 맛 프로파일 세부 점수
export interface TasteProfile {
  sweetness: number
  acidity: number
  body: number
  carbonation: number
  bitterness: number
  aroma: number
}

// 술 정보
export interface DrinkInfo {
  id: number
  name: string
  brewery: BreweryInfo
  ingredients: string
  alcohol_type: string
  alcohol_type_display: string
  abv: number
  volume_ml: number
  food_pairing: string
  taste_profile: TasteProfile
  created_at: string
  updated_at: string
}

// 패키지 상세 정보
export interface PackageDetail {
  id: number
  name: string
  drinks: {
    id: number
    name: string
    abv: number
    volume_ml: number
    food_pairing?: string
  }[]
}

// 이미지 정보
export interface ProductImage {
  image_url: string
  is_main: boolean
  created_at: string
}

export type ProductTagGroup = 'DISPLAY' | 'FEATURE'

export interface ProductTag {
  id: number
  name: string
  group: ProductTagGroup
  description: string
  is_active: boolean
  sort_order: number
  created_at?: string
  updated_at?: string
}

// 최종 상품 타입
export interface ProductDetail {
  id: string
  name: string
  product_type: 'individual' | 'package'
  drink: DrinkInfo | null
  package: PackageDetail | null
  price: number
  original_price: number | null
  discount: number | null
  discount_rate: number
  final_price: number
  is_on_sale: boolean
  description: string
  description_image_url: string
  tags: ProductTag[]
  is_tasting_available: boolean
  view_count: number
  order_count: number
  like_count: number
  is_liked: boolean
  review_count: number
  status: 'ACTIVE' | 'INACTIVE'
  images: ProductImage[]
  created_at: string
  updated_at: string
  main_image_url?: string
  brewery_name?: string
}

export type ProductCardShape = Pick<
  ProductDetail,
  'id' | 'product_type' | 'main_image_url' | 'name' | 'final_price'
> & {
  drink: { brewery: { name: string } } | null
}

export interface Product {
  id: string | number
  name: string
  product_type: 'individual' | 'package'
  main_image_url: string
  price: number
  final_price?: number
  short_description?: string
  brewery_name?: string
  is_featured?: boolean
  recommendation_score?: number | null
  recommendation_reason?: string | null
  description?: string
  discount_rate?: number
  is_on_sale?: boolean
  is_tasting_available?: boolean
  view_count?: number
  order_count?: number
  like_count?: number
  is_liked?: boolean
  review_count?: number
  tags?: ProductTag[]
  status?: 'ACTIVE' | 'INACTIVE'
  created_at?: string
  updated_at?: string
}
