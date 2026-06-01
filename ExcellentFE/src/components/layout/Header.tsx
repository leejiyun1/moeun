import CartIcon from '@/assets/icons/header/cart.svg?react'
import MypageIcon from '@/assets/icons/header/mypage.svg?react'
import Logo from '@/assets/logos/logo.svg'
import Icon from '@/components/common/Icon'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { Z_INDEX } from '@/foundations/zIndex'
import { useAuthStore } from '@/stores/authStore'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const NAV_ITEMS = [
  { label: '패키지', path: ROUTE_PATHS.PACKAGE },
  { label: '테스트', path: ROUTE_PATHS.TEST },
  { label: '제품 검색', path: ROUTE_PATHS.SEARCH },
  { label: '후기', path: ROUTE_PATHS.FEEDBACK },
]

const USER_ICONS = [
  { label: '마이페이지', icon: MypageIcon, path: ROUTE_PATHS.MYPAGE.INDEX },
  { label: '장바구니', icon: CartIcon, path: ROUTE_PATHS.CART },
]

const Header = () => {
  const { isLoggedIn, logout } = useAuthStore()
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const closeMenu = () => setIsMenuOpen(false)

  const handleLogout = () => {
    logout()
    closeMenu()
    navigate(ROUTE_PATHS.HOME)
  }

  return (
    <header
      className="fixed top-0 left-0 w-full border-b border-[#d9d9d9] bg-white"
      style={{ zIndex: Z_INDEX.HEADER }}
    >
      <div className="mx-auto flex h-16 w-full max-w-[1440px] items-center justify-between px-5 md:h-[90px] md:px-10 xl:px-20">
        <Link
          to={ROUTE_PATHS.HOME}
          aria-label="홈으로 이동"
          onClick={closeMenu}
        >
          <img
            src={Logo}
            alt="모은 한잔취향 로고"
            className="h-9 w-auto md:h-auto"
          />
        </Link>

        <div className="hidden items-center gap-10 lg:flex xl:gap-15">
          <nav>
            <ul className="flex gap-8 xl:gap-15">
              {NAV_ITEMS.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className="text-lg font-semibold text-[#333]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div className="flex items-center">
            {!isLoggedIn ? (
              <Link
                to={ROUTE_PATHS.LOGIN}
                className="h-13 w-41 rounded-[60px] bg-[#f2544b] text-center leading-[52px] font-semibold text-white hover:bg-[#e04439]"
              >
                로그인/회원가입
              </Link>
            ) : (
              <div className="flex items-center gap-8">
                {USER_ICONS.map((icon) => (
                  <Link key={icon.label} to={icon.path} aria-label={icon.label}>
                    <Icon icon={icon.icon} size={32} />
                  </Link>
                ))}
                <button
                  type="button"
                  className="h-13 w-30 cursor-pointer rounded-4xl border border-[#d9d9d9] font-semibold text-[#666666]"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </div>

        <button
          type="button"
          className="flex h-11 w-11 items-center justify-center rounded-full border border-[#d9d9d9] text-[#333333] lg:hidden"
          aria-label={isMenuOpen ? '메뉴 닫기' : '메뉴 열기'}
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((prev) => !prev)}
        >
          {isMenuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {isMenuOpen && (
        <div className="border-t border-[#eeeeee] bg-white px-5 py-5 shadow-[0_12px_24px_rgba(0,0,0,0.08)] lg:hidden">
          <nav>
            <ul className="flex flex-col gap-4">
              {NAV_ITEMS.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className="block py-2 text-lg font-semibold text-[#333333]"
                    onClick={closeMenu}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div className="mt-5 border-t border-[#eeeeee] pt-5">
            {!isLoggedIn ? (
              <Link
                to={ROUTE_PATHS.LOGIN}
                className="flex h-12 w-full items-center justify-center rounded-full bg-[#f2544b] font-semibold text-white"
                onClick={closeMenu}
              >
                로그인/회원가입
              </Link>
            ) : (
              <div className="flex flex-col gap-4">
                {USER_ICONS.map((icon) => (
                  <Link
                    key={icon.label}
                    to={icon.path}
                    className="flex items-center gap-3 py-2 font-semibold text-[#333333]"
                    onClick={closeMenu}
                  >
                    <Icon icon={icon.icon} size={26} />
                    {icon.label}
                  </Link>
                ))}
                <button
                  type="button"
                  className="h-12 rounded-full border border-[#d9d9d9] font-semibold text-[#666666]"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  )
}

export default Header
