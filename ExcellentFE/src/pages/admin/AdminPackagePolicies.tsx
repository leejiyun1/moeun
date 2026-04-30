import { adminApi } from '@/api/admin'
import {
  ADMIN_QUERY_KEYS,
  PACKAGE_ALLOWED_SCOPE_OPTIONS,
  PACKAGE_DISCOUNT_TYPE_OPTIONS,
  PACKAGE_POLICY_STATUS_OPTIONS,
} from '@/constants/admin'
import type {
  CreatePackagePolicyPayload,
  PackageAllowedItemScope,
  PackageDiscountType,
  PackagePolicyStatus,
} from '@/types/admin'
import { isAxiosError } from 'axios'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactNode,
} from 'react'
import AdminPageShell from './AdminPageShell'

interface PolicyFormState {
  name: string
  status: PackagePolicyStatus
  minItems: string
  maxItems: string
  allowDuplicateItems: boolean
  allowedItemScope: PackageAllowedItemScope
  discountType: PackageDiscountType
  discountValue: string
  allowedProductIds: string[]
}

const initialForm: PolicyFormState = {
  name: '',
  status: 'ACTIVE',
  minItems: '2',
  maxItems: '5',
  allowDuplicateItems: false,
  allowedItemScope: 'SINGLE_PRODUCTS',
  discountType: 'NONE',
  discountValue: '0',
  allowedProductIds: [],
}

const statusLabel = {
  ACTIVE: '활성',
  INACTIVE: '비활성',
} as const

const scopeLabel = Object.fromEntries(
  PACKAGE_ALLOWED_SCOPE_OPTIONS.map((option) => [option.value, option.label])
) as Record<PackageAllowedItemScope, string>

const discountLabel = Object.fromEntries(
  PACKAGE_DISCOUNT_TYPE_OPTIONS.map((option) => [option.value, option.label])
) as Record<PackageDiscountType, string>

const getErrorMessage = (error: unknown) => {
  if (!isAxiosError(error)) {
    return '패키지 정책 등록 중 오류가 발생했습니다.'
  }

  const data = error.response?.data
  if (typeof data === 'string') return data
  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0]
    if (Array.isArray(firstValue)) return String(firstValue[0])
    if (typeof firstValue === 'string') return firstValue
  }

  return '정책 값을 다시 확인해 주세요.'
}

