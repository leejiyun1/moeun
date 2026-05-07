import { ROUTE_PATHS } from '@/constants/routePaths'
import { useDemoAdultVerification } from '@/hooks/auth/useAdultAuth'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

const AdultAuthManual = () => {
  const [searchParams] = useSearchParams()
  const redirect = searchParams.get('redirect') || ROUTE_PATHS.CART
  const [birthDate, setBirthDate] = useState('')
  const { mutate: verifyAdult, isPending } = useDemoAdultVerification(redirect)

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    verifyAdult({ birth_date: birthDate })
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-white px-6 text-[#333333]">
      <section className="w-full max-w-[520px] rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-8">
        <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
          19+
        </p>
        <h1 className="text-[34px] font-bold">성인 인증이 필요합니다</h1>
        <p className="mt-3 leading-7 text-[#666666]">
          주류 주문과 시음 신청은 성인 인증 완료 후 진행할 수 있습니다. 현재는
          데모 인증으로 생년월일만 확인합니다.
        </p>

        <form className="mt-8 flex flex-col gap-5" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-2 font-semibold">
            생년월일
            <input
              value={birthDate}
              onChange={(event) => setBirthDate(event.target.value)}
              type="date"
              required
              className="h-13 rounded-[12px] border border-[#d9d9d9] bg-white px-4 outline-none focus:border-[#f2544b]"
            />
          </label>

          <div className="rounded-[12px] bg-white p-4 text-sm leading-6 text-[#666666]">
            데모 인증은 포트폴리오와 개발 검증용입니다. 실제 운영 전에는
            PortOne/KCP 같은 본인인증 provider 결과를 백엔드에서 검증하는
            방식으로 교체해야 합니다.
          </div>

          <button
            type="submit"
            disabled={isPending || !birthDate}
            className="h-13 rounded-[60px] bg-[#f2544b] font-bold text-white transition hover:bg-[#e04439] disabled:cursor-not-allowed disabled:bg-[#d9d9d9]"
          >
            {isPending ? '확인 중...' : '성인 인증 완료하기'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default AdultAuthManual
