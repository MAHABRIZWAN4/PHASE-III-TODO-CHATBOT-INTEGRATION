'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Button component with multiple variants and sizes
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </Button>
 *
 * <Button variant="danger" loading>
 *   Deleting...
 * </Button>
 * ```
 */

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Size of the button */
  size?: 'sm' | 'md' | 'lg';
  /** Show loading spinner and disable interaction */
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    // Base styles
    const baseStyles =
      'font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2';

    // Variant styles
    const variantStyles = {
      primary:
        'bg-primary-500 hover:bg-primary-600 active:bg-primary-700 text-white focus:ring-primary-500',
      secondary:
        'bg-neutral-100 hover:bg-neutral-200 active:bg-neutral-300 text-neutral-900 focus:ring-neutral-400',
      ghost:
        'text-neutral-700 hover:bg-neutral-100 active:bg-neutral-200 focus:ring-neutral-400',
      danger:
        'bg-semantic-error hover:bg-red-600 active:bg-red-700 text-white focus:ring-red-500',
    };

    // Size styles
    const sizeStyles = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={combinedClassName}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <Loader2 className="animate-spin" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
