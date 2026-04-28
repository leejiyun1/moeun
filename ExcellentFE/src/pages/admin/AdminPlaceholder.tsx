import { ROUTE_PATHS } from '@/constants/routePaths'
import { Link } from 'react-router-dom'

interface AdminPlaceholderProps {
  title: string
  description: string
}

const AdminPlaceholder = ({ title, description }: AdminPlaceholderProps) => {
  return (
    <main className="min-h-screen bg-white px-10 pt-[150px] pb-24 text-[#333333]">
      <div className="mx-auto w-[1280px]">
        <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
          Admin
        </p>
        <div className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-10">
          <h1 className="text-[36px] font-bold">{title}</h1>
          <p className="mt-4 text-lg text-[#666666]">{description}</p>
          <p className="mt-8 rounded-[16px] bg-white p-5 text-[#666666]">
            이 화면은 다음 단계에서 목록, 등록, 수정 기능을 연결할
            예정입니다.
          </p>
          <Link
            to={ROUTE_PATHS.ADMIN.INDEX}
            className="mt-8 inline-block font-bold text-[#f2544b]"
          >
            관리자 홈으로 돌아가기
          </Link>
        </div>
      </div>
    </main>
  )
}

export default AdminPlaceholder
