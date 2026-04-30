import type {
  AdminProductStatus,
  PackageAllowedItemScope,
  PackageDiscountType,
  PackagePolicyStatus,
} from '@/types/admin'

export const ADMIN_QUERY_KEYS = {
  PRODUCTS: 'admin-products',
  BREWERIES: 'admin-breweries',
  DRINKS_FOR_PACKAGE: 'admin-drinks-for-package',
  PACKAGE_POLICIES: 'admin-package-policies',
} as const

export const ADMIN_PRODUCT_STATUS_OPTIONS: {
  value: AdminProductStatus
  label: string
}[] = [
  { value: 'ACTIVE', label: '활성' },
  { value: 'INACTIVE', label: '비활성' },
  { value: 'OUT_OF_STOCK', label: '품절' },
]

export const PACKAGE_POLICY_STATUS_OPTIONS: {
  value: PackagePolicyStatus
  label: string
}[] = [
  { value: 'ACTIVE', label: '활성' },
  { value: 'INACTIVE', label: '비활성' },
]

export const PACKAGE_ALLOWED_SCOPE_OPTIONS: {
  value: PackageAllowedItemScope
  label: string
  description: string
}[] = [
  {
    value: 'SINGLE_PRODUCTS',
    label: '단일 상품만',
    description: '고객이나 운영자가 개별 술 상품만 골라 패키지를 구성합니다.',
  },
  {
    value: 'ALL_PRODUCTS',
    label: '모든 상품',
    description: '단일 상품과 패키지 상품을 모두 구성 후보로 허용합니다.',
  },
  {
    value: 'PACKAGE_PRODUCTS',
    label: '패키지 상품만',
    description: '이미 만들어진 패키지 상품끼리 다시 묶는 정책입니다.',
  },
  {
    value: 'ALLOWED_SET',
    label: '허용 상품만',
    description: '관리자가 지정한 상품 목록 안에서만 패키지를 구성합니다.',
  },
]

export const PACKAGE_DISCOUNT_TYPE_OPTIONS: {
  value: PackageDiscountType
  label: string
}[] = [
  { value: 'NONE', label: '할인 없음' },
  { value: 'FIXED_AMOUNT', label: '정액 할인' },
]

export const ALCOHOL_TYPE_OPTIONS = [
  { value: 'MAKGEOLLI', label: '막걸리' },
  { value: 'YAKJU', label: '약주' },
  { value: 'CHEONGJU', label: '청주' },
  { value: 'SOJU', label: '소주' },
  { value: 'FRUIT_WINE', label: '과실주' },
] as const

export const PRODUCT_FEATURE_OPTIONS = [
  { key: 'is_gift_suitable', label: '선물 적합' },
  { key: 'is_award_winning', label: '수상작' },
  { key: 'is_regional_specialty', label: '지역 특산주' },
  { key: 'is_limited_edition', label: '리미티드' },
  { key: 'is_premium', label: '프리미엄' },
  { key: 'is_organic', label: '유기농' },
] as const
