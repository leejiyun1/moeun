import type { TestCardProps } from '@/types/cardProps'
import SafeImage from '@/components/common/SafeImage'

const TestCard = ({
  imgSrc,
  imgAlt,
  title,
  subtitle,
  firstLabel,
  secondLabel,
}: TestCardProps) => {
  return (
    <div className="flex w-[148px] flex-col sm:w-[154px]">
      <div className="relative mb-3 flex aspect-[1.18] w-full items-center justify-center overflow-hidden rounded-[6px] border border-[#D9D9D9] bg-white">
        <SafeImage
          src={imgSrc}
          alt={imgAlt}
          className="h-full w-full object-contain p-3"
        />
      </div>
      <p className="mb-2 text-[15px] leading-[1.35] font-bold text-[#333333]">
        {title}
      </p>
      <p className="mb-3 min-h-[34px] text-xs leading-[1.45] font-bold text-[#666666]">
        {subtitle}
      </p>
      <div className="flex flex-wrap gap-1.5">
        <p className="flex h-[25px] items-center justify-center bg-[#FFFFFF] px-2 py-[5px] text-[11px] text-[#F2544B]">
          {firstLabel}
        </p>
        <p className="flex h-[25px] items-center justify-center bg-[#FFFFFF] px-2 py-[5px] text-[11px] text-[#F2544B]">
          {secondLabel}
        </p>
      </div>
    </div>
  )
}

export default TestCard
