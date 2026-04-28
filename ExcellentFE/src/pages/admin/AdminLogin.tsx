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
    <main className="flex min-h-screen items-center justify-center bg-white px-6 text-[#333333]">
      <section className="w-full max-w-[440px] rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-8">
        <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
          Admin
        </p>
        <h1 className="text-[34px] font-bold">관리자 로그인</h1>
        <p className="mt-3 text-[#666666]">
          운영자 전용 페이지입니다. 관리자 계정으로만 접근할 수 있습니다.
        </p>

        <form className="mt-8 flex flex-col gap-5" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-2 font-semibold">
            아이디
            <input
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              autoComplete="username"
              className="h-13 rounded-[12px] border border-[#d9d9d9] bg-white px-4 outline-none focus:border-[#f2544b]"
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
              className="h-13 rounded-[12px] border border-[#d9d9d9] bg-white px-4 outline-none focus:border-[#f2544b]"
              placeholder="비밀번호"
            />
          </label>

          {errorMessage && (
            <p className="rounded-[12px] bg-[#fff0ed] p-4 text-sm font-semibold text-[#f2544b]">
              {errorMessage}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="h-13 rounded-[60px] bg-[#f2544b] font-bold text-white transition hover:bg-[#e04439] disabled:cursor-not-allowed disabled:bg-[#d9d9d9]"
          >
            {isSubmitting ? '확인 중...' : '관리자 로그인'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default AdminLogin
