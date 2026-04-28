import { ROUTE_PATHS } from '@/constants/routePaths'
import { Link } from 'react-router-dom'

interface AdminPlaceholderProps {
  title: string
  description: string
}

const AdminPlaceholder = ({ title, description }: AdminPlaceholderProps) => {
  return (
    <main className="min-h-screen bg-[#f7f2ea] px-10 py-12 text-[#2f2923]">
      <div className="mx-auto max-w-[960px] rounded-[32px] border border-[#e4d8cc] bg-white p-10 shadow-[0_20px_60px_rgba(94,64,43,0.08)]">
        <p className="mb-3 text-sm font-bold tracking-[0.24em] text-[#b0644f] uppercase">
          Moeun Admin
        </p>
        <h1 className="text-[36px] font-bold">{title}</h1>
        <p className="mt-4 text-lg text-[#6f6258]">{description}</p>
        <p className="mt-8 rounded-2xl bg-[#f7f2ea] p-5 text-[#6f6258]">
          이 화면은 다음 단계에서 목록, 등록, 수정 기능을 연결할 예정입니다.
        </p>
        <Link
          to={ROUTE_PATHS.ADMIN.INDEX}
          className="mt-8 inline-block font-bold text-[#b0644f]"
        >
          관리자 홈으로 돌아가기
        </Link>
      </div>
    </main>
  )
}

export default AdminPlaceholder
