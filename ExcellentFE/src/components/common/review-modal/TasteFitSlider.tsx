import Button from '@/components/common/Button'
import Slider from '@/components/common/Slider'
import {
  TASTE_FIT_SCORE_LABELS,
  TASTE_FIT_SLIDERS,
} from '@/constants/feedbackReview'
import type { TastingReview } from '@/types/feedback'

type TasteFitField = keyof Omit<TastingReview, 'rating'>

interface TasteFitSliderProps {
  review: TastingReview
  updateReview: (field: keyof TastingReview, value: number) => void
  clearTasteFitScore: (field: TasteFitField) => void
}

const TasteFitSlider = ({
  review,
  updateReview,
  clearTasteFitScore,
}: TasteFitSliderProps) => {
  return (
    <div className="mt-12">
      <div className="border-b-2 pb-3">
        <p className="text-xl font-bold text-[#333333]">
          맛별 입맛 적합도
        </p>
        <p className="mt-2 text-sm text-[#666666]">
          술의 맛을 객관적으로 평가하는 게 아니라, 내 입맛에 얼마나
          잘 맞았는지 선택해주세요. 잘 모르겠는 항목은 건너뛰어도 됩니다.
        </p>
      </div>
      <div className="mt-7 flex flex-col items-center gap-7">
        {TASTE_FIT_SLIDERS.map((slider) => {
          const value = review[slider.key]
          const isUnset = value === undefined
          return (
            <div
              key={slider.key}
              className="flex w-full flex-col items-center gap-2"
            >
              <Slider
                label={slider.label}
                variant={slider.variant}
                value={[value ?? 0]}
                onValueChange={(vals) =>
                  updateReview(slider.key, vals[0] ?? 0)
                }
                formatValue={(nextValue) =>
                  nextValue === 0
                    ? TASTE_FIT_SCORE_LABELS.min
                    : nextValue.toFixed(1)
                }
              />
              <div className="flex w-[480px] items-center justify-end gap-3 text-sm">
                <span className="text-[#666666]">
                  {isUnset
                    ? TASTE_FIT_SCORE_LABELS.unset
                    : `${value.toFixed(1)}점, ${TASTE_FIT_SCORE_LABELS.max}에 가까움`}
                </span>
                <Button
                  variant="VARIANT10"
                  onClick={() => clearTasteFitScore(slider.key)}
                  className="h-8 border-[#999999] px-3 text-xs text-[#555555]"
                >
                  건너뛰기
                </Button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TasteFitSlider
