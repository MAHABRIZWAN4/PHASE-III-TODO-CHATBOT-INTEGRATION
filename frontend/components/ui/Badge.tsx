'use client';

import { HTMLAttributes, ReactNode, forwardRef } from 'react';

/**
 * Badge component for labels and status indicators
 *
 * @example
 * ```tsx
 * <Badge variant="primary" size="md">
 *   New
 * </Badge>
 *
 * <Badge variant="success" size="sm">
 *   Completed
 * </Badge>
 * ```
 */

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Visual style variant */
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  /** Size of the badge */
  size?: 'sm' | 'md' | 'lg';
  /** Badge content */
  children: ReactNode;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'primary', size = 'md', children, className = '', ...props }, ref) => {
    // Base styles
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-full';

    // Variant styles
    const variantStyles = {
      primary: 'bg-primary-100 text-primary-700',
      secondary: 'bg-secondary-100 text-secondary-700',
      success: 'bg-semantic-success-light text-semantic-success-dark',
      error: 'bg-semantic-error-light text-semantic-error-dark',
      warning: 'bg-semantic-warning-light text-semantic-warning-dark',
      info: 'bg-semantic-info-light text-semantic-info-dark',
    };

    // Size styles
    const sizeStyles = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-sm',
      lg: 'px-3 py-1.5 text-base',
    };

    const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

    return (
      <span ref={ref} className={combinedClassName} {...props}>
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';
