'use client';

import { ImgHTMLAttributes, forwardRef, useState } from 'react';

/**
 * Avatar component for displaying user images or initials
 *
 * @example
 * ```tsx
 * <Avatar src="/avatar.jpg" alt="John Doe" size="md" />
 *
 * <Avatar initials="JD" size="lg" />
 * ```
 */

export interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size'> {
  /** Image source URL */
  src?: string;
  /** Alt text for the image */
  alt?: string;
  /** User name (used to generate initials if initials not provided) */
  name?: string;
  /** Initials to display if image fails or is not provided */
  initials?: string;
  /** Size of the avatar */
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ src, alt, name, initials, size = 'md', className = '', ...props }, ref) => {
    const [imageError, setImageError] = useState(false);

    // Size styles
    const sizeStyles = {
      sm: 'w-8 h-8 text-xs',
      md: 'w-10 h-10 text-sm',
      lg: 'w-12 h-12 text-base',
      xl: 'w-16 h-16 text-lg',
    };

    // Base styles
    const baseStyles =
      'rounded-full flex items-center justify-center font-medium overflow-hidden';

    // Background color for initials
    const initialsStyles = 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300';

    const combinedClassName = `${baseStyles} ${sizeStyles[size]} ${className}`;

    // Show initials if no image, image failed, or no src provided
    const showInitials = !src || imageError;

    // Generate initials from name, alt text, or initials prop
    const displayInitials =
      initials ||
      (name
        ? name
            .split(' ')
            .map((word) => word[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)
        : alt
        ? alt
            .split(' ')
            .map((word) => word[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)
        : '?');

    return (
      <div ref={ref} className={combinedClassName}>
        {showInitials ? (
          <span className={`${initialsStyles} w-full h-full flex items-center justify-center`}>
            {displayInitials}
          </span>
        ) : (
          <img
            src={src}
            alt={alt}
            onError={() => setImageError(true)}
            className="w-full h-full object-cover"
            {...props}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';
