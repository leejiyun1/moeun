import { adminApi } from '@/api/admin'
import {
  ADMIN_QUERY_KEYS,
  PRODUCT_TAG_GROUP_LABELS,
} from '@/constants/admin'
import type { CreateProductTagPayload } from '@/types/admin'
import type { ProductTagGroup } from '@/types/product'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import {
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactNode,
} from 'react'
import AdminPageShell from './AdminPageShell'

interface TagFormState {
  name: string
  slug: string
  group: ProductTagGroup
  description: string
  sortOrder: string
}

const initialForm: TagFormState = {
  name: '',
  slug: '',
  group: 'DISPLAY',
  description: '',
  sortOrder: '0',
}

const groupOptions = Object.entries(PRODUCT_TAG_GROUP_LABELS).map(
  ([value, label]) => ({
    value: value as ProductTagGroup,
    label,
  })
)

const getErrorMessage = (error: unknown) => {
  if (!isAxiosError(error)) {
    return '태그 저장 중 오류가 발생했습니다.'
  }

  const data = error.response?.data
  if (typeof data === 'string') return data
  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0]
    if (Array.isArray(firstValue)) return String(firstValue[0])
    if (typeof firstValue === 'string') return firstValue
  }

  return '태그 값을 다시 확인해 주세요.'
}

