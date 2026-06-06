import GoogleIcon from '@/assets/icons/login/google.svg?react'
import KaKaoIcon from '@/assets/icons/login/kakao.svg?react'
import NaverIcon from '@/assets/icons/login/naver.svg?react'
import LoginBackground from '@/assets/images/backgrounds/login.jpg'
import LogoLeft from '@/assets/logos/logo-login.svg'
import LogoRight from '@/assets/logos/logo.svg'
import Button from '@/components/common/Button'
import Icon from '@/components/common/Icon'
import { useSocialLoginURL } from '@/hooks/auth/useSocialLogin'
import { type SocialProvider } from '@/types/auth'
import { Link } from 'react-router-dom'

interface SocialLogin {
  provider: SocialProvider
  icon: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  label: string
  className: string
}

const socialLogins: SocialLogin[] = [
  {
    provider: 'kakao',
    icon: KaKaoIcon,
    label: '카카오로 로그인',
    className: 'bg-[#FEE500] text-[#000]',
  },
  {
    provider: 'naver',
    icon: NaverIcon,
    label: '네이버로 로그인',
    className: 'bg-[#03C75A] text-[#FFF]',
  },
  {
    provider: 'google',
    icon: GoogleIcon,
    label: '구글로 로그인',
    className: 'border border-[#DFDFDF] bg-[#FFF]',
  },
]

const Login = () => {
  const { mutate: handleSocialLogin } = useSocialLoginURL()

  return (
    <div className="flex min-h-dvh w-full bg-white p-4 sm:p-5">
      <div
        className="relative hidden min-h-[calc(100dvh-40px)] w-full rounded-[20px] bg-cover bg-center bg-no-repeat xl:block xl:w-[55%]"
        style={{ backgroundImage: `url('${LoginBackground}')` }}
      >
        <Link
          to="/"
          aria-label="홈으로 이동"
          className="absolute top-1/2 left-1/2 z-10 -translate-x-1/2 -translate-y-1/2"
        >
          <img src={LogoLeft} alt="모은 로고" className="h-auto max-w-[240px]" />
        </Link>
      </div>
      <main className="relative flex min-h-[calc(100dvh-32px)] w-full items-center justify-center overflow-hidden rounded-2xl px-2 py-8 sm:min-h-[calc(100dvh-40px)] sm:px-6 xl:w-[45%] xl:px-10 xl:py-0">
        <div
          className="absolute inset-0 bg-cover bg-center xl:hidden"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.68), rgba(255,255,255,0.78)), url('${LoginBackground}')`,
          }}
        />
        <div className="relative z-10 flex w-full max-w-[440px] flex-col">
          <header className="flex flex-col items-center">
            <Link to="/" aria-label="홈으로 이동" className="mb-5">
              <img
                src={LogoRight}
                alt="모은 로고"
                className="h-auto w-[104px] sm:w-[118px]"
              />
            </Link>
            <h1 className="mb-12 text-center text-[19px] leading-8 font-semibold text-[#333] sm:mb-16 sm:text-[22px] xl:mb-20">
              로그인하고 나만의 전통주를 즐겨보세요!
            </h1>
          </header>
          <section className="flex w-full flex-col gap-3 sm:gap-5">
            {socialLogins.map(({ provider, icon, label, className }) => (
              <Button
                key={provider}
                variant={'VARIANT8'}
                className={`grid h-13 w-full grid-cols-[24px_1fr_24px] items-center rounded-xl px-5 text-[15px] tracking-normal sm:h-14 sm:text-base ${className}`}
                onClick={() => handleSocialLogin(provider)}
              >
                <Icon icon={icon} size={16} />
                <span className="text-center">{label}</span>
                <span aria-hidden="true" />
              </Button>
            ))}
          </section>
        </div>
      </main>
    </div>
  )
}

export default Login
