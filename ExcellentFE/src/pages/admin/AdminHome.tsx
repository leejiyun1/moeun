import { ROUTE_PATHS } from '@/constants/routePaths'
import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import AdminOrders from './AdminOrders'
import AdminPackagePolicies from './AdminPackagePolicies'
import AdminProductTags from './AdminProductTags'
import AdminProducts from './AdminProducts'

type AdminCategoryKey = 'products' | 'packagePolicies' | 'productTags' | 'orders'

interface AdminCategory {
  key: AdminCategoryKey
  label: string
  title: string
  description: string
  action?: ReactNode
}

const adminCategories: AdminCategory[] = [
  {
    key: 'products',
    label: '상품',
    title: '상품 관리',
    description: '단일 상품과 패키지 상품을 등록하고 운영 상태를 확인합니다.',
    action: (
      <Link
        to={ROUTE_PATHS.ADMIN.PRODUCT_NEW}
        className="rounded-full bg-[#f2544b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#d9443c]"
      >
        상품 등록
      </Link>
    ),
  },
  {
    key: 'packagePolicies',
    label: '패키지 정책',
    title: '패키지 정책',
    description:
      '패키지 구성 수량, 중복 허용, 허용 상품 범위, 할인 방식을 관리합니다.',
  },
  {
    key: 'productTags',
    label: '태그',
    title: '상품 태그',
    description:
      '상품에 붙일 표시용 라벨을 관리합니다. 검색과 추천 정책에는 연결하지 않습니다.',
  },
  {
    key: 'orders',
    label: '주문',
    title: '주문 관리',
    description: '테스트 주문과 결제 상태를 한 곳에서 확인합니다.',
  },
]

const AdminHome = () => {
  const [selectedCategory, setSelectedCategory] =
    useState<AdminCategoryKey>('products')

  const currentCategory =
    adminCategories.find((category) => category.key === selectedCategory) ??
    adminCategories[0]

  const renderCategory = () => {
    switch (selectedCategory) {
      case 'products':
        return <AdminProducts embedded />
      case 'packagePolicies':
        return <AdminPackagePolicies embedded />
      case 'productTags':
        return <AdminProductTags embedded />
      case 'orders':
        return <AdminOrders embedded />
      default:
        return null
    }
  }

  return (
    <main className="min-h-screen bg-white px-5 pt-[130px] pb-24 text-[#333333] md:px-10 md:pt-[150px]">
      <div className="mx-auto w-full max-w-[1280px]">
        <div className="mb-8 border-b border-[#d9d9d9] pb-8">
          <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
            Admin
          </p>
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-[32px] leading-tight font-bold md:text-[36px]">
                관리자 페이지
              </h1>
              <p className="mt-4 max-w-[720px] text-base text-[#666666] md:text-lg">
                관리 기능을 카테고리별로 나눠 한 화면에서 전환합니다.
              </p>
            </div>
            {currentCategory.action}
          </div>
        </div>

        <nav className="mb-8 flex flex-wrap gap-3 rounded-[24px] border border-[#eeeeee] bg-[#fafafa] p-3">
          {adminCategories.map((category) => {
            const isSelected = category.key === selectedCategory

            return (
              <button
                key={category.key}
                type="button"
                onClick={() => setSelectedCategory(category.key)}
                className={`rounded-full px-5 py-3 text-sm font-bold transition ${
                  isSelected
                    ? 'bg-[#333333] text-white'
                    : 'bg-white text-[#666666] hover:text-[#f2544b]'
                }`}
              >
                {category.label}
              </button>
            )
          })}
        </nav>

        <section className="mb-6 rounded-[22px] bg-[#fff4f2] px-6 py-5">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-2xl font-bold">{currentCategory.title}</h2>
              <p className="mt-2 text-sm leading-6 text-[#8a3a32]">
                {currentCategory.description}
              </p>
            </div>
          </div>
        </section>

        {renderCategory()}
      </div>
    </main>
  )
}

export default AdminHome
