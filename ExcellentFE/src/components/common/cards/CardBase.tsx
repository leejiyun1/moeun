import type { CardBaseProps } from '@/types/cardProps'
import HeartButton from '@/components/common/HeartButton.tsx'
import SafeImage from '@/components/common/SafeImage'
import { Link } from 'react-router-dom'
import { useProductLike } from '@/hooks/product/useProductLike'

const CardBase = ({
  id,
  productType,
  imgSrc,
  imgAlt,
  title,
  subtitle,
  price,
  isLiked: initialLiked,
}: CardBaseProps) => {
  const detailPath =
    id && productType
      ? productType === 'PACKAGE'
        ? `/package/${id}`
        : `/product/${id}`
      : null
  const { isLiked, toggleLike } = useProductLike(id, initialLiked)

  return (
    <div className="mx-auto flex w-[220px] shrink-0 flex-col sm:w-[240px] md:w-full md:max-w-[260px] lg:max-w-[300px]">
      <div className="relative mb-5 flex aspect-square max-h-[290px] w-full max-w-[300px] items-center justify-center overflow-hidden rounded-[6px] border border-[#D9D9D9] bg-gray-200">
        {detailPath ? (
          <Link to={detailPath} className="h-full w-full">
            <SafeImage
              src={imgSrc}
              alt={imgAlt}
              className="h-full w-full object-contain p-3"
            />
          </Link>
        ) : (
          <SafeImage
            src={imgSrc}
            alt={imgAlt}
            className="h-full w-full object-contain p-3"
          />
        )}
        <HeartButton
          isLiked={isLiked}
          onClick={toggleLike}
          className="absolute right-2 bottom-2"
        />
      </div>

      {detailPath ? (
        <Link to={detailPath}>
          <h2 className="text-lg text-balance text-[#333333]">{title}</h2>
          <p className="mt-1 text-[#666666]">{subtitle}</p>
          <p className="mt-1 text-[15px] text-[#333333]">
            {price?.toLocaleString()}원
          </p>
        </Link>
      ) : (
        <>
          <h2 className="text-lg text-balance text-[#333333]">{title}</h2>
          <p className="mt-1 text-[#666666]">{subtitle}</p>
          <p className="mt-1 text-[15px] text-[#333333]">
            {price?.toLocaleString()}원
          </p>
        </>
      )}
    </div>
  )
}

export default CardBase
