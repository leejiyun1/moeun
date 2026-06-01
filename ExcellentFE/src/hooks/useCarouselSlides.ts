import { useEffect, useState } from 'react'

type CarouselResponsive = {
  mobile?: number
  tablet?: number
  desktop?: number
}

type UseCarouselSlidesOptions = {
  itemCount: number
  slidesToShow: number
  responsive?: CarouselResponsive
  enabled?: boolean
}

export const useCarouselSlides = ({
  itemCount,
  slidesToShow,
  responsive,
  enabled = true,
}: UseCarouselSlidesOptions) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentSlidesToShow, setCurrentSlidesToShow] =
    useState<number>(slidesToShow)

  useEffect(() => {
    if (!enabled) {
      setCurrentIndex(0)
      setCurrentSlidesToShow(slidesToShow)
      return
    }

    const handleResize = () => {
      const width = window.innerWidth
      const mobileSlides = responsive?.mobile ?? 1
      const tabletSlides = responsive?.tablet ?? Math.min(2, slidesToShow)
      const desktopSlides = responsive?.desktop ?? slidesToShow

      if (width < 768) {
        setCurrentSlidesToShow(mobileSlides)
      } else if (width < 1024) {
        setCurrentSlidesToShow(tabletSlides)
      } else {
        setCurrentSlidesToShow(desktopSlides)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)

    return () => window.removeEventListener('resize', handleResize)
  }, [enabled, responsive, slidesToShow])

  const totalSlides = enabled ? Math.ceil(itemCount / currentSlidesToShow) : 0
  const showArrows = totalSlides > 1

  useEffect(() => {
    if (!enabled) return

    setCurrentIndex((prev) => Math.min(prev, Math.max(totalSlides - 1, 0)))
  }, [enabled, totalSlides])

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev === 0 ? totalSlides - 1 : prev - 1))
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === totalSlides - 1 ? 0 : prev + 1))
  }

  return {
    currentIndex,
    currentSlidesToShow,
    totalSlides,
    showArrows,
    handlePrev,
    handleNext,
  }
}
