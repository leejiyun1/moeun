import Slider from '@/components/common/Slider'
import { SLIDER_CONFIGS, type SliderConfig } from '@/constants/search'
import type { SliderGroupProps } from '@/types/search'

const SliderGroup = ({ filters, onSliderChange }: SliderGroupProps) => {
  const leftSliders = SLIDER_CONFIGS.filter((s) =>
    ['sweetness', 'acidity', 'body'].includes(s.filterKey)
  )

  const rightSliders = SLIDER_CONFIGS.filter((s) =>
    ['carbonation', 'bitterness', 'aroma'].includes(s.filterKey)
  )

  const renderSliders = (sliders: SliderConfig[]) => (
    <div className="flex w-full flex-col justify-between gap-[30px] md:h-[181px]">
      {sliders.map(({ filterKey, label, variant }) => (
        <Slider
          key={filterKey}
          variant={variant}
          label={label}
          value={filters[filterKey] as number[]}
          onValueChange={(value) => onSliderChange(filterKey, value)}
        />
      ))}
    </div>
  )

  return (
    <div className="flex w-full flex-col gap-8 lg:flex-row">
      {renderSliders(leftSliders)}
      {renderSliders(rightSliders)}
    </div>
  )
}

export default SliderGroup
