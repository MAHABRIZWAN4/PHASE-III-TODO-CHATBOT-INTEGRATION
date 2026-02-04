'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Brain, Mail, Lock, Eye, EyeOff, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { setAuthToken, setAuthUser } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();

  console.log('[LoginPage] Component rendered');

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Log when component mounts
  useEffect(() => {
    console.log('[LoginPage] Component mounted - useEffect called');
  }, []);

  // Form validation
  const validateForm = () => {
    if (!formData.email) {
      setError('Email address is required');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (!formData.password) {
      setError('Password is required');
      return false;
    }
    return true;
  };

  // Form submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    console.log('[Login] Form submitted');

    // Validate form
    if (!validateForm()) {
      console.log('[Login] Form validation failed');
      return;
    }

    setLoading(true);
    console.log('[Login] Starting login request...');

    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`;
      console.log('[Login] API URL:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('[Login] Response status:', response.status);
      console.log('[Login] Response ok:', response.ok);

      const data = await response.json();
      console.log('[Login] Response data:', data);

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed. Please check your credentials.');
      }

      console.log('[Login] API Response:', data);
      console.log('[Login] Token:', data.token);
      console.log('[Login] User:', data.user);

      // Store token and user data
      console.log('[Login] Calling setAuthToken...');
      setAuthToken(data.token);
      console.log('[Login] Calling setAuthUser...');
      setAuthUser(data.user);

      console.log('[Login] Stored in localStorage');
      console.log('[Login] Token check:', localStorage.getItem('auth_token'));
      console.log('[Login] User check:', localStorage.getItem('auth_user'));

      // Use window.location for full page reload to ensure localStorage is written
      console.log('[Login] Redirecting to dashboard...');
      window.location.href = '/dashboard';
    } catch (err) {
      console.error('[Login] Error during login:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Login Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-md w-full space-y-8">
          {/* Logo and Header */}
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Brain className="w-10 h-10 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-neutral-900">Welcome back</h1>
            <p className="mt-2 text-sm text-neutral-600">
              Sign in to continue to your dashboard
            </p>
          </div>

          {/* Login Form */}
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {/* Error Alert */}
            {error && (
              <div
                className="alert-error animate-slide-down"
                role="alert"
                aria-live="polite"
              >
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{error}</p>
                </div>
              </div>
            )}

            <div className="space-y-4">
              {/* Email Input */}
              <Input
                id="email"
                name="email"
                type="email"
                label="Email address"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                icon={<Mail className="w-5 h-5" />}
                iconPosition="left"
                required
                disabled={loading}
                aria-label="Email address"
              />

              {/* Password Input */}
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  label="Password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  icon={<Lock className="w-5 h-5" />}
                  iconPosition="left"
                  required
                  disabled={loading}
                  aria-label="Password"
                  className="pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-neutral-400 hover:text-neutral-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded p-1"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  disabled={loading}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="checkbox"
                  disabled={loading}
                />
                <label htmlFor="remember-me" className="ml-2 text-sm text-neutral-700">
                  Remember me
                </label>
              </div>
              <Link
                href="/forgot-password"
                className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
              >
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              disabled={loading}
              className="w-full"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>

            {/* Sign Up Link */}
            <p className="text-center text-sm text-neutral-600">
              Don&apos;t have an account?{' '}
              <Link
                href="/signup"
                className="font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
              >
                Sign up for free
              </Link>
            </p>
          </form>
        </div>
      </div>

      {/* Right Side - Branding (Desktop Only) */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 to-secondary-600 items-center justify-center p-12">
        <div className="max-w-md text-white space-y-8">
          {/* Branding Content */}
          <div className="space-y-4">
            <h2 className="text-4xl font-bold leading-tight">
              Manage tasks with AI intelligence
            </h2>
            <p className="text-lg text-primary-100">
              Join thousands of users who are transforming their productivity with TaskAI.
            </p>
          </div>

          {/* Feature List */}
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Natural language task creation</h3>
                <p className="text-primary-100 text-sm">
                  Simply describe what you need to do, and let AI organize it for you.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Smart prioritization</h3>
                <p className="text-primary-100 text-sm">
                  AI automatically prioritizes your tasks based on urgency and importance.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Real-time collaboration</h3>
                <p className="text-primary-100 text-sm">
                  Work together seamlessly with your team in real-time.
                </p>
              </div>
            </div>
          </div>

          {/* Decorative Element */}
          <div className="pt-8 border-t border-primary-500/30">
            <p className="text-sm text-primary-100">
              Trusted by over 10,000+ professionals worldwide
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
