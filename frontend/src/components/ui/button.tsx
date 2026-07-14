import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default:
          'bg-accent text-[#0d0d0d] hover:bg-teal font-semibold shadow-[0_0_24px_-6px_rgba(0,209,255,0.75)]',
        accent:
          'bg-teal text-[#0d0d0d] hover:bg-accent font-semibold shadow-[0_0_24px_-6px_rgba(0,209,255,0.65)]',
        outline:
          'border border-border dark:border-cyan-500/25 bg-transparent text-slate-800 dark:text-slate-100 hover:bg-cyan-50 dark:hover:bg-[#1a1a1a]',
        ghost: 'hover:bg-cyan-50 dark:hover:bg-[#1a1a1a] text-slate-700 dark:text-slate-200',
        danger: 'bg-danger text-white hover:brightness-110',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-12 px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    )
  },
)
Button.displayName = 'Button'
