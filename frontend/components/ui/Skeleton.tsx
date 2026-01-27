'use client';

import { HTMLAttributes, forwardRef } from 'react';

/**
 * Skeleton component for loading placeholders
 *
 * @example
 * ```tsx
 * <Skeleton variant="text" width="200px" />
 * <Skeleton variant="circle" width="40px" height="40px" />
 * <Skeleton variant="rectangle" width="100%" height="100px" />
 * ```
 */

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /** Shape variant of the skeleton */
  variant?: 'text' | 'circle' | 'rectangle';
  /** Width of the skeleton */
  width?: string | number;
  /** Height of the skeleton */
  height?: string | number;
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  ({ variant = 'text', width, height, className = '', style, ...props }, ref) => {
    // Base styles
    const baseStyles = 'bg-neutral-200 animate-pulse';

    // Variant styles
    const variantStyles = {
      text: 'rounded h-4',
      circle: 'rounded-full',
      rectangle: 'rounded',
    };

    // Convert width/height to CSS values
    const getSize = (size: string | number | undefined) => {
      if (typeof size === 'number') return `${size}px`;
      return size;
    };

    const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className}`;

    const combinedStyle = {
      width: getSize(width),
      height: getSize(height),
      ...style,
    };

    return (
      <div
        ref={ref}
        className={combinedClassName}
        style={combinedStyle}
        aria-hidden="true"
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';

/**
 * SkeletonGroup component for multiple skeleton lines
 *
 * @example
 * ```tsx
 * <SkeletonGroup lines={3} />
 * ```
 */

export interface SkeletonGroupProps {
  /** Number of skeleton lines to display */
  lines?: number;
  /** Gap between skeleton lines */
  gap?: string;
  /** Width of each line */
  width?: string;
  /** Additional className */
  className?: string;
}

export const SkeletonGroup = ({
  lines = 3,
  gap = '0.5rem',
  width = '100%',
  className = '',
}: SkeletonGroupProps) => {
  return (
    <div className={`flex flex-col ${className}`} style={{ gap }}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          width={index === lines - 1 ? '60%' : width}
        />
      ))}
    </div>
  );
};

SkeletonGroup.displayName = 'SkeletonGroup';
