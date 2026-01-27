'use client';

import { useEffect } from 'react';
import { X, CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

/**
 * Toast notification component with auto-dismiss
 *
 * @example
 * ```tsx
 * <Toast
 *   variant="success"
 *   message="Task created successfully!"
 *   duration={3000}
 *   onClose={() => setShowToast(false)}
 * />
 * ```
 */

export interface ToastProps {
  /** Visual style variant */
  variant: 'success' | 'error' | 'warning' | 'info';
  /** Message to display */
  message: string;
  /** Auto-dismiss duration in milliseconds (0 to disable) */
  duration?: number;
  /** Callback when toast is closed */
  onClose: () => void;
  /** Additional className */
  className?: string;
}

export const Toast = ({
  variant,
  message,
  duration = 5000,
  onClose,
  className = '',
}: ToastProps) => {
  // Auto-dismiss after duration
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  // Icon mapping
  const icons = {
    success: <CheckCircle size={20} />,
    error: <XCircle size={20} />,
    warning: <AlertTriangle size={20} />,
    info: <Info size={20} />,
  };

  // Variant styles
  const variantStyles = {
    success: 'bg-semantic-success-light border-semantic-success text-semantic-success-dark',
    error: 'bg-semantic-error-light border-semantic-error text-semantic-error-dark',
    warning: 'bg-semantic-warning-light border-semantic-warning text-semantic-warning-dark',
    info: 'bg-semantic-info-light border-semantic-info text-semantic-info-dark',
  };

  // Icon color styles
  const iconColorStyles = {
    success: 'text-semantic-success',
    error: 'text-semantic-error',
    warning: 'text-semantic-warning',
    info: 'text-semantic-info',
  };

  const combinedClassName = `${variantStyles[variant]} border-l-4 px-4 py-3 rounded-r-lg shadow-lg min-w-[300px] max-w-[400px] flex items-start gap-3 animate-slide-in-right ${className}`;

  return (
    <div
      className={combinedClassName}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className={`flex-shrink-0 ${iconColorStyles[variant]}`}>
        {icons[variant]}
      </div>
      <p className="flex-1 text-sm font-medium">{message}</p>
      <button
        onClick={onClose}
        className="flex-shrink-0 text-current opacity-70 hover:opacity-100 transition-opacity focus:outline-none focus:ring-2 focus:ring-current rounded"
        aria-label="Close notification"
      >
        <X size={18} />
      </button>
    </div>
  );
};

Toast.displayName = 'Toast';

/**
 * Toast Container component for positioning toasts
 *
 * @example
 * ```tsx
 * <ToastContainer position="top-right">
 *   {toasts.map(toast => (
 *     <Toast key={toast.id} {...toast} />
 *   ))}
 * </ToastContainer>
 * ```
 */

export interface ToastContainerProps {
  /** Position of the toast container */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  /** Toast elements */
  children: React.ReactNode;
}

export const ToastContainer = ({
  position = 'top-right',
  children,
}: ToastContainerProps) => {
  const positionStyles = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  return (
    <div className={`fixed ${positionStyles[position]} z-50 flex flex-col gap-2`}>
      {children}
    </div>
  );
};

ToastContainer.displayName = 'ToastContainer';
