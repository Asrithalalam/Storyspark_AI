import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Feather, Lock, Mail, User as UserIcon, Eye, EyeOff, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { ApiError } from '../services/api';

export const RegisterPage: React.FC = () => {
  const { register, isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Intended destination route or default to home
  const fromLocation = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  // If already authenticated, redirect immediately
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      navigate(fromLocation, { replace: true });
    }
  }, [isAuthenticated, authLoading, navigate, fromLocation]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setErrorMessage('Please enter your email address.');
      return;
    }

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please verify your password.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        email: trimmedEmail,
        password,
        full_name: fullName.trim() || undefined,
      });
      navigate(fromLocation, { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage('Failed to create account. Please check your information.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-1 items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Card Header */}
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#C85E45] to-[#8E7C9D] text-white shadow-md shadow-[#C85E45]/20 ring-1 ring-white/60">
            <Feather className="h-7 w-7" />
          </div>
          <h2 className="mt-5 font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#2B1B2A]">
            Begin Your Journey
          </h2>
          <p className="mt-1.5 font-serif text-xs sm:text-sm italic text-[#7D6B8D]">
            Create a StorySpark account to save and collect your stories.
          </p>
        </div>

        {/* Card Container */}
        <div className="rounded-2xl border border-[#EFE8DF] bg-[#FDFBF7]/90 p-6 sm:p-8 shadow-sm shadow-[#2B1B2A]/5 backdrop-blur-md">
          {/* Error Banner */}
          {errorMessage && (
            <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50/80 p-3.5 text-xs text-red-800 animate-in fade-in duration-200">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-600 mt-0.5" />
              <div className="flex-1 font-medium">{errorMessage}</div>
            </div>
          )}

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name Field */}
            <div>
              <label htmlFor="register-name" className="block text-xs font-semibold text-[#554553] mb-1.5">
                Full Name <span className="text-[#8E7C9D] font-normal">(optional)</span>
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#8E7C9D]">
                  <UserIcon className="h-4 w-4" />
                </div>
                <input
                  id="register-name"
                  type="text"
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Austen"
                  className="w-full rounded-xl border border-[#E8DFD5] bg-white pl-10 pr-4 py-2.5 text-xs text-[#2B1B2A] placeholder-[#A0939F] shadow-2xs transition-all focus:border-[#C85E45] focus:outline-none focus:ring-2 focus:ring-[#C85E45]/20"
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="register-email" className="block text-xs font-semibold text-[#554553] mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#8E7C9D]">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  id="register-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="author@example.com"
                  className="w-full rounded-xl border border-[#E8DFD5] bg-white pl-10 pr-4 py-2.5 text-xs text-[#2B1B2A] placeholder-[#A0939F] shadow-2xs transition-all focus:border-[#C85E45] focus:outline-none focus:ring-2 focus:ring-[#C85E45]/20"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="register-password" className="block text-xs font-semibold text-[#554553] mb-1.5">
                Password <span className="text-[#8E7C9D] font-normal">(min 8 characters)</span>
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#8E7C9D]">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  id="register-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-[#E8DFD5] bg-white pl-10 pr-10 py-2.5 text-xs text-[#2B1B2A] placeholder-[#A0939F] shadow-2xs transition-all focus:border-[#C85E45] focus:outline-none focus:ring-2 focus:ring-[#C85E45]/20"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3.5 text-[#8E7C9D] hover:text-[#554553] transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="register-confirm-password" className="block text-xs font-semibold text-[#554553] mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-[#8E7C9D]">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  id="register-confirm-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-[#E8DFD5] bg-white pl-10 pr-4 py-2.5 text-xs text-[#2B1B2A] placeholder-[#A0939F] shadow-2xs transition-all focus:border-[#C85E45] focus:outline-none focus:ring-2 focus:ring-[#C85E45]/20"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#C85E45] to-[#B24D35] px-4 py-2.5 text-xs font-semibold text-white shadow-sm shadow-[#C85E45]/25 hover:from-[#B8533B] hover:to-[#A3432C] focus:outline-none focus:ring-2 focus:ring-[#C85E45]/40 transition-all disabled:opacity-50 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-white" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </button>
          </form>

        </div>

        {/* Link to Login */}
        <p className="text-center text-xs text-[#6A5868]">
          Already have an account?{' '}
          <Link
            to="/login"
            state={{ from: { pathname: fromLocation } }}
            className="font-semibold text-[#C85E45] hover:text-[#B24D35] underline decoration-[#C85E45]/40 hover:decoration-[#C85E45] transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};
