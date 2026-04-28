import { ROUTE_PATHS } from '@/constants/routePaths'
import { Link } from 'react-router-dom'

const adminCards = [
  {
    title: '상품 관리',
    description: '일반 상품과 패키지 상품을 등록하고 상태를 관리합니다.',
    to: ROUTE_PATHS.ADMIN.PRODUCTS,
  },
  {
    title: '패키지 정책',
    description: '시음 가능 여부와 패키지 구성 규칙을 관리합니다.',
    to: ROUTE_PATHS.ADMIN.PACKAGE_POLICIES,
  },
]

const AdminHome = () => {
  return (
    <main className="min-h-screen bg-white px-10 pt-[150px] pb-24 text-[#333333]">
      <div className="mx-auto w-[1280px]">
        <div className="mb-12 border-b border-[#d9d9d9] pb-8">
          <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
            Admin
          </p>
          <h1 className="text-[36px] leading-tight font-bold">관리자 페이지</h1>
          <p className="mt-4 max-w-[680px] text-lg text-[#666666]">
            상품, 패키지, 시음 정책을 운영 기준으로 관리하기 위한 내부
            화면입니다.
          </p>
        </div>

        <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {adminCards.map((card) => (
            <Link
              key={card.to}
              to={card.to}
              className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-8 transition hover:-translate-y-1 hover:border-[#f2544b] hover:bg-white"
            >
              <h2 className="text-2xl font-bold">{card.title}</h2>
              <p className="mt-3 text-[#666666]">{card.description}</p>
              <span className="mt-8 inline-block font-bold text-[#f2544b]">
                관리하러 가기
              </span>
            </Link>
          ))}
        </section>
      </div>
    </main>
  )
}

export default AdminHome
