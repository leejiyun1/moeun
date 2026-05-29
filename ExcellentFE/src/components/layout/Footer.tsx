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

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isFloatingPage])

  return (
    <footer
      className={cn(
        'text-base text-white',
        isFloatingPage
          ? [
              'fixed right-0 bottom-0 left-0',
              'transition-transform duration-300',
              isVisible ? 'translate-y-0' : 'translate-y-full',
            ]
          : 'relative mt-auto w-full'
      )}
      style={{
        backgroundColor: '#2E2F2F',
        height: '255px',
        zIndex: Z_INDEX.FOOTER,
      }}
    >
      <div className="max-w-10xl mx-auto flex h-full flex-col justify-between px-80 py-[50px] text-sm">
        <div className="mb-4 flex flex-col items-start justify-between space-y-4 lg:flex-row lg:items-center lg:space-y-0">
          <div className="flex flex-col space-y-2">
            <span>상호명 : 모은 | 대표 : 김영선</span>
            <span>
              주소 : 인천광역시 부평구 충선로209번길 13, 407-1호 | 고객센터 :
              070-8835-1898
            </span>
            <span>사업자등록번호 : 147-10-03095</span>
          </div>

          <Link to="/" aria-label="홈으로 이동" className="shrink-0">
            <img src={Logo} alt="모은 취향 추천 로고" />
          </Link>
        </div>

        <div className="border-t border-white/30 pt-8">
          <p className="text-white/50">Copyright © 모은. All right reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
