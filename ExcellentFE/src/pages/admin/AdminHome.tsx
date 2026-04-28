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
    <main className="min-h-screen bg-[#f7f2ea] px-10 py-12 text-[#2f2923]">
      <div className="mx-auto max-w-[1120px]">
        <div className="mb-10">
          <p className="mb-3 text-sm font-bold tracking-[0.24em] text-[#b0644f] uppercase">
            Moeun Admin
          </p>
          <h1 className="text-[42px] leading-tight font-bold">
            운영자 관리 페이지
          </h1>
          <p className="mt-4 max-w-[680px] text-lg text-[#6f6258]">
            상품, 패키지, 시음 정책을 운영 기준으로 관리하기 위한 내부
            화면입니다.
          </p>
        </div>

        <section className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {adminCards.map((card) => (
            <Link
              key={card.to}
              to={card.to}
              className="rounded-[28px] border border-[#e4d8cc] bg-white p-8 shadow-[0_20px_60px_rgba(94,64,43,0.08)] transition hover:-translate-y-1 hover:border-[#c47d62]"
            >
              <h2 className="text-2xl font-bold">{card.title}</h2>
              <p className="mt-3 text-[#6f6258]">{card.description}</p>
              <span className="mt-8 inline-block font-bold text-[#b0644f]">
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
