import ArrowLeftIcon from '@/assets/icons/carousel/arrow_left.svg?react'
import ArrowRightIcon from '@/assets/icons/carousel/arrow_right.svg?react'
import Icon from '@/components/common/Icon'
import CardRenderer, {
  type CardListItem,
} from '@/components/common/cards/CardRenderer'
import { useCarouselSlides } from '@/hooks/useCarouselSlides'

type CarouselResponsive = {
  mobile?: number
  tablet?: number
  desktop?: number
}

interface CardCarouselProps {
  type: 'default' | 'review' | 'test' | 'best'
  cards: CardListItem[]
  slidesToShow: number
  gap: string
  responsive?: CarouselResponsive
}

const CardCarousel = ({
  type,
  cards,
  slidesToShow,
  gap,
  responsive,
}: CardCarouselProps) => {
  const {
    currentIndex,
    currentSlidesToShow,
    totalSlides,
    showArrows,
    handlePrev,
    handleNext,
  } = useCarouselSlides({
    itemCount: cards.length,
    slidesToShow,
    responsive,
  })

  return (
    <div className="relative w-full px-12 md:px-16 xl:px-20">
      {showArrows && (
        <button
          type="button"
          onClick={handlePrev}
          className="absolute top-1/2 left-1 z-10 flex -translate-y-1/2 items-center justify-center transition-all duration-200 hover:scale-105 md:left-2"
          aria-label="이전 슬라이드"
        >
          <Icon icon={ArrowLeftIcon} size={40} color="#000" />
        </button>
      )}

      <div className="mx-auto w-full max-w-[1281px] overflow-hidden">
        <div
          className="flex transition-transform duration-500 ease-in-out"
          style={{
            transform: `translateX(-${currentIndex * 100}%)`,
          }}
        >
          {Array.from({ length: totalSlides }, (_, slideIndex) => {
            const startIndex = slideIndex * currentSlidesToShow
            const endIndex = Math.min(
              startIndex + currentSlidesToShow,
              cards.length
            )
            const slideCards = cards.slice(startIndex, endIndex)

            return (
              <div
                key={slideIndex}
                className="grid w-full shrink-0"
                style={{
                  gap,
                  gridTemplateColumns: `repeat(${currentSlidesToShow}, minmax(0, 1fr))`,
                }}
              >
                {slideCards.map((card, cardIndex) => (
                  <div
                    key={`${slideIndex}-${cardIndex}`}
                    className="flex min-w-0 justify-center"
                  >
                    <CardRenderer type={type} card={card} />
                  </div>
                ))}
                {Array.from(
                  { length: currentSlidesToShow - slideCards.length },
                  (_, emptyIndex) => (
                    <div key={`empty-${slideIndex}-${emptyIndex}`} />
                  )
                )}
              </div>
            )
          })}
        </div>
      </div>

      {showArrows && (
        <button
          type="button"
          onClick={handleNext}
          className="absolute top-1/2 right-1 z-10 flex -translate-y-1/2 items-center justify-center transition-all duration-200 hover:scale-105 md:right-2"
          aria-label="다음 슬라이드"
        >
          <Icon icon={ArrowRightIcon} size={40} color="#000" />
        </button>
      )}
    </div>
  )
}

export default CardCarousel
