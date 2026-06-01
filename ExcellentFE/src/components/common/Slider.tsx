import * as SliderPrimitive from '@radix-ui/react-slider'
import clsx from 'clsx'
import type { SliderProps } from '@/types/slider.types'
import { VARIANT_COLOR_MAP } from '@/constants/sliderColors'

const Slider = ({
  defaultValue = [0],
  max = 5,
  step = 0.5,
  label,
  variant = 'sweetness',
  value,
  onValueChange,
  className,
  formatValue,
}: SliderProps) => {
  const color = VARIANT_COLOR_MAP[variant]
  const displayValue = value?.[0] ?? 0

  return (
    <div
      className={clsx(
        'flex w-full flex-col gap-3 sm:flex-row sm:items-center lg:w-[480px]',
        className
      )}
    >
      <span className="text-5 w-13 shrink-0 text-left font-bold text-[#333333] select-none sm:mr-[44px] sm:text-center">
        {label}
      </span>
      <div className="flex min-w-0 flex-1 items-center">
        <div className="mr-3 shrink-0 text-[18px] font-light sm:text-[22px]">
          {formatValue ? formatValue(0) : '0'}
        </div>
        <SliderPrimitive.Root
          defaultValue={defaultValue}
          value={value}
          onValueChange={onValueChange}
          max={max}
          step={step}
          className={clsx(
            'relative flex h-[20px] min-w-0 flex-1 cursor-pointer touch-none items-center select-none sm:w-[308px] sm:flex-none',
            className
          )}
        >
          <SliderPrimitive.Track className="relative h-full w-full rounded-full bg-[#DFDFDF]">
            <SliderPrimitive.Range
              className="absolute h-full rounded-full"
              style={{ backgroundColor: color }}
            />
          </SliderPrimitive.Track>
          <SliderPrimitive.Thumb asChild>
            <div
              className="flex h-[40px] w-[40px] items-center justify-center rounded-full border-[3px] bg-[#FFFFFF] outline-none"
              style={{ borderColor: color }}
            >
              <div
                className="h-[24px] w-[24px] rounded-full"
                style={{ backgroundColor: color }}
              />
            </div>
          </SliderPrimitive.Thumb>
        </SliderPrimitive.Root>
        <div className="ml-3 shrink-0 text-[18px] font-light sm:text-[22px]">
          {formatValue ? formatValue(displayValue) : displayValue.toFixed(1)}
        </div>
      </div>
    </div>
  )
}

export default Slider
