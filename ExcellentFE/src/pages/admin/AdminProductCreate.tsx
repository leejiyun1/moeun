import { adminApi } from '@/api/admin'
import {
  ADMIN_QUERY_KEYS,
  ALCOHOL_TYPE_OPTIONS,
  PRODUCT_TAG_GROUP_LABELS,
} from '@/constants/admin'
import { ROUTE_PATHS } from '@/constants/routePaths'
import type {
  CreateIndividualProductPayload,
  CreatePackageProductPayload,
} from '@/types/admin'
import type { ProductTag } from '@/types/product'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import {
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import AdminPageShell from './AdminPageShell'

type ProductKind = 'individual' | 'package'

interface CommonProductFormState {
  price: string
  originalPrice: string
  discount: string
  description: string
  descriptionImageFile: File | null
  mainImageFile: File | null
  isTastingAvailable: boolean
}

interface IndividualFormState {
  name: string
  breweryId: string
  ingredients: string
  alcoholType: string
  abv: string
  volumeMl: string
  sweetnessLevel: string
  acidityLevel: string
  bodyLevel: string
  carbonationLevel: string
  bitternessLevel: string
  aromaLevel: string
}

interface PackageFormState {
  name: string
  policyId: string
  items: PackageItemFormState[]
}

interface PackageItemFormState {
  drinkId: string
  quantity: string
}

type CommonTextField = Exclude<
  keyof CommonProductFormState,
  'isTastingAvailable' | 'descriptionImageFile' | 'mainImageFile'
>
type CommonFileField = 'descriptionImageFile' | 'mainImageFile'

const initialCommonForm: CommonProductFormState = {
  price: '',
  originalPrice: '',
  discount: '',
  description: '',
  descriptionImageFile: null,
  mainImageFile: null,
  isTastingAvailable: false,
}

const initialIndividualForm: IndividualFormState = {
  name: '',
  breweryId: '',
  ingredients: '',
  alcoholType: 'MAKGEOLLI',
  abv: '',
  volumeMl: '',
  sweetnessLevel: '2.5',
  acidityLevel: '2.5',
  bodyLevel: '2.5',
  carbonationLevel: '0',
  bitternessLevel: '2.5',
  aromaLevel: '2.5',
}

const initialPackageForm: PackageFormState = {
  name: '',
  policyId: '',
  items: [
    { drinkId: '', quantity: '1' },
    { drinkId: '', quantity: '1' },
  ],
}

const numericValue = (value: string) => Number(value)
const optionalNumericValue = (value: string) =>
  value.trim() === '' ? null : Number(value)

const getErrorMessage = (error: unknown) => {
  if (!isAxiosError(error)) {
    return '상품 등록 중 오류가 발생했습니다.'
  }

  const data = error.response?.data
  if (typeof data === 'string') return data
  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0]
    if (Array.isArray(firstValue)) return String(firstValue[0])
    if (typeof firstValue === 'string') return firstValue
  }

  return '입력값을 다시 확인해 주세요.'
}

