/**
 * UI Component Library
 *
 * Comprehensive reusable UI components following the Tailwind Design System
 *
 * @example
 * ```tsx
 * import { Button, Input, Card, Badge } from '@/components/ui';
 *
 * <Button variant="primary" size="md">Click me</Button>
 * <Input type="email" placeholder="Enter email" />
 * <Card variant="elevated">Card content</Card>
 * <Badge variant="success">New</Badge>
 * ```
 */

export { Button } from './Button';
export type { ButtonProps } from './Button';

export { Input } from './Input';
export type { InputProps } from './Input';

export { Card, CardHeader, CardBody, CardFooter } from './Card';
export type { CardProps } from './Card';

export { Badge } from './Badge';
export type { BadgeProps } from './Badge';

export { Avatar } from './Avatar';
export type { AvatarProps } from './Avatar';

export { Modal } from './Modal';
export type { ModalProps } from './Modal';

export { Toast, ToastContainer } from './Toast';
export type { ToastProps, ToastContainerProps } from './Toast';

export { Spinner } from './Spinner';
export type { SpinnerProps } from './Spinner';

export { Skeleton, SkeletonGroup } from './Skeleton';
export type { SkeletonProps, SkeletonGroupProps } from './Skeleton';
