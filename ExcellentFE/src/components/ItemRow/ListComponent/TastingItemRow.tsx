import SafeImage from '@/components/common/SafeImage'

interface TastingItemRowProps {
  img: string
  name: string
  order: string
  feedback: string
}

const TastingItemRow = ({
  img,
  name,
  order,
  feedback,
}: TastingItemRowProps) => {
  return (
    <div className="flex items-center border-b border-[#e1e1e1] py-4 text-[#666666]">
      <div className="ml-10 flex items-center justify-center gap-4">
        <SafeImage
          src={img}
          alt={name}
          className="h-25 w-25 rounded-[5px] border border-[#d9d9d9] object-contain"
        />
        <p className="w-36 text-left text-base font-bold whitespace-nowrap">
          {name}
        </p>
      </div>
      <div className="ml-38 w-[20%] text-center text-lg">{order}</div>
      <div className="ml-34 w-95 text-left text-lg leading-6 font-semibold tracking-[0.05em] text-[#666666]">
        <p className="font-normal">{feedback}</p>
      </div>
    </div>
  )
}

export default TastingItemRow
