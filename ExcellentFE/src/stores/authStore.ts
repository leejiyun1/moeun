import { userApi } from '@/api/user'
import { ERROR_MESSAGE } from '@/constants/message'
import type { UserProfile } from '@/types/user'
import { getAxiosErrorMessage, showError } from '@/utils/feedbackUtils'
import { tokenStorage } from '@/utils/tokenStorage'
import { create } from 'zustand'

interface AuthState {
  isLoggedIn: boolean
  isAuthInitialized: boolean
  user: UserProfile | null
  login: () => Promise<void>
  logout: () => void
  initializeAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  isLoggedIn: false,
  isAuthInitialized: false,
  user: null,

  login: async () => {
    try {
      const user = await userApi.getProfile()
      set({ isLoggedIn: true, isAuthInitialized: true, user })
    } catch (error) {
      tokenStorage.removeAccessToken()
      tokenStorage.removeRefreshToken()
      tokenStorage.removeTempToken()
      set({ isLoggedIn: false, isAuthInitialized: true, user: null })
      showError(getAxiosErrorMessage(error, ERROR_MESSAGE.LOGIN_FAILED))
    }
  },

  logout: () => {
    tokenStorage.removeAccessToken()
    tokenStorage.removeRefreshToken()
    set({ isLoggedIn: false, isAuthInitialized: true, user: null })
  },

  initializeAuth: async () => {
    const token = tokenStorage.getAccessToken()

    if (!token) {
      set({ isLoggedIn: false, isAuthInitialized: true, user: null })
      return
    }

    try {
      const user = await userApi.getProfile()
      set({ isLoggedIn: true, isAuthInitialized: true, user })
    } catch (error) {
      tokenStorage.removeAccessToken()
      tokenStorage.removeRefreshToken()
      set({ isLoggedIn: false, isAuthInitialized: true, user: null })
      showError(getAxiosErrorMessage(error, ERROR_MESSAGE.LOGIN_FAILED))
    }
  },
}))
