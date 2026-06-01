import defaultProductImage from '@/assets/images/default-product.svg'
import { cn } from '@/utils/cn'
import { useEffect, useState } from 'react'

interface SafeImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackSrc?: string
}

const SafeImage = ({
  src,
  fallbackSrc = defaultProductImage,
  alt,
  className,
  onError,
  ...props
}: SafeImageProps) => {
  const [currentSrc, setCurrentSrc] = useState(src || fallbackSrc)

  useEffect(() => {
    setCurrentSrc(src || fallbackSrc)
  }, [fallbackSrc, src])

  return (
    <img
      {...props}
      src={currentSrc}
      alt={alt || '모은 상품 이미지'}
      className={cn('bg-[#f8f8f8]', className)}
      onError={(event) => {
        if (currentSrc !== fallbackSrc) {
          setCurrentSrc(fallbackSrc)
        }
        onError?.(event)
      }}
    />
  )
}

export default SafeImage
