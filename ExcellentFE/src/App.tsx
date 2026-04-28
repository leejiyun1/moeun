import Layout from '@/components/layout/Layout'
import MyPageLayout from '@/components/layout/MyPageLayout'
import { RequireAdmin } from '@/components/RequireAdmin'
import { RequireAuth } from '@/components/RequireAuth'
import { ROUTE_PATHS } from '@/constants/routePaths'
import { useAuthStore } from '@/stores/authStore'
import { setOnUnauthorized } from '@/utils/axios'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { lazy, Suspense, useEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'
import ScrollToTop from '@/components/common/ScrollToTop'

const queryClient = new QueryClient()

const Login = lazy(() => import('@/pages/auth/Login'))
const SocialCallback = lazy(() => import('@/pages/auth/SocialCallback'))
const AdultCallback = lazy(() => import('@/pages/auth/AdultCallback'))
const AdultAuthManual = lazy(() => import('@/pages/auth/AdultAuthManual'))
const Cart = lazy(() => import('@/pages/Cart'))
const Home = lazy(() => import('@/pages/Index'))
const Package = lazy(() => import('@/pages/Package'))
const Search = lazy(() => import('@/pages/Search'))
const Feedback = lazy(() => import('@/pages/Feedback'))
const Detail = lazy(() => import('@/pages/Detail'))
const TestMain = lazy(() => import('@/pages/tasteTest'))
const AccountEdit = lazy(() => import('@/pages/my-page/AccountEdit'))
const OrderHistory = lazy(() => import('@/pages/my-page/OrderHistory'))
const TasteProfile = lazy(() => import('@/pages/my-page/TasteProfile'))
const TastingHistory = lazy(() => import('@/pages/my-page/TastingHistory'))
const NotFound = lazy(() => import('@/pages/NotFound'))
const AdminHome = lazy(() => import('@/pages/admin/AdminHome'))
const AdminPlaceholder = lazy(() => import('@/pages/admin/AdminPlaceholder'))

function App() {
  const navigate = useNavigate()
  const { initializeAuth } = useAuthStore()

  useEffect(() => {
    setOnUnauthorized(() => {
      navigate(ROUTE_PATHS.LOGIN)
    })
  }, [navigate])

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <QueryClientProvider client={queryClient}>
      <ScrollToTop />
      <Suspense fallback={null}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/auth/:provider/callback"
            element={<SocialCallback />}
          />
          <Route path="/auth/adult-manual" element={<AdultAuthManual />} />
          <Route
            path="/auth/adult-verification/callback"
            element={<AdultCallback />}
          />

          <Route
            path="admin"
            element={
              <RequireAdmin>
                <AdminHome />
              </RequireAdmin>
            }
          />
          <Route
            path="admin/products"
            element={
              <RequireAdmin>
                <AdminPlaceholder
                  title="상품 관리"
                  description="일반 상품과 패키지 상품을 관리하는 화면입니다."
                />
              </RequireAdmin>
            }
          />
          <Route
            path="admin/products/new"
            element={
              <RequireAdmin>
                <AdminPlaceholder
                  title="상품 등록"
                  description="일반 상품과 패키지 상품을 등록하는 화면입니다."
                />
              </RequireAdmin>
            }
          />
          <Route
            path="admin/package-policies"
            element={
              <RequireAdmin>
                <AdminPlaceholder
                  title="패키지 정책"
                  description="시음 가능 여부와 패키지 구성 정책을 관리하는 화면입니다."
                />
              </RequireAdmin>
            }
          />

          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="package" element={<Package />} />
            <Route path="test" element={<TestMain />} />
            <Route path="search" element={<Search />} />
            <Route path="feedback" element={<Feedback />} />
            <Route path="product/:id" element={<Detail />} />
            <Route path="package/:id" element={<Detail />} />
            <Route
              path="cart"
              element={
                <RequireAuth>
                  <Cart />
                </RequireAuth>
              }
            />

            {/* 마이페이지 라우팅 */}
            <Route
              path="mypage"
              element={
                <RequireAuth>
                  <MyPageLayout />
                </RequireAuth>
              }
            >
              <Route index element={<Navigate to="taste-profile" replace />} />
              <Route path="taste-profile" element={<TasteProfile />} />
              <Route path="account-edit" element={<AccountEdit />} />
              <Route path="order-history" element={<OrderHistory />} />
              <Route path="tasting-history" element={<TastingHistory />} />
            </Route>

            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
    </QueryClientProvider>
  )
}

export default App
