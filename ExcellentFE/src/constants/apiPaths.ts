import type { SocialProvider } from '@/types/auth'

export const BASE_URL = import.meta.env.VITE_API_URL

export const API_PATHS = {
  AUTH: {
    LOGIN: (provider: SocialProvider) => `/auth/login/${provider}`,
    ADMIN_LOGIN: '/auth/admin/login/',
    STATE: '/auth/state',
    TOKEN_REFRESH: '/auth/token/refresh',
    ADULT_AUTH_DEMO: '/auth/adult-verification/demo/',
  },
  USER: {
    PROFILE: '/user/profile/',
    DELETE: '/user/delete/',
    TASTE_TEST_PROFILE: '/user/taste_test/profile/',
    TASTE_PROFILE: '/user/taste-profile/',
    FEEDBACKS: '/user/feedbacks/',
  },
  TASTE_TEST: {
    QUESTIONS: '/taste_test/questions/',
    RESULT: '/taste_test/submit/',
    RETAKE: '/taste_test/retake/',
  },
  FEEDBACK: {
    SUBMIT: '/feedbacks/',
    RECENT: '/feedbacks/recent/',
    POPULAR: '/feedbacks/popular/',
    PERSONALIZED: '/feedbacks/personalized/',
  },
  PRODUCTS: {
    DETAIL: (id: string | number) => `/products/${id}/`,
    MONTH: '/products/monthly/',
    POPULAR: '/products/popular/',
    FEATURED: '/products/featured/',
    RECOMMENDED: '/products/recommended/',
    AWARD: '/products/award-winning/',
    MAKGEOLLI: '/products/makgeolli/',
    REGIONAL: '/products/regional/',
  },
  ADMIN: {
    PRODUCTS: '/products/manage/',
    PRODUCT_INDIVIDUAL_CREATE: '/products/individual/create/',
    PRODUCT_PACKAGE_CREATE: '/products/package/create/',
    DRINKS_FOR_PACKAGE: '/drinks/for-package/',
    PACKAGE_POLICIES: '/package-policies/manage/',
    BREWERIES: '/breweries/',
  },
  SEARCHPRODUCTS: {
    SEARCH: '/products/search/',
  },
  ORDER: {
    LIST: '/orders/order-items/',
    CREATE_FROM_CART: '/orders/create_from_cart/',
  },
  STORES: {
    LIST: '/stores/',
  },
  CART: {
    ADD: '/cart/',
    GET: '/cart/',
    DELETE: (id: string) => `/cart/${id}/`,
    UPDATE: (id: string) => `/cart/${id}/`,
  },
} as const
