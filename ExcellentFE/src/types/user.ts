export interface UserProfile {
  success: boolean
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

export interface UpdateProfilePayload {
  nickname?: string
  notification_agreed?: boolean
}