const AdminPackagePolicies = () => {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<PolicyFormState>(initialForm)
  const [errorMessage, setErrorMessage] = useState('')

  const { data: policies, isLoading: isPoliciesLoading } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PACKAGE_POLICIES],
    queryFn: adminApi.getPackagePolicies,
  })

  const { data: products } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PRODUCTS, { allowedSet: true }],
    queryFn: () => adminApi.getProducts({ status: 'ACTIVE' }),
  })

  const createMutation = useMutation({
    mutationFn: adminApi.createPackagePolicy,
    onSuccess: async () => {
      setForm(initialForm)
      setErrorMessage('')
      await queryClient.invalidateQueries({
        queryKey: [ADMIN_QUERY_KEYS.PACKAGE_POLICIES],
      })
    },
    onError: (error) => {
      setErrorMessage(getErrorMessage(error))
    },
  })

  const handleFieldChange =
    <T extends HTMLInputElement | HTMLSelectElement>(field: keyof PolicyFormState) =>
    (event: ChangeEvent<T>) => {
      setForm((current) => ({
        ...current,
        [field]: event.target.value,
      }))
    }

  const handleDuplicateChange = (event: ChangeEvent<HTMLInputElement>) => {
    setForm((current) => ({
      ...current,
      allowDuplicateItems: event.target.checked,
    }))
  }

  const handleAllowedProductChange = (
    productId: string,
    checked: boolean
  ) => {
    setForm((current) => {
      const selected = new Set(current.allowedProductIds)
      if (checked) {
        selected.add(productId)
      } else {
        selected.delete(productId)
      }

      return {
        ...current,
        allowedProductIds: Array.from(selected),
      }
    })
  }

  const buildPayload = (): CreatePackagePolicyPayload => ({
    name: form.name.trim(),
    status: form.status,
    min_items: Number(form.minItems),
    max_items: Number(form.maxItems),
    allow_duplicate_items: form.allowDuplicateItems,
    allowed_item_scope: form.allowedItemScope,
    discount_type: form.discountType,
    discount_value:
      form.discountType === 'NONE' ? 0 : Number(form.discountValue),
    allowed_product_ids:
      form.allowedItemScope === 'ALLOWED_SET'
        ? form.allowedProductIds
        : [],
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage('')
    createMutation.mutate(buildPayload())
  }

  const selectedScope = PACKAGE_ALLOWED_SCOPE_OPTIONS.find(
    (option) => option.value === form.allowedItemScope
  )

  return (
    <AdminPageShell
      title="패키지 정책"
      description="패키지 정책은 패키지를 만들 때 적용되는 운영 규칙입니다. 구성 수량, 같은 술 중복 허용, 허용 상품 범위, 할인 방식을 한 곳에서 관리합니다."
    >
      <div className="grid gap-6 lg:grid-cols-[440px_1fr]">
        <form
          onSubmit={handleSubmit}
          className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-6"
        >
          <h2 className="text-2xl font-bold">정책 등록</h2>
          <p className="mt-3 text-sm leading-6 text-[#666666]">
            예를 들어 “3병 체험 세트”는 최소/최대 수량을 3으로 고정하고,
            같은 술 중복 허용 여부를 정책에서 결정합니다.
          </p>

          <div className="mt-6 grid gap-4">
            <Field label="정책명">
              <input
                required
                value={form.name}
                onChange={handleFieldChange<HTMLInputElement>('name')}
                className="admin-input"
                placeholder="예: 3병 체험 세트"
              />
            </Field>

            <Field label="상태">
              <select
                value={form.status}
                onChange={handleFieldChange<HTMLSelectElement>('status')}
                className="admin-input"
              >
                {PACKAGE_POLICY_STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="최소 구성 수량">
                <input
                  required
                  type="number"
                  min="1"
                  value={form.minItems}
                  onChange={handleFieldChange<HTMLInputElement>('minItems')}
                  className="admin-input"
                />
              </Field>
              <Field label="최대 구성 수량">
                <input
                  required
                  type="number"
                  min="1"
                  value={form.maxItems}
                  onChange={handleFieldChange<HTMLInputElement>('maxItems')}
                  className="admin-input"
                />
              </Field>
            </div>

            <label className="flex items-center gap-3 rounded-[14px] bg-white p-4 text-sm font-bold">
              <input
                type="checkbox"
                checked={form.allowDuplicateItems}
                onChange={handleDuplicateChange}
              />
              같은 술 중복 담기 허용
            </label>

            <Field label="허용 상품 범위">
              <select
                value={form.allowedItemScope}
                onChange={handleFieldChange<HTMLSelectElement>('allowedItemScope')}
                className="admin-input"
              >
                {PACKAGE_ALLOWED_SCOPE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </Field>

            {selectedScope && (
              <p className="rounded-[14px] bg-white p-4 text-sm leading-6 text-[#666666]">
                {selectedScope.description}
              </p>
            )}

            {form.allowedItemScope === 'ALLOWED_SET' && (
              <div className="rounded-[14px] bg-white p-4">
                <p className="mb-3 text-sm font-bold text-[#555555]">
                  허용 상품 선택
                </p>
                <div className="grid max-h-[220px] gap-2 overflow-y-auto pr-1">
                  {products?.results.map((product) => (
                    <label
                      key={product.id}
                      className="flex items-center gap-2 text-sm text-[#555555]"
                    >
                      <input
                        type="checkbox"
                        checked={form.allowedProductIds.includes(product.id)}
                        onChange={(event) =>
                          handleAllowedProductChange(
                            product.id,
                            event.target.checked
                          )
                        }
                      />
                      {product.name}
                    </label>
                  ))}
                </div>
                {!products?.results.length && (
                  <p className="text-sm text-[#f2544b]">
                    허용할 상품을 먼저 등록해야 합니다.
                  </p>
                )}
              </div>
            )}

            <Field label="할인 방식">
              <select
                value={form.discountType}
                onChange={handleFieldChange<HTMLSelectElement>('discountType')}
                className="admin-input"
              >
                {PACKAGE_DISCOUNT_TYPE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </Field>

            {form.discountType === 'FIXED_AMOUNT' && (
              <Field label="할인 금액">
                <input
                  required
                  type="number"
                  min="0"
                  value={form.discountValue}
                  onChange={handleFieldChange<HTMLInputElement>('discountValue')}
                  className="admin-input"
                />
              </Field>
            )}
          </div>

          {errorMessage && (
            <p className="mt-5 rounded-[14px] bg-[#fff4f2] p-4 font-bold text-[#f2544b]">
              {errorMessage}
            </p>
          )}

          <button
            disabled={createMutation.isPending}
            className="mt-6 w-full rounded-full bg-[#f2544b] px-6 py-4 font-bold text-white transition hover:bg-[#d9443c] disabled:cursor-not-allowed disabled:bg-[#cccccc]"
          >
            {createMutation.isPending ? '등록 중' : '정책 등록'}
          </button>
        </form>

        <section className="rounded-[20px] border border-[#d9d9d9] bg-white">
          <div className="border-b border-[#eeeeee] px-6 py-5">
            <h2 className="text-2xl font-bold">등록된 정책</h2>
            <p className="mt-2 text-sm text-[#888888]">
              운영자가 만든 고정 패키지와 고객 선택형 패키지가 이 정책을
              참조합니다.
            </p>
          </div>

          {isPoliciesLoading && (
            <p className="p-8 text-center text-[#666666]">
              정책을 불러오는 중입니다.
            </p>
          )}
          {!isPoliciesLoading && policies?.results.length === 0 && (
            <p className="p-8 text-center text-[#666666]">
              등록된 정책이 없습니다.
            </p>
          )}
          <div className="grid gap-4 p-5">
            {policies?.results.map((policy) => (
              <article
                key={policy.id}
                className="rounded-[18px] border border-[#eeeeee] bg-[#fafafa] p-5"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-xl font-bold">{policy.name}</h3>
                    <p className="mt-2 text-sm text-[#666666]">
                      {policy.min_items}~{policy.max_items}개 구성 ·{' '}
                      {policy.allow_duplicate_items
                        ? '중복 허용'
                        : '중복 불가'}
                    </p>
                  </div>
                  <span className="rounded-full bg-white px-3 py-1 text-sm font-bold text-[#f2544b]">
                    {statusLabel[policy.status]}
                  </span>
                </div>
                <div className="mt-5 grid gap-2 text-sm text-[#555555] md:grid-cols-2">
                  <Info label="허용 범위" value={scopeLabel[policy.allowed_item_scope]} />
                  <Info label="할인 방식" value={discountLabel[policy.discount_type]} />
                  <Info
                    label="할인 금액"
                    value={`${policy.discount_value.toLocaleString('ko-KR')}원`}
                  />
                  <Info
                    label="허용 상품"
                    value={
                      policy.allowed_products.length > 0
                        ? `${policy.allowed_products.length}개`
                        : '범위 기준'
                    }
                  />
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </AdminPageShell>
  )
}

interface FieldProps {
  label: string
  children: ReactNode
}

const Field = ({ label, children }: FieldProps) => (
  <label className="flex flex-col gap-2 text-sm font-bold text-[#555555]">
    {label}
    {children}
  </label>
)

interface InfoProps {
  label: string
  value: string
}

const Info = ({ label, value }: InfoProps) => (
  <div className="rounded-[12px] bg-white px-4 py-3">
    <span className="mr-2 text-[#999999]">{label}</span>
    <strong>{value}</strong>
  </div>
)

export default AdminPackagePolicies
