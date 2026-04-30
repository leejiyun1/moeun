import type { ProductDetail } from '@/types/product'

export const DRINK_INFO_ROWS = (data: ProductDetail) => [
  {
    label: '맛 정보',
    value: data.drink
      ? `단맛 ${data.drink.taste_profile.sweetness}, 산미 ${data.drink.taste_profile.acidity}, 쓴맛 ${data.drink.taste_profile.bitterness}, 바디감 ${data.drink.taste_profile.body}, 향 ${data.drink.taste_profile.aroma}`
      : '-',
  },
  { label: '주종', value: data.drink?.alcohol_type_display ?? '-' },
  { label: '도수', value: data.drink ? `${data.drink.abv}%` : '-' },
  {
    label: '특징',
    value: data.drink?.ingredients ?? '-',
  },
]

export const PACKAGE_INFO_ROWS = (data: ProductDetail) => [
  {
    label: '구성품',
    value:
      data.package?.drinks
        ?.map((drink) => `${drink.name} (${drink.abv}%)`)
        ?.join(',\n') ?? '-',
  },
  {
    label: '용량',
    value:
      data.package?.drinks
        ?.map((drink) => `${drink.name} (${drink.volume_ml}ml)`)
        ?.join(',\n') ?? '-',
  },
  {
    label: '특징',
    value: data.description ?? '-',
  },
]
