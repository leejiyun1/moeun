import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { Outlet } from 'react-router-dom'

const Layout = () => {
  return (
    <>
      <Header />
      <div className="mt-16 flex min-h-screen flex-col md:mt-[90px]">
        <main className="min-w-0">
          <Outlet />
        </main>
      </div>
      <Footer />
    </>
  )
}

export default Layout