const AdminProductCreate = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [productKind, setProductKind] = useState<ProductKind>('individual')
  const [commonForm, setCommonForm] =
    useState<CommonProductFormState>(initialCommonForm)
  const [individualForm, setIndividualForm] = useState<IndividualFormState>(
    initialIndividualForm
  )
  const [packageForm, setPackageForm] =
    useState<PackageFormState>(initialPackageForm)
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([])
  const [errorMessage, setErrorMessage] = useState('')

  const { data: breweries, isLoading: isBreweriesLoading } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.BREWERIES],
    queryFn: adminApi.getBreweries,
  })

  const { data: drinks, isLoading: isDrinksLoading } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.DRINKS_FOR_PACKAGE],
    queryFn: adminApi.getDrinksForPackage,
  })

  const { data: policies } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PACKAGE_POLICIES],
    queryFn: adminApi.getPackagePolicies,
  })

  const { data: tags } = useQuery({
    queryKey: [ADMIN_QUERY_KEYS.PRODUCT_TAGS],
    queryFn: adminApi.getProductTags,
  })

  const onCreateSuccess = async () => {
    await queryClient.invalidateQueries({
      queryKey: [ADMIN_QUERY_KEYS.PRODUCTS],
    })
    await queryClient.invalidateQueries({
      queryKey: [ADMIN_QUERY_KEYS.DRINKS_FOR_PACKAGE],
    })
    navigate(ROUTE_PATHS.ADMIN.PRODUCTS)
  }

  const individualMutation = useMutation({
    mutationFn: adminApi.createIndividualProduct,
    onSuccess: onCreateSuccess,
    onError: (error) => setErrorMessage(getErrorMessage(error)),
  })

  const packageMutation = useMutation({
    mutationFn: adminApi.createPackageProduct,
    onSuccess: onCreateSuccess,
    onError: (error) => setErrorMessage(getErrorMessage(error)),
  })

  const isSubmitting = individualMutation.isPending || packageMutation.isPending
  const hasBreweries = Boolean(breweries?.results.length)
  const hasDrinks = Boolean(drinks?.results.length)

  const handleKindChange = (kind: ProductKind) => {
    setProductKind(kind)
    setErrorMessage('')
  }

  const handleCommonFieldChange =
    (field: CommonTextField) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setCommonForm((current) => ({
        ...current,
        [field]: event.target.value,
      }))
    }

  const handleIndividualFieldChange =
    (field: keyof IndividualFormState) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setIndividualForm((current) => ({
        ...current,
        [field]: event.target.value,
      }))
    }

  const handlePackageFieldChange =
    (field: Exclude<keyof PackageFormState, 'items'>) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setPackageForm((current) => ({
        ...current,
        [field]: event.target.value,
      }))
    }

  const handlePackageItemChange =
    (index: number, field: keyof PackageItemFormState) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setPackageForm((current) => ({
        ...current,
        items: current.items.map((item, itemIndex) =>
          itemIndex === index ? { ...item, [field]: event.target.value } : item
        ),
      }))
    }

  const addPackageItem = () => {
    setPackageForm((current) => ({
      ...current,
      items: [...current.items, { drinkId: '', quantity: '1' }],
    }))
  }

  const removePackageItem = (index: number) => {
    setPackageForm((current) => ({
      ...current,
      items: current.items.filter((_, itemIndex) => itemIndex !== index),
    }))
  }

  const handleTagChange = (tagId: number, checked: boolean) => {
    setSelectedTagIds((current) => {
      const selected = new Set(current)
      if (checked) {
        selected.add(tagId)
      } else {
        selected.delete(tagId)
      }
      return Array.from(selected)
    })
  }

  const handleTastingChange = (event: ChangeEvent<HTMLInputElement>) => {
    setCommonForm((current) => ({
      ...current,
      isTastingAvailable: event.target.checked,
    }))
  }

  const handleCommonFileChange =
    (field: CommonFileField) => (event: ChangeEvent<HTMLInputElement>) => {
      setCommonForm((current) => ({
        ...current,
        [field]: event.target.files?.[0] ?? null,
      }))
    }

  const appendCommonPayload = (formData: FormData) => {
    formData.append('price', String(numericValue(commonForm.price)))
    const originalPrice = optionalNumericValue(commonForm.originalPrice)
    const discount = optionalNumericValue(commonForm.discount)
    if (originalPrice !== null) {
      formData.append('original_price', String(originalPrice))
    }
    if (discount !== null) {
      formData.append('discount', String(discount))
    }
    formData.append('description', commonForm.description.trim())
    formData.append('tag_ids', JSON.stringify(selectedTagIds))
    formData.append(
      'is_tasting_available',
      String(commonForm.isTastingAvailable)
    )
    if (commonForm.mainImageFile) {
      formData.append('main_image_file', commonForm.mainImageFile)
    }
    if (commonForm.descriptionImageFile) {
      formData.append('description_image_file', commonForm.descriptionImageFile)
    }
  }

  const buildIndividualPayload = (): CreateIndividualProductPayload => {
    const formData = new FormData()
    appendCommonPayload(formData)
    formData.append(
      'drink_info',
      JSON.stringify({
        name: individualForm.name.trim(),
        brewery_id: numericValue(individualForm.breweryId),
        ingredients: individualForm.ingredients.trim(),
        alcohol_type: individualForm.alcoholType,
        abv: numericValue(individualForm.abv),
        volume_ml: numericValue(individualForm.volumeMl),
        sweetness_level: numericValue(individualForm.sweetnessLevel),
        acidity_level: numericValue(individualForm.acidityLevel),
        body_level: numericValue(individualForm.bodyLevel),
        carbonation_level: numericValue(individualForm.carbonationLevel),
        bitterness_level: numericValue(individualForm.bitternessLevel),
        aroma_level: numericValue(individualForm.aromaLevel),
      })
    )
    return formData
  }

  const buildPackagePayload = (): CreatePackageProductPayload => {
    const formData = new FormData()
    appendCommonPayload(formData)
    formData.append(
      'package_info',
      JSON.stringify({
        name: packageForm.name.trim(),
        type: 'CURATED',
        policy_id: optionalNumericValue(packageForm.policyId),
        items: packageForm.items
          .filter((item) => item.drinkId)
          .map((item, index) => ({
            drink_id: numericValue(item.drinkId),
            quantity: numericValue(item.quantity),
            sort_order: index,
          })),
      })
    )
    return formData
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage('')

    if (productKind === 'individual') {
      individualMutation.mutate(buildIndividualPayload())
      return
    }

    packageMutation.mutate(buildPackagePayload())
  }

  return (
    <AdminPageShell
      title="상품 등록"
      description="단일 상품은 새 술을 함께 만들고, 패키지 상품은 이미 등록된 술을 골라 고정 구성 상품으로 만듭니다."
    >
      <form onSubmit={handleSubmit} className="grid gap-6">
        <section className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-6">
          <h2 className="text-2xl font-bold">상품 유형</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <KindButton
              active={productKind === 'individual'}
              title="단일 상품"
              description="새 술 정보를 입력하고 판매 상품으로 등록합니다."
              onClick={() => handleKindChange('individual')}
            />
            <KindButton
              active={productKind === 'package'}
              title="패키지 상품"
              description="이미 등록된 술을 골라 고정 패키지로 등록합니다."
              onClick={() => handleKindChange('package')}
            />
          </div>
        </section>

        {productKind === 'individual' ? (
          <IndividualProductSection
            form={individualForm}
            breweries={breweries?.results ?? []}
            isBreweriesLoading={isBreweriesLoading}
            hasBreweries={hasBreweries}
            onChange={handleIndividualFieldChange}
          />
        ) : (
          <PackageProductSection
            form={packageForm}
            drinks={drinks?.results ?? []}
            policies={policies?.results ?? []}
            isDrinksLoading={isDrinksLoading}
            hasDrinks={hasDrinks}
            onFieldChange={handlePackageFieldChange}
            onItemChange={handlePackageItemChange}
            onAddItem={addPackageItem}
            onRemoveItem={removePackageItem}
          />
        )}

        <CommonSaleSection
          form={commonForm}
          onChange={handleCommonFieldChange}
          onFileChange={handleCommonFileChange}
        />
        <CommonDescriptionSection
          form={commonForm}
          tags={tags?.results ?? []}
          selectedTagIds={selectedTagIds}
          onFieldChange={handleCommonFieldChange}
          onTagChange={handleTagChange}
          onTastingChange={handleTastingChange}
        />

        {errorMessage && (
          <p className="rounded-[14px] bg-[#fff4f2] p-4 font-bold text-[#f2544b]">
            {errorMessage}
          </p>
        )}
        {productKind === 'individual' &&
          !hasBreweries &&
          !isBreweriesLoading && (
            <p className="rounded-[14px] bg-[#fff4f2] p-4 font-bold text-[#8a3a32]">
              등록 가능한 양조장이 없습니다. 상품 등록 전에 양조장 등록 화면이
              필요합니다.
            </p>
          )}
        {productKind === 'package' && !hasDrinks && !isDrinksLoading && (
          <p className="rounded-[14px] bg-[#fff4f2] p-4 font-bold text-[#8a3a32]">
            패키지에 담을 술이 없습니다. 단일 상품을 먼저 등록해야 합니다.
          </p>
        )}

        <div className="flex justify-end">
          <button
            disabled={
              isSubmitting ||
              (productKind === 'individual' && !hasBreweries) ||
              (productKind === 'package' && !hasDrinks)
            }
            className="rounded-full bg-[#f2544b] px-8 py-4 font-bold text-white transition hover:bg-[#d9443c] disabled:cursor-not-allowed disabled:bg-[#cccccc]"
          >
            {isSubmitting
              ? '등록 중'
              : productKind === 'individual'
                ? '단일 상품 등록'
                : '패키지 상품 등록'}
          </button>
        </div>
      </form>
    </AdminPageShell>
  )
}

