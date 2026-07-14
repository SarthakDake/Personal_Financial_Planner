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
          'bg-accent text-white hover:bg-blue-500 shadow-[0_8px_24px_-12px_rgba(59,130,246,0.8)]',
        accent:
          'bg-sky-400 text-slate-950 hover:bg-sky-300 shadow-[0_8px_24px_-12px_rgba(56,189,248,0.7)]',
        outline:
          'border border-border dark:border-border-dark bg-transparent text-slate-800 dark:text-slate-100 hover:bg-blue-50 dark:hover:bg-slate-800/80',
        ghost: 'hover:bg-blue-50 dark:hover:bg-slate-800/70 text-slate-700 dark:text-slate-200',
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
