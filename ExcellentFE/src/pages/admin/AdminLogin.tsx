import { authApi } from '@/api/auth'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { useAuthStore } from '@/stores/authStore'
import { tokenStorage } from '@/utils/tokenStorage'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const AdminLogin = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login } = useAuthStore()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const redirect = searchParams.get('redirect') || ROUTE_PATHS.ADMIN.INDEX

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)

    try {
      const data = await authApi.adminLogin({ identifier, password })
      tokenStorage.setAccessToken(data.access)
      tokenStorage.setRefreshToken(data.refresh)
      await login()
      navigate(redirect, { replace: true })
    } catch {
      setErrorMessage('관리자 계정 정보를 확인해주세요.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#2f2923] px-6 text-[#2f2923]">
      <section className="w-full max-w-[440px] rounded-[32px] bg-[#f7f2ea] p-8 shadow-[0_32px_80px_rgba(0,0,0,0.24)]">
        <p className="mb-3 text-sm font-bold tracking-[0.24em] text-[#b0644f] uppercase">
          Moeun Admin
        </p>
        <h1 className="text-[34px] font-bold">관리자 로그인</h1>
        <p className="mt-3 text-[#6f6258]">
          운영자 전용 페이지입니다. 관리자 계정으로만 접근할 수 있습니다.
        </p>

        <form className="mt-8 flex flex-col gap-5" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-2 font-semibold">
            아이디
            <input
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              autoComplete="username"
              className="h-13 rounded-2xl border border-[#ddcfc2] bg-white px-4 outline-none focus:border-[#b0644f]"
              placeholder="admin@test.com"
            />
          </label>
          <label className="flex flex-col gap-2 font-semibold">
            비밀번호
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete="current-password"
              className="h-13 rounded-2xl border border-[#ddcfc2] bg-white px-4 outline-none focus:border-[#b0644f]"
              placeholder="비밀번호"
            />
          </label>

          {errorMessage && (
            <p className="rounded-2xl bg-[#fff0ed] p-4 text-sm font-semibold text-[#b04432]">
              {errorMessage}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="h-13 rounded-2xl bg-[#b0644f] font-bold text-white transition hover:bg-[#964e3d] disabled:cursor-not-allowed disabled:bg-[#c8aaa0]"
          >
            {isSubmitting ? '확인 중...' : '관리자 로그인'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default AdminLogin
