export const TASTE_FIT_SLIDERS = [
  { key: 'sweetness' as const, label: '단맛', variant: 'sweetness' as const },
  { key: 'acidity' as const, label: '산미', variant: 'acidity' as const },
  { key: 'body' as const, label: '바디감', variant: 'body' as const },
  {
    key: 'carbonation' as const,
    label: '탄산감',
    variant: 'carbonation' as const,
  },
  { key: 'bitterness' as const, label: '쓴맛', variant: 'bitter' as const },
  { key: 'aroma' as const, label: '향', variant: 'aroma' as const },
] as const

export const TASTE_FIT_SCORE_LABELS = {
  min: '안 맞음',
  max: '잘 맞음',
  unset: '선택 안 함',
} as const
