import Logo from '@/assets/logos/logo-footer.svg'
import { Z_INDEX } from '@/foundations/zIndex'
import { cn } from '@/utils/cn'
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Footer = () => {
  const [isVisible, setIsVisible] = useState(false)
  const location = useLocation()

  const floatingPages = ['/', '/package']
  const isFloatingPage = floatingPages.includes(location.pathname)

  useEffect(() => {
    if (!isFloatingPage) {
      setIsVisible(true)
      return
    }

    const handleScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      const isNearBottom = scrollTop + windowHeight >= documentHeight - 100

      setIsVisible(isNearBottom)
    }

    handleScroll()
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isFloatingPage])

  return (
    <footer
      className={cn(
        'w-full bg-[#2E2F2F] text-white',
        isFloatingPage
          ? [
              'relative md:fixed md:right-0 md:bottom-0 md:left-0',
              'md:transition-transform md:duration-300',
              isVisible ? 'md:translate-y-0' : 'md:translate-y-full',
            ]
          : 'relative mt-auto'
      )}
      style={{ zIndex: Z_INDEX.FOOTER }}
    >
      <div className="mx-auto flex min-h-[255px] w-full max-w-[1440px] flex-col justify-between px-5 py-8 text-xs leading-6 sm:px-8 md:px-10 md:py-[50px] md:text-sm xl:px-20 2xl:px-80">
        <div className="mb-6 flex flex-col items-start justify-between gap-6 lg:flex-row lg:items-center">
          <div className="flex flex-col gap-1.5 break-keep">
            <span>상호명 : 모은 | 대표 : 김영선</span>
            <span>
              주소 : 인천광역시 부평구 충선로209번길 13, 407-1호 | 고객센터 :
              070-8835-1898
            </span>
            <span>사업자등록번호 : 147-10-03095</span>
          </div>

          <Link to="/" aria-label="홈으로 이동" className="shrink-0">
            <img
              src={Logo}
              alt="모은 취향 추천 로고"
              className="h-10 w-auto md:h-auto"
            />
          </Link>
        </div>

        <div className="border-t border-white/30 pt-6 md:pt-8">
          <p className="text-white/50">
            Copyright © 모은. All right reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
