import type { CardBaseProps } from '@/types/cardProps'
import HeartButton from '@/components/common/HeartButton.tsx'
import SafeImage from '@/components/common/SafeImage'
import { useProductLike } from '@/hooks/product/useProductLike'

interface DetailCardProps extends CardBaseProps {
  className?: string
}

const DetailCard = ({
  id,
  imgSrc,
  imgAlt,
  isLiked: initialLiked,
  className,
}: DetailCardProps) => {
  const { isLiked, toggleLike } = useProductLike(id, initialLiked)
  return (
    <div className={className}>
      <div className="relative flex h-full w-full items-center justify-center overflow-hidden rounded-[6px] border border-[#D9D9D9] bg-gray-200">
        <SafeImage
          src={imgSrc}
          alt={imgAlt}
          className="h-full w-full object-contain p-4"
        />
        <HeartButton
          isLiked={isLiked}
          onClick={toggleLike}
          className="absolute right-2 bottom-2"
        />
      </div>
    </div>
  )
}

export default DetailCard