interface KindButtonProps {
  active: boolean
  title: string
  description: string
  onClick: () => void
}

const KindButton = ({
  active,
  title,
  description,
  onClick,
}: KindButtonProps) => (
  <button
    type="button"
    onClick={onClick}
    className={`rounded-[18px] border p-5 text-left transition ${
      active
        ? 'border-[#f2544b] bg-white'
        : 'border-[#d9d9d9] bg-[#f8f8f8] hover:border-[#f2544b]'
    }`}
  >
    <strong className="block text-xl">{title}</strong>
    <span className="mt-2 block text-sm leading-6 text-[#666666]">
      {description}
    </span>
  </button>
)

interface IndividualProductSectionProps {
  form: IndividualFormState
  breweries: { id: number; name: string; region: string | null }[]
  isBreweriesLoading: boolean
  hasBreweries: boolean
  onChange: (
    field: keyof IndividualFormState
  ) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

const IndividualProductSection = ({
  form,
  breweries,
  isBreweriesLoading,
  hasBreweries,
  onChange,
}: IndividualProductSectionProps) => (
  <>
    <section className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-6">
      <h2 className="text-2xl font-bold">술 기본 정보</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <Field label="술 이름">
          <input
            required
            value={form.name}
            onChange={onChange('name')}
            className="admin-input"
            placeholder="예: 모은 막걸리"
          />
        </Field>
        <Field label="양조장">
          <select
            required
            value={form.breweryId}
            onChange={onChange('breweryId')}
            disabled={isBreweriesLoading || !hasBreweries}
            className="admin-input"
          >
            <option value="">
              {isBreweriesLoading
                ? '양조장을 불러오는 중'
                : '양조장을 선택하세요'}
            </option>
            {breweries.map((brewery) => (
              <option key={brewery.id} value={brewery.id}>
                {brewery.name}
                {brewery.region ? ` (${brewery.region})` : ''}
              </option>
            ))}
          </select>
        </Field>
        <Field label="주종">
          <select
            required
            value={form.alcoholType}
            onChange={onChange('alcoholType')}
            className="admin-input"
          >
            {ALCOHOL_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="원재료">
          <input
            required
            value={form.ingredients}
            onChange={onChange('ingredients')}
            className="admin-input"
            placeholder="쌀, 누룩, 정제수"
          />
        </Field>
        <Field label="도수(%)">
          <input
            required
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={form.abv}
            onChange={onChange('abv')}
            className="admin-input"
          />
        </Field>
        <Field label="용량(ml)">
          <input
            required
            type="number"
            min="1"
            value={form.volumeMl}
            onChange={onChange('volumeMl')}
            className="admin-input"
          />
        </Field>
      </div>
    </section>

    <section className="rounded-[20px] border border-[#d9d9d9] bg-white p-6">
      <h2 className="text-2xl font-bold">맛 프로필</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <TasteField
          label="단맛"
          value={form.sweetnessLevel}
          onChange={onChange('sweetnessLevel')}
        />
        <TasteField
          label="산미"
          value={form.acidityLevel}
          onChange={onChange('acidityLevel')}
        />
        <TasteField
          label="바디감"
          value={form.bodyLevel}
          onChange={onChange('bodyLevel')}
        />
        <TasteField
          label="탄산감"
          value={form.carbonationLevel}
          onChange={onChange('carbonationLevel')}
        />
        <TasteField
          label="쓴맛"
          value={form.bitternessLevel}
          onChange={onChange('bitternessLevel')}
        />
        <TasteField
          label="풍미"
          value={form.aromaLevel}
          onChange={onChange('aromaLevel')}
        />
      </div>
    </section>
  </>
)

interface PackageProductSectionProps {
  form: PackageFormState
  drinks: {
    id: number
    name: string
    brewery: { name: string; region: string | null }
    price: number | null
  }[]
  policies: { id: number; name: string; min_items: number; max_items: number }[]
  isDrinksLoading: boolean
  hasDrinks: boolean
  onFieldChange: (
    field: Exclude<keyof PackageFormState, 'items'>
  ) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
  onItemChange: (
    index: number,
    field: keyof PackageItemFormState
  ) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
  onAddItem: () => void
  onRemoveItem: (index: number) => void
}

const PackageProductSection = ({
  form,
  drinks,
  policies,
  isDrinksLoading,
  hasDrinks,
  onFieldChange,
  onItemChange,
  onAddItem,
  onRemoveItem,
}: PackageProductSectionProps) => (
  <section className="rounded-[20px] border border-[#d9d9d9] bg-[#f8f8f8] p-6">
    <h2 className="text-2xl font-bold">패키지 구성</h2>
    <p className="mt-3 text-sm leading-6 text-[#666666]">
      종류와 수량이 고정된 판매용 패키지입니다. 정책은 필수가 아니며, 구성
      수량/중복/허용 상품을 정책으로 묶어 관리하고 싶을 때만 선택합니다.
    </p>

    <div className="mt-6 grid gap-4 md:grid-cols-2">
      <Field label="패키지명">
        <input
          required
          value={form.name}
          onChange={onFieldChange('name')}
          className="admin-input"
          placeholder="예: 막걸리 3병 세트"
        />
      </Field>
      <Field label="패키지 정책">
        <select
          value={form.policyId}
          onChange={onFieldChange('policyId')}
          className="admin-input"
        >
          <option value="">정책 없음 - 고정 구성 패키지</option>
          {policies.map((policy) => (
            <option key={policy.id} value={policy.id}>
              {policy.name} ({policy.min_items}~{policy.max_items}개)
            </option>
          ))}
        </select>
      </Field>
    </div>

    <div className="mt-6 grid gap-3">
      {form.items.map((item, index) => (
        <div
          key={index}
          className="grid gap-3 rounded-[16px] bg-white p-4 md:grid-cols-[1fr_120px_auto]"
        >
          <Field label={`구성 술 ${index + 1}`}>
            <select
              required
              value={item.drinkId}
              onChange={onItemChange(index, 'drinkId')}
              disabled={isDrinksLoading || !hasDrinks}
              className="admin-input"
            >
              <option value="">
                {isDrinksLoading ? '술 목록을 불러오는 중' : '술 선택'}
              </option>
              {drinks.map((drink) => (
                <option key={drink.id} value={drink.id}>
                  {drink.name} · {drink.brewery.name}
                  {drink.price
                    ? ` · ${drink.price.toLocaleString('ko-KR')}원`
                    : ''}
                </option>
              ))}
            </select>
          </Field>
          <Field label="수량">
            <input
              required
              type="number"
              min="1"
              value={item.quantity}
              onChange={onItemChange(index, 'quantity')}
              className="admin-input"
            />
          </Field>
          <button
            type="button"
            onClick={() => onRemoveItem(index)}
            disabled={form.items.length <= 1}
            className="self-end rounded-[12px] border border-[#d9d9d9] px-4 py-3 text-sm font-bold text-[#666666] disabled:cursor-not-allowed disabled:text-[#cccccc]"
          >
            제거
          </button>
        </div>
      ))}
    </div>

    <button
      type="button"
      onClick={onAddItem}
      className="mt-4 rounded-full border border-[#f2544b] px-5 py-3 text-sm font-bold text-[#f2544b]"
    >
      구성 추가
    </button>
  </section>
)

interface CommonSaleSectionProps {
  form: CommonProductFormState
  onChange: (
    field: CommonTextField
  ) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
  onFileChange: (
    field: CommonFileField
  ) => (event: ChangeEvent<HTMLInputElement>) => void
}

const CommonSaleSection = ({
  form,
  onChange,
  onFileChange,
}: CommonSaleSectionProps) => (
  <section className="rounded-[20px] border border-[#d9d9d9] bg-white p-6">
    <h2 className="text-2xl font-bold">가격과 이미지</h2>
    <div className="mt-6 grid gap-4 md:grid-cols-3">
      <Field label="판매가">
        <input
          required
          type="number"
          min="0"
          value={form.price}
          onChange={onChange('price')}
          className="admin-input"
        />
      </Field>
      <Field label="정가">
        <input
          type="number"
          min="0"
          value={form.originalPrice}
          onChange={onChange('originalPrice')}
          className="admin-input"
          placeholder="할인 시 입력"
        />
      </Field>
      <Field label="할인 금액">
        <input
          type="number"
          min="0"
          value={form.discount}
          onChange={onChange('discount')}
          className="admin-input"
          placeholder="없으면 비움"
        />
      </Field>
    </div>
    <div className="mt-4 grid gap-4 md:grid-cols-2">
      <FileField
        label="대표 이미지"
        file={form.mainImageFile}
        onChange={onFileChange('mainImageFile')}
      />
      <FileField
        label="상세 설명 이미지"
        file={form.descriptionImageFile}
        onChange={onFileChange('descriptionImageFile')}
      />
    </div>
  </section>
)

interface FileFieldProps {
  label: string
  file: File | null
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
}

const FileField = ({ label, file, onChange }: FileFieldProps) => (
  <Field label={label}>
    <div className="rounded-[16px] border border-dashed border-[#d9d9d9] bg-[#fafafa] p-4">
      <input
        required
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif"
        onChange={onChange}
        className="block w-full text-sm text-[#666666] file:mr-4 file:rounded-full file:border-0 file:bg-[#333333] file:px-4 file:py-2 file:text-sm file:font-bold file:text-white"
      />
      <p className="mt-3 text-xs leading-5 text-[#888888]">
        jpg, png, webp, gif 파일을 첨부하세요. 저장 후 URL은 서버가 자동으로
        생성합니다.
      </p>
      {file && (
        <p className="mt-2 rounded-[10px] bg-white px-3 py-2 text-sm font-bold text-[#333333]">
          선택됨: {file.name}
        </p>
      )}
    </div>
  </Field>
)

interface CommonDescriptionSectionProps {
  form: CommonProductFormState
  tags: ProductTag[]
  selectedTagIds: number[]
  onFieldChange: (
    field: CommonTextField
  ) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
  onTagChange: (tagId: number, checked: boolean) => void
  onTastingChange: (event: ChangeEvent<HTMLInputElement>) => void
}

const CommonDescriptionSection = ({
  form,
  tags,
  selectedTagIds,
  onFieldChange,
  onTagChange,
  onTastingChange,
}: CommonDescriptionSectionProps) => (
  <section className="rounded-[20px] border border-[#d9d9d9] bg-white p-6">
    <h2 className="text-2xl font-bold">설명과 특성</h2>
    <Field label="상품 설명">
      <textarea
        required
        value={form.description}
        onChange={onFieldChange('description')}
        className="min-h-[160px] w-full rounded-[12px] border border-[#d9d9d9] bg-white px-4 py-3 outline-none focus:border-[#f2544b]"
        placeholder="상품 페이지에 노출될 설명을 입력하세요."
      />
    </Field>

    <div className="mt-5">
      <div className="mb-3 flex items-center justify-between">
        <strong className="text-sm text-[#555555]">운영 태그</strong>
        <span className="text-xs font-bold text-[#999999]">
          태그 관리 화면에서 추가/비활성화할 수 있습니다.
        </span>
      </div>
      {tags.length === 0 ? (
        <p className="rounded-[14px] bg-[#f8f8f8] p-4 text-sm text-[#666666]">
          아직 등록된 태그가 없습니다. 태그가 없으면 상품은 태그 없이
          등록됩니다.
        </p>
      ) : (
        <div className="flex flex-wrap gap-3">
          {tags
            .filter((tag) => tag.is_active)
            .map((tag) => (
              <label
                key={tag.id}
                className="flex cursor-pointer items-center gap-2 rounded-full border border-[#d9d9d9] bg-[#f8f8f8] px-4 py-2 text-sm font-bold"
              >
                <input
                  type="checkbox"
                  checked={selectedTagIds.includes(tag.id)}
                  onChange={(event) =>
                    onTagChange(tag.id, event.target.checked)
                  }
                />
                <span>{tag.name}</span>
                <span className="text-xs text-[#999999]">
                  {PRODUCT_TAG_GROUP_LABELS[tag.group]}
                </span>
              </label>
            ))}
        </div>
      )}
    </div>

    <label className="mt-5 flex items-start gap-3 rounded-[14px] bg-[#fff4f2] p-4 text-sm leading-6 font-bold text-[#8a3a32]">
      <input
        type="checkbox"
        checked={form.isTastingAvailable}
        onChange={onTastingChange}
        className="mt-1"
      />
      이 상품을 시음 신청 가능 상품으로 운영합니다.
    </label>
  </section>
)

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

interface TasteFieldProps {
  label: string
  value: string
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
}

const TasteField = ({ label, value, onChange }: TasteFieldProps) => (
  <Field label={`${label} (0~5)`}>
    <input
      required
      type="number"
      min="0"
      max="5"
      step="0.1"
      value={value}
      onChange={onChange}
      className="admin-input"
    />
  </Field>
)

export default AdminProductCreate
