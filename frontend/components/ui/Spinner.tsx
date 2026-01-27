'use client';

import { HTMLAttributes, forwardRef } from 'react';

/**
 * Spinner component for loading states
 *
 * @example
 * ```tsx
 * <Spinner size="md" />
 *
 * <div className="flex items-center gap-2">
 *   <Spinner size="sm" />
 *   <span>Loading...</span>
 * </div>
 * ```
 */

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg';
}

export const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  ({ size = 'md', className = '', ...props }, ref) => {
    // Size styles
    const sizeStyles = {
      sm: 'w-4 h-4 border-2',
      md: 'w-8 h-8 border-4',
      lg: 'w-12 h-12 border-4',
    };

    // Base styles
    const baseStyles =
      'animate-spin rounded-full border-neutral-200 dark:border-neutral-700 border-t-primary-500 dark:border-t-primary-400';

    const combinedClassName = `${baseStyles} ${sizeStyles[size]} ${className}`;

    return (
      <div
        ref={ref}
        className={combinedClassName}
        role="status"
        aria-label="Loading"
        {...props}
      >
        <span className="sr-only">Loading...</span>
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

/**
 * Full-page spinner component for loading states
 * Covers the entire screen with a centered spinner
 *
 * @example
 * ```tsx
 * <SpinnerFullPage />
 * ```
 */
export const SpinnerFullPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-neutral-900 dark:to-neutral-800">
      <Spinner size="lg" />
    </div>
  );
};

SpinnerFullPage.displayName = 'SpinnerFullPage';