const AdminProductTags = () => {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<TagFormState>(initialForm)
  const [errorMessage, setErrorMessage] = useState('')

  const { data, isLoading, isError } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PRODUCT_TAGS],
    queryFn: adminApi.getProductTags,
  })

  const invalidateTags = async () => {
    await queryClient.invalidateQueries({
      queryKey: [ADMIN_QUERY_KEYS.PRODUCT_TAGS],
    })
    await queryClient.invalidateQueries({
      queryKey: [ADMIN_QUERY_KEYS.PRODUCTS],
    })
  }

  const createMutation = useMutation({
    mutationFn: adminApi.createProductTag,
    onSuccess: async () => {
      setForm(initialForm)
      setErrorMessage('')
      await invalidateTags()
    },
    onError: (error) => setErrorMessage(getErrorMessage(error)),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) =>
      adminApi.updateProductTag(id, { is_active: isActive }),
    onSuccess: invalidateTags,
    onError: (error) => setErrorMessage(getErrorMessage(error)),
  })

  const handleFieldChange =
    <T extends HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>(
      field: keyof TagFormState
    ) =>
    (event: ChangeEvent<T>) => {
      setForm((current) => ({
        ...current,
        [field]: event.target.value,
      }))
    }

  const buildPayload = (): CreateProductTagPayload => ({
    name: form.name.trim(),
    slug: form.slug.trim(),
    group: form.group,
    description: form.description.trim(),
    is_active: true,
    sort_order: Number(form.sortOrder),
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage('')
    createMutation.mutate(buildPayload())
  }

  return (
    <AdminPageShell
      title="상품 태그"
      description="상품 태그는 노출, 추천, 특성 분류를 관리하는 운영 기준입니다. 상품 모델에 필드를 늘리지 않고 여기서 태그를 추가해 확장합니다."
    >
      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <form
          onSubmit={handleSubmit}
          className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-6"
        >
          <h2 className="text-2xl font-bold">태그 등록</h2>
          <p className="mt-3 text-sm leading-6 text-[#666666]">
            예: 선물 적합, 수상작, 프리미엄. 검색 필터와 추천 로직에서
            쓰려면 slug를 정책에 맞게 고정합니다.
          </p>

          <div className="mt-6 grid gap-4">
            <Field label="태그명">
              <input
                required
                value={form.name}
                onChange={handleFieldChange<HTMLInputElement>('name')}
                className="admin-input"
                placeholder="예: 선물 적합"
              />
            </Field>
            <Field label="slug">
              <input
                required
                value={form.slug}
                onChange={handleFieldChange<HTMLInputElement>('slug')}
                className="admin-input"
                placeholder="예: gift-suitable"
              />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="그룹">
                <select
                  value={form.group}
                  onChange={handleFieldChange<HTMLSelectElement>('group')}
                  className="admin-input"
                >
                  {groupOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="정렬 순서">
                <input
                  required
                  type="number"
                  value={form.sortOrder}
                  onChange={handleFieldChange<HTMLInputElement>('sortOrder')}
                  className="admin-input"
                />
              </Field>
            </div>
            <Field label="설명">
              <textarea
                value={form.description}
                onChange={handleFieldChange<HTMLTextAreaElement>('description')}
                className="min-h-[96px] w-full rounded-[12px] border border-[#d9d9d9] bg-white px-4 py-3 outline-none focus:border-[#f2544b]"
                placeholder="운영자가 구분할 수 있는 설명"
              />
            </Field>
          </div>

          {errorMessage && (
            <p className="mt-4 rounded-[14px] bg-[#fff4f2] p-4 font-bold text-[#f2544b]">
              {errorMessage}
            </p>
          )}

          <button
            disabled={createMutation.isPending}
            className="mt-6 w-full rounded-full bg-[#f2544b] px-5 py-3 font-bold text-white transition hover:bg-[#d9443c] disabled:cursor-not-allowed disabled:bg-[#cccccc]"
          >
            {createMutation.isPending ? '등록 중' : '태그 등록'}
          </button>
        </form>

        <section className="rounded-[20px] border border-[#d9d9d9] bg-white">
          <div className="flex items-center justify-between border-b border-[#eeeeee] px-5 py-4">
            <h2 className="text-xl font-bold">태그 목록</h2>
            <span className="text-sm text-[#888888]">
              총 {data?.count ?? 0}개
            </span>
          </div>

          {isLoading && (
            <p className="p-8 text-center text-[#666666]">
              태그를 불러오는 중입니다.
            </p>
          )}
          {isError && (
            <p className="p-8 text-center text-[#f2544b]">
              태그 목록을 불러오지 못했습니다.
            </p>
          )}
          {!isLoading && !isError && data?.results.length === 0 && (
            <p className="p-8 text-center text-[#666666]">
              등록된 태그가 없습니다.
            </p>
          )}
          {!isLoading && !isError && Boolean(data?.results.length) && (
            <div className="divide-y divide-[#eeeeee]">
              {data?.results.map((tag) => (
                <div
                  key={tag.id}
                  className="grid gap-4 px-5 py-4 md:grid-cols-[1fr_auto]"
                >
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <strong>{tag.name}</strong>
                      <span className="rounded-full bg-[#f8f8f8] px-2.5 py-1 text-xs font-bold text-[#666666]">
                        {PRODUCT_TAG_GROUP_LABELS[tag.group]}
                      </span>
                      <span className="text-sm text-[#999999]">
                        {tag.slug}
                      </span>
                    </div>
                    {tag.description && (
                      <p className="mt-2 text-sm leading-6 text-[#666666]">
                        {tag.description}
                      </p>
                    )}
                    <p className="mt-2 text-xs font-bold text-[#999999]">
                      정렬 {tag.sort_order}
                    </p>
                  </div>
                  <button
                    type="button"
                    disabled={toggleMutation.isPending}
                    onClick={() =>
                      toggleMutation.mutate({
                        id: tag.id,
                        isActive: !tag.is_active,
                      })
                    }
                    className={`h-10 rounded-full px-4 text-sm font-bold transition disabled:cursor-not-allowed disabled:bg-[#cccccc] ${
                      tag.is_active
                        ? 'bg-[#333333] text-white hover:bg-[#111111]'
                        : 'bg-[#eeeeee] text-[#666666] hover:bg-[#dddddd]'
                    }`}
                  >
                    {tag.is_active ? '활성' : '비활성'}
                  </button>
                </div>
              ))}
            </div>
          )}
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

export default AdminProductTags
