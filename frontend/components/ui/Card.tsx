'use client';

import { HTMLAttributes, ReactNode, forwardRef } from 'react';

/**
 * Card component with multiple variants
 *
 * @example
 * ```tsx
 * <Card variant="default">
 *   <Card.Header>
 *     <h3>Card Title</h3>
 *   </Card.Header>
 *   <Card.Body>
 *     Card content goes here
 *   </Card.Body>
 *   <Card.Footer>
 *     <Button>Action</Button>
 *   </Card.Footer>
 * </Card>
 *
 * <Card variant="interactive" onClick={handleClick}>
 *   Clickable card
 * </Card>
 * ```
 */

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Visual style variant */
  variant?: 'default' | 'elevated' | 'interactive';
  /** Card content */
  children: ReactNode;
}

const CardRoot = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', children, className = '', onClick, ...props }, ref) => {
    // Base styles
    const baseStyles = 'bg-white rounded-lg transition-shadow duration-200';

    // Variant styles
    const variantStyles = {
      default: 'shadow-sm border border-neutral-200 p-6 hover:shadow-md',
      elevated: 'shadow-lg rounded-xl p-6 hover:shadow-xl hover:-translate-y-1 transition-all',
      interactive:
        'shadow-sm border border-neutral-200 p-6 hover:shadow-md cursor-pointer hover:border-primary-300',
    };

    const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className}`;

    return (
      <div ref={ref} className={combinedClassName} onClick={onClick} {...props}>
        {children}
      </div>
    );
  }
);

CardRoot.displayName = 'Card';

/**
 * Card Header component
 */
interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className = '', ...props }, ref) => {
    return (
      <div ref={ref} className={`mb-4 ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardHeader.displayName = 'Card.Header';

/**
 * Card Body component (also exported as CardContent for compatibility)
 */
interface CardBodyProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

const CardBody = forwardRef<HTMLDivElement, CardBodyProps>(
  ({ children, className = '', ...props }, ref) => {
    return (
      <div ref={ref} className={className} {...props}>
        {children}
      </div>
    );
  }
);

CardBody.displayName = 'Card.Body';

// Alias for CardBody to match common UI library conventions
const CardContent = CardBody;

/**
 * Card Footer component
 */
interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, className = '', ...props }, ref) => {
    return (
      <div ref={ref} className={`mt-4 ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'Card.Footer';

// Create compound component with proper TypeScript typing
type CardComponent = typeof CardRoot & {
  Header: typeof CardHeader;
  Body: typeof CardBody;
  Content: typeof CardContent;
  Footer: typeof CardFooter;
};

// Attach subcomponents to Card
const Card = CardRoot as CardComponent;
Card.Header = CardHeader;
Card.Body = CardBody;
Card.Content = CardContent;
Card.Footer = CardFooter;

// Export Card and subcomponents
export { Card, CardHeader, CardBody, CardContent, CardFooter };
