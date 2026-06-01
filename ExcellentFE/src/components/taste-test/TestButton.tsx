import type React from 'react'

interface TestButtonProps {
  className?: string
  onClick?: () => void
  children: React.ReactNode
  disabled?: boolean
}

const TestButton = ({
  className,
  onClick,
  children,
  disabled,
}: TestButtonProps) => {
  return (
    <button
      className={`h-[59px] w-full max-w-[460px] rounded-[60px] px-5 text-base sm:text-xl ${className} cursor-pointer`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}

export default TestButton
