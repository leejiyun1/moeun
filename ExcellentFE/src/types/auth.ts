export const SOCIAL_PROVIDERS = ['kakao', 'naver', 'google'] as const
export type SocialProvider = (typeof SOCIAL_PROVIDERS)[number]

export interface SocialLoginRequest {
  code: string
  state?: string
  redirect_uri?: string
}

export interface SocialLoginUser {
  success: boolean
  access: string
  refresh: string
  user_info: {
    nickname: string
    email: string | null
    role: string
    is_adult: boolean
    adult_verified_at: string | null
    created_at: string
  }
  auth_type: string
}

export interface AdminLoginRequest {
  identifier: string
  password: string
}

export interface DemoAdultVerificationRequest {
  birth_date: string
}

export interface AdminLoginResponse {
  success: boolean
  access: string
  refresh: string
  user_info: {
    nickname: string
    email: string | null
    role: string
    is_adult: boolean
    adult_verified_at: string | null
    created_at: string
    notification_agreed: boolean
  }
}

export interface RefreshTokenResponse {
  access: string
  refresh: string
}
