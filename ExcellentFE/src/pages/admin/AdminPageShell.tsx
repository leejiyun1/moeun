import { ROUTE_PATHS } from '@/constants/routePaths'
import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

interface AdminPageShellProps {
  title: string
  description: string
  action?: ReactNode
  children: ReactNode
}

const AdminPageShell = ({
  title,
  description,
  action,
  children,
}: AdminPageShellProps) => {
  return (
    <main className="min-h-screen bg-white px-5 pt-[130px] pb-24 text-[#333333] md:px-10 md:pt-[150px]">
      <div className="mx-auto w-full max-w-[1280px]">
        <div className="mb-10 flex flex-col gap-6 border-b border-[#d9d9d9] pb-8 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-3 text-sm font-bold tracking-[0.18em] text-[#f2544b] uppercase">
              Admin
            </p>
            <h1 className="text-[32px] leading-tight font-bold md:text-[36px]">
              {title}
            </h1>
            <p className="mt-4 max-w-[720px] text-base text-[#666666] md:text-lg">
              {description}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              to={ROUTE_PATHS.ADMIN.INDEX}
              className="rounded-full border border-[#d9d9d9] px-5 py-3 text-sm font-bold text-[#666666] transition hover:border-[#f2544b] hover:text-[#f2544b]"
            >
              관리자 홈
            </Link>
            {action}
          </div>
        </div>
        {children}
      </div>
    </main>
  )
}

export default AdminPageShell
