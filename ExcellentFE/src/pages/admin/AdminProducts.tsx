import { adminApi } from '@/api/admin'
import {
  ADMIN_PRODUCT_STATUS_OPTIONS,
  ADMIN_QUERY_KEYS,
} from '@/constants/admin'
import { ROUTE_PATHS } from '@/constants/routePaths'
import type { AdminProductStatus } from '@/types/admin'
import { useQuery } from '@tanstack/react-query'
import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import AdminPageShell from './AdminPageShell'

const priceFormatter = new Intl.NumberFormat('ko-KR')

const productTypeLabel = {
  individual: '단일 상품',
  package: '패키지 상품',
} as const

const statusLabel = {
  ACTIVE: '활성',
  INACTIVE: '비활성',
  OUT_OF_STOCK: '품절',
} as const

const AdminProducts = () => {
  const [searchDraft, setSearchDraft] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<AdminProductStatus | ''>('')

  const { data, isLoading, isError } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PRODUCTS, { search, status }],
    queryFn: () =>
      adminApi.getProducts({
        search,
        status,
        ordering: '-created_at',
      }),
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSearch(searchDraft.trim())
  }

  const handleStatusChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setStatus(event.target.value as AdminProductStatus | '')
  }

  return (
    <AdminPageShell
      title="상품 관리"
      description="등록된 단일 상품과 패키지 상품을 확인합니다. 상태 변경과 수정은 다음 단계에서 같은 화면에 붙입니다."
      action={
        <Link
          to={ROUTE_PATHS.ADMIN.PRODUCT_NEW}
          className="rounded-full bg-[#f2544b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#d9443c]"
        >
          상품 등록
        </Link>
      }
    >
      <section className="mb-6 rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-5 md:p-6">
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 md:flex-row md:items-end"
        >
          <label className="flex flex-1 flex-col gap-2 text-sm font-bold text-[#555555]">
            검색어
            <input
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              placeholder="상품명 또는 설명 검색"
              className="h-12 rounded-[12px] border border-[#d9d9d9] bg-white px-4 font-normal outline-none focus:border-[#f2544b]"
            />
          </label>
          <label className="flex flex-col gap-2 text-sm font-bold text-[#555555] md:w-[220px]">
            상태
            <select
              value={status}
              onChange={handleStatusChange}
              className="h-12 rounded-[12px] border border-[#d9d9d9] bg-white px-4 font-normal outline-none focus:border-[#f2544b]"
            >
              <option value="">전체</option>
              {ADMIN_PRODUCT_STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <button className="h-12 rounded-[12px] bg-[#333333] px-6 font-bold text-white transition hover:bg-[#111111]">
            조회
          </button>
        </form>
      </section>

      <section className="rounded-[20px] border border-[#d9d9d9] bg-white">
        <div className="flex items-center justify-between border-b border-[#eeeeee] px-5 py-4">
          <h2 className="text-xl font-bold">상품 목록</h2>
          <span className="text-sm text-[#888888]">
            총 {data?.count ?? 0}개
          </span>
        </div>

        {isLoading && (
          <p className="p-8 text-center text-[#666666]">상품을 불러오는 중입니다.</p>
        )}
        {isError && (
          <p className="p-8 text-center text-[#f2544b]">
            상품 목록을 불러오지 못했습니다.
          </p>
        )}
        {!isLoading && !isError && data?.results.length === 0 && (
          <p className="p-8 text-center text-[#666666]">
            등록된 상품이 없습니다.
          </p>
        )}
        {!isLoading && !isError && Boolean(data?.results.length) && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse text-left">
              <thead className="bg-[#fafafa] text-sm text-[#666666]">
                <tr>
                  <th className="px-5 py-4">상품</th>
                  <th className="px-5 py-4">구분</th>
                  <th className="px-5 py-4">가격</th>
                  <th className="px-5 py-4">할인</th>
                  <th className="px-5 py-4">시음</th>
                  <th className="px-5 py-4">상태</th>
                  <th className="px-5 py-4">조회/좋아요</th>
                </tr>
              </thead>
              <tbody>
                {data?.results.map((product) => (
                  <tr
                    key={product.id}
                    className="border-t border-[#eeeeee] text-sm"
                  >
                    <td className="px-5 py-4">
                      <div className="font-bold">{product.name}</div>
                      <div className="mt-1 text-[#888888]">
                        {product.brewery_name ?? '양조장 없음'}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      {productTypeLabel[product.product_type]}
                    </td>
                    <td className="px-5 py-4 font-bold">
                      {priceFormatter.format(product.final_price)}원
                    </td>
                    <td className="px-5 py-4">
                      {product.is_on_sale
                        ? `${priceFormatter.format(product.discount ?? 0)}원`
                        : '없음'}
                    </td>
                    <td className="px-5 py-4">
                      {product.is_tasting_available ? '가능' : '불가'}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-[#f8f8f8] px-3 py-1 font-bold">
                        {statusLabel[product.status]}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-[#666666]">
                      {priceFormatter.format(product.view_count)} /{' '}
                      {priceFormatter.format(product.like_count)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AdminPageShell>
  )
}

export default AdminProducts
