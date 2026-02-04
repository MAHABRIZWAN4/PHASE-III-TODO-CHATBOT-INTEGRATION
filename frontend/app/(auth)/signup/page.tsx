'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Brain, User, Mail, Lock, Eye, EyeOff, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { setAuthToken, setAuthUser } from '@/lib/auth';

export default function SignupPage() {
  const router = useRouter();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Password strength calculation
  const getPasswordStrength = (password: string): 'weak' | 'medium' | 'strong' | null => {
    if (!password) return null;
    if (password.length < 8) return 'weak';

    const hasLetters = /[a-zA-Z]/.test(password);
    const hasNumbers = /[0-9]/.test(password);
    const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (hasLetters && hasNumbers && hasSpecialChars) return 'strong';
    if ((hasLetters && hasNumbers) || (hasLetters && hasSpecialChars) || (hasNumbers && hasSpecialChars)) return 'medium';
    return 'weak';
  };

  const passwordStrength = getPasswordStrength(formData.password);

  // Form validation
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Full name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Terms validation
    if (!formData.acceptTerms) {
      newErrors.acceptTerms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Form submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setErrors({});

    // Validate form
    if (!validateForm()) {
      setError('Please fix the errors above');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed. Please try again.');
      }

      // Store token and user data
      setAuthToken(data.token);
      setAuthUser(data.user);

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Clear field error on change
  const handleFieldChange = (field: string, value: string | boolean) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Signup Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-md w-full space-y-8">
          {/* Logo and Header */}
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Brain className="w-10 h-10 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-neutral-900">Create your account</h1>
            <p className="mt-2 text-sm text-neutral-600">
              Start managing your tasks with AI
            </p>
          </div>

          {/* Signup Form */}
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
              {/* Name Input */}
              <Input
                id="name"
                name="name"
                type="text"
                label="Full name"
                placeholder="John Doe"
                value={formData.name}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                icon={<User className="w-5 h-5" />}
                iconPosition="left"
                error={errors.name}
                required
                disabled={loading}
                aria-label="Full name"
              />

              {/* Email Input */}
              <Input
                id="email"
                name="email"
                type="email"
                label="Email address"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                icon={<Mail className="w-5 h-5" />}
                iconPosition="left"
                error={errors.email}
                required
                disabled={loading}
                aria-label="Email address"
              />

              {/* Password Input */}
              <div>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    label="Password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => handleFieldChange('password', e.target.value)}
                    icon={<Lock className="w-5 h-5" />}
                    iconPosition="left"
                    error={errors.password}
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

                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="mt-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            passwordStrength === 'weak'
                              ? 'w-1/3 bg-semantic-error'
                              : passwordStrength === 'medium'
                              ? 'w-2/3 bg-semantic-warning'
                              : 'w-full bg-semantic-success'
                          }`}
                        />
                      </div>
                      <span
                        className={`text-xs font-medium ${
                          passwordStrength === 'weak'
                            ? 'text-semantic-error-dark'
                            : passwordStrength === 'medium'
                            ? 'text-semantic-warning-dark'
                            : 'text-semantic-success-dark'
                        }`}
                      >
                        {passwordStrength === 'weak'
                          ? 'Weak'
                          : passwordStrength === 'medium'
                          ? 'Medium'
                          : 'Strong'}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password Input */}
              <div className="relative">
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  label="Confirm password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={(e) => handleFieldChange('confirmPassword', e.target.value)}
                  icon={<Lock className="w-5 h-5" />}
                  iconPosition="left"
                  error={errors.confirmPassword}
                  required
                  disabled={loading}
                  aria-label="Confirm password"
                  className="pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-[38px] text-neutral-400 hover:text-neutral-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded p-1"
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  disabled={loading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Terms & Conditions */}
            <div>
              <div className="flex items-start">
                <input
                  id="accept-terms"
                  name="accept-terms"
                  type="checkbox"
                  checked={formData.acceptTerms}
                  onChange={(e) => handleFieldChange('acceptTerms', e.target.checked)}
                  className="checkbox mt-0.5"
                  disabled={loading}
                  aria-required="true"
                  aria-invalid={errors.acceptTerms ? 'true' : 'false'}
                />
                <label htmlFor="accept-terms" className="ml-2 text-sm text-neutral-700">
                  I agree to the{' '}
                  <Link
                    href="/terms"
                    className="font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
                    target="_blank"
                  >
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link
                    href="/privacy"
                    className="font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
                    target="_blank"
                  >
                    Privacy Policy
                  </Link>
                </label>
              </div>
              {errors.acceptTerms && (
                <p className="mt-1 text-sm text-semantic-error-dark" role="alert">
                  {errors.acceptTerms}
                </p>
              )}
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
              {loading ? 'Creating account...' : 'Create account'}
            </Button>

            {/* Login Link */}
            <p className="text-center text-sm text-neutral-600">
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-medium text-primary-600 hover:text-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-1"
              >
                Sign in
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
              Join thousands of productive users
            </h2>
            <p className="text-lg text-primary-100">
              Transform the way you manage tasks with AI-powered intelligence.
            </p>
          </div>

          {/* Feature List */}
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">AI-powered task management</h3>
                <p className="text-primary-100 text-sm">
                  Let AI help you organize, prioritize, and complete your tasks efficiently.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Natural language processing</h3>
                <p className="text-primary-100 text-sm">
                  Simply describe what you need to do in plain language.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Smart reminders and notifications</h3>
                <p className="text-primary-100 text-sm">
                  Never miss a deadline with intelligent reminders.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Collaborative workspaces</h3>
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
