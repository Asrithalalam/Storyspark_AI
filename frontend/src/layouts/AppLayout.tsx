import React, { useState } from 'react';
import { NavLink, Link, useLocation, useNavigate } from 'react-router-dom';
import { Sparkles, Home, BookOpen, Info, Menu, X, Feather, LogIn, LogOut } from 'lucide-react';
import { useStorySession } from '../hooks/useStorySession';
import { useAuth } from '../hooks/useAuth';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { clearActiveStory } = useStorySession();
  const { user, isAuthenticated, logout } = useAuth();

  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/stories', label: 'My Stories', icon: BookOpen },
    { to: '/about', label: 'About', icon: Info },
  ];

  const handleLinkClick = (to: string) => {
    if (to === '/') {
      clearActiveStory();
    }
    setMobileMenuOpen(false);
  };

  const handleLogout = async () => {
    setMobileMenuOpen(false);
    await logout();
    navigate('/login');
  };

  return (
    <div className="relative flex min-h-screen flex-col bg-[#FAF8F5] text-[#3D313C] overflow-x-hidden selection:bg-[#E07A5F]/20 selection:text-[#9E3F27]">
      {/* Subtle background storytelling motifs & ambient glow */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
        {/* Soft atmospheric gradient touches */}
        <div className="absolute -top-32 -left-32 h-[26rem] w-[26rem] rounded-full bg-[#E07A5F]/5 blur-3xl" />
        <div className="absolute top-1/4 right-0 h-96 w-96 rounded-full bg-[#9C8EB9]/7 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-[#F3D5B5]/10 blur-3xl" />

        {/* Faint constellation line art - top right */}
        <svg
          className="absolute top-12 right-12 w-80 h-80 opacity-[0.06] text-[#301B2E]"
          viewBox="0 0 200 200"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.2"
        >
          <circle cx="30" cy="40" r="3" fill="currentColor" />
          <circle cx="90" cy="20" r="2.5" fill="currentColor" />
          <circle cx="150" cy="60" r="3" fill="currentColor" />
          <circle cx="120" cy="120" r="2.5" fill="currentColor" />
          <circle cx="60" cy="140" r="3" fill="currentColor" />
          <line x1="30" y1="40" x2="90" y2="20" />
          <line x1="90" y1="20" x2="150" y2="60" />
          <line x1="150" y1="60" x2="120" y2="120" />
          <line x1="120" y1="120" x2="60" y2="140" />
          <line x1="60" y1="140" x2="30" y2="40" />
        </svg>

        {/* Faint open book line motif - bottom left */}
        <svg
          className="absolute -bottom-10 -left-10 w-96 h-96 opacity-[0.04] text-[#301B2E]"
          viewBox="0 0 200 200"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path d="M 20,140 Q 60,120 100,135 Q 140,120 180,140 L 180,60 Q 140,40 100,55 Q 60,40 20,60 Z" />
          <line x1="100" y1="55" x2="100" y2="135" />
        </svg>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-[#EFE8DF] bg-[#FDFBF7]/90 backdrop-blur-md shadow-[0_1px_4px_rgba(43,27,42,0.02)]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5 sm:px-6">
          {/* Brand Identity */}
          <Link
            to="/"
            onClick={() => handleLinkClick('/')}
            className="flex items-center gap-3 transition-opacity hover:opacity-95 group cursor-pointer"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#C85E45] to-[#8E7C9D] shadow-sm shadow-[#C85E45]/20 text-white ring-1 ring-white/60 transition-transform group-hover:scale-105">
              <Feather className="h-5 w-5" />
            </div>
            <div className="flex flex-col text-left">
              <span className="font-serif text-xl sm:text-2xl font-bold tracking-tight text-[#2B1B2A]">
                StorySpark AI
              </span>
              <p className="font-serif text-xs italic text-[#7D6B8D]">
                Where ideas become stories.
              </p>
            </div>
          </Link>

          {/* Desktop & Tablet Navigation */}
          <div className="hidden sm:flex items-center gap-2">
            <nav className="flex items-center gap-1.5" aria-label="Main Navigation">
              {navLinks.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  onClick={() => handleLinkClick(to)}
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-medium transition-all ${
                      isActive
                        ? 'border border-[#F0D5C9] bg-[#FAF3EE] text-[#C85E45] font-semibold shadow-2xs'
                        : 'border border-transparent text-[#6A5868] hover:border-[#E8DFD5] hover:bg-[#F3ECE4] hover:text-[#2B1B2A]'
                    }`
                  }
                >
                  <Icon className="h-3.5 w-3.5 text-[#C85E45]" />
                  <span>{label}</span>
                </NavLink>
              ))}
            </nav>

            {/* Auth Controls */}
            <div className="ml-2 pl-3 border-l border-[#EFE8DF] flex items-center gap-2">
              {isAuthenticated && user ? (
                <div className="flex items-center gap-2.5">
                  <div className="flex items-center gap-2 rounded-full border border-[#E8DFD5] bg-[#FAF8F5] px-2.5 py-1 text-xs text-[#2B1B2A] shadow-2xs">
                    {user.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.full_name || user.email}
                        className="h-5 w-5 rounded-full object-cover ring-1 ring-[#C85E45]/30"
                      />
                    ) : (
                      <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#FAF0EB] text-[#C85E45] font-serif font-bold text-2xs ring-1 ring-[#F0D5C9]">
                        {(user.full_name || user.email)[0].toUpperCase()}
                      </div>
                    )}
                    <span className="font-medium max-w-[120px] truncate text-[#2B1B2A]">
                      {user.full_name || user.email.split('@')[0]}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={handleLogout}
                    title="Sign Out"
                    className="inline-flex items-center gap-1.5 rounded-xl border border-transparent px-2.5 py-1.5 text-xs font-medium text-[#6A5868] hover:border-[#E8DFD5] hover:bg-[#F3ECE4] hover:text-[#C85E45] transition-all cursor-pointer"
                  >
                    <LogOut className="h-3.5 w-3.5 text-[#C85E45]" />
                    <span className="hidden md:inline">Sign Out</span>
                  </button>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#C85E45] to-[#B24D35] px-3.5 py-2 text-xs font-semibold text-white shadow-2xs hover:from-[#B8533B] hover:to-[#A3432C] transition-all cursor-pointer"
                >
                  <LogIn className="h-3.5 w-3.5" />
                  <span>Sign In</span>
                </Link>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex sm:hidden items-center gap-2">
            {isAuthenticated && user && (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#FAF0EB] text-[#C85E45] font-serif font-bold text-xs ring-1 ring-[#F0D5C9]">
                {(user.full_name || user.email)[0].toUpperCase()}
              </div>
            )}
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-[#E8DFD5] bg-[#F7F2EC] text-[#554553] hover:bg-[#ECE5DD] hover:text-[#2B1B2A] transition-colors cursor-pointer"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Navigation */}
        {mobileMenuOpen && (
          <div className="sm:hidden border-t border-[#EFE8DF] bg-[#FDFBF7]/98 px-4 pt-3 pb-4 backdrop-blur-xl animate-in slide-in-from-top-2 duration-200">
            {isAuthenticated && user && (
              <div className="mb-3 flex items-center gap-2.5 rounded-xl border border-[#EFE8DF] bg-[#FAF8F5] p-3 text-xs">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name || user.email}
                    className="h-8 w-8 rounded-full object-cover ring-1 ring-[#C85E45]/30"
                  />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#FAF0EB] text-[#C85E45] font-serif font-bold text-sm ring-1 ring-[#F0D5C9]">
                    {(user.full_name || user.email)[0].toUpperCase()}
                  </div>
                )}
                <div className="flex flex-col min-w-0">
                  <span className="font-semibold text-[#2B1B2A] truncate">
                    {user.full_name || user.email.split('@')[0]}
                  </span>
                  <span className="text-2xs text-[#7D6B8D] truncate">{user.email}</span>
                </div>
              </div>
            )}

            <nav className="flex flex-col gap-1.5" aria-label="Mobile Navigation">
              {navLinks.map(({ to, label, icon: Icon }) => {
                const isActive =
                  to === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(to);

                return (
                  <Link
                    key={to}
                    to={to}
                    onClick={() => handleLinkClick(to)}
                    className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                      isActive
                        ? 'border border-[#F0D5C9] bg-[#FAF3EE] text-[#C85E45] font-semibold'
                        : 'text-[#6A5868] hover:bg-[#F3ECE4] hover:text-[#2B1B2A]'
                    }`}
                  >
                    <Icon className="h-4 w-4 text-[#C85E45]" />
                    <span>{label}</span>
                  </Link>
                );
              })}

              <div className="mt-2 pt-2 border-t border-[#EFE8DF]">
                {isAuthenticated ? (
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-700 hover:bg-red-50/80 transition-colors cursor-pointer"
                  >
                    <LogOut className="h-4 w-4 text-red-600" />
                    <span>Sign Out</span>
                  </button>
                ) : (
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#C85E45] to-[#B24D35] px-4 py-3 text-sm font-semibold text-white shadow-2xs hover:from-[#B8533B] hover:to-[#A3432C] transition-all cursor-pointer"
                  >
                    <LogIn className="h-4 w-4" />
                    <span>Sign In</span>
                  </Link>
                )}
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex flex-col">{children}</main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#EFE8DF] bg-[#FAF7F2] py-6 text-center text-xs text-[#7A6C79] backdrop-blur-xs">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <div className="h-5 w-5 rounded-md bg-[#FAF0EB] flex items-center justify-center text-[#C85E45]">
              <Sparkles className="h-3 w-3" />
            </div>
            <span className="font-serif font-bold text-[#2B1B2A]">StorySpark AI</span>
            <span className="text-[#D6C7B9]">•</span>
            <span className="font-serif italic text-[#7D6B8D]">Where ideas become stories.</span>
          </div>

          <p className="text-[#7A6C79] text-xs font-serif italic">
            Created with imagination and AI.
          </p>
        </div>
      </footer>
    </div>
  );
};
