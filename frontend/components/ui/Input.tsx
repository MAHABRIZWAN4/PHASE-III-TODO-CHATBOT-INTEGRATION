'use client';

import { InputHTMLAttributes, forwardRef, ReactNode } from 'react';

/**
 * Input component with validation states and icon support
 *
 * @example
 * ```tsx
 * <Input
 *   type="email"
 *   placeholder="Enter your email"
 *   value={email}
 *   onChange={(e) => setEmail(e.target.value)}
 * />
 *
 * <Input
 *   type="text"
 *   error="This field is required"
 *   icon={<SearchIcon />}
 *   iconPosition="left"
 * />
 * ```
 */

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Error message to display */
  error?: string;
  /** Success state indicator */
  success?: boolean;
  /** Icon element to display */
  icon?: ReactNode;
  /** Position of the icon */
  iconPosition?: 'left' | 'right';
  /** Label for the input */
  label?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      error,
      success,
      icon,
      iconPosition = 'left',
      label,
      className = '',
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${inputId}-error` : undefined;

    // Base styles
    const baseStyles =
      'w-full rounded-lg border bg-white text-neutral-900 placeholder-neutral-400 transition-colors duration-200 focus:outline-none disabled:bg-neutral-100 disabled:cursor-not-allowed';

    // State-based styles
    const stateStyles = error
      ? 'border-semantic-error focus:border-semantic-error focus:ring-2 focus:ring-red-500 focus:ring-offset-1'
      : success
      ? 'border-semantic-success focus:border-semantic-success focus:ring-2 focus:ring-green-500 focus:ring-offset-1'
      : 'border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:ring-offset-1';

    // Padding based on icon position
    const paddingStyles = icon
      ? iconPosition === 'left'
        ? 'pl-10 pr-4 py-2'
        : 'pl-4 pr-10 py-2'
      : 'px-4 py-2';

    const combinedClassName = `${baseStyles} ${stateStyles} ${paddingStyles} ${className}`;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-neutral-700 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            className={combinedClassName}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={errorId}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400">
              {icon}
            </div>
          )}
        </div>
        {error && (
          <p id={errorId} className="mt-1 text-sm text-semantic-error-dark" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
