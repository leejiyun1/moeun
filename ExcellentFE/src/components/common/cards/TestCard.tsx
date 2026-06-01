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
    <div className="flex w-[130px] flex-col">
      <div className="relative mb-[9px] flex h-[125px] w-full items-center justify-center overflow-hidden rounded-[6px] border border-[#D9D9D9] bg-gray-200">
        <SafeImage
          src={imgSrc}
          alt={imgAlt}
          className="h-full w-full object-contain p-2"
        />
      </div>
      <p className="mb-[9px] text-sm font-bold text-[#333333]"> {title} </p>
      <p className="mb-[13px] text-xs font-bold text-[#666666]">{subtitle}</p>
      <div className="flex gap-1">
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
