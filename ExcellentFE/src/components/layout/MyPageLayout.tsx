import { Z_INDEX } from '@/foundations/zIndex'
import { useAuthStore } from '@/stores/authStore'
import { NavLink, Outlet } from 'react-router-dom'

const baseMenuItems = [
  { to: 'taste-profile', label: '나의 입맛 프로필' },
  { to: 'order-history', label: '주문/배송 내역' },
  { to: 'tasting-history', label: '나의 시음 히스토리' },
  { to: 'account-edit', label: '회원정보 수정' },
]

const MyPageLayout = () => {
  const { user } = useAuthStore()
  const isAdmin = user?.user_info.role === 'ADMIN'
  const menuItems = isAdmin
    ? [...baseMenuItems, { to: '/admin', label: '관리자' }]
    : baseMenuItems

  return (
    <div className="min-h-screen bg-white lg:flex">
      <nav
        className="sticky top-16 w-full border-b border-[#d9d9d9] bg-[#F2F2F2] px-5 py-5 md:top-[90px] lg:fixed lg:top-0 lg:left-0 lg:h-screen lg:w-[260px] lg:border-b-0 lg:px-[52px] lg:pt-[152px]"
        style={{ zIndex: Z_INDEX.SIDEBAR }}
      >
        <h2 className="mb-4 text-2xl font-bold text-[#333] lg:mb-8 lg:text-3xl">
          마이페이지
        </h2>
        <ul className="flex gap-3 overflow-x-auto text-sm text-[#666] lg:flex-col lg:gap-4 lg:overflow-visible lg:text-base">
          {menuItems.map(({ to, label }) => (
            <li key={to} className="shrink-0">
              <NavLink
                to={to}
                className={({ isActive }) =>
                  isActive
                    ? 'block border-b-2 border-[#333333] py-1 font-bold text-[#333333]'
                    : 'block py-1 font-medium'
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <section className="w-full px-5 pt-10 pb-[100px] sm:px-8 lg:ml-[320px] lg:max-w-[1280px] lg:px-0 lg:pt-[106px]">
        <Outlet />
      </section>
    </div>
  )
}

export default MyPageLayout
