import Link from 'next/link';
import { useRouter } from 'next/router';
import { Brain, LogIn, Menu, X, LogOut, Trophy, Shield, ChevronDown, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth';

const NAV_LINKS = [
  { name: 'LearnAI',    href: '/learnai' },
  { name: 'FlashLearn', href: '/flashlearn' },
  { name: 'ResumeAI',   href: '/resumeai' },
  { name: 'MockMate',   href: '/mockmate' },
  { name: 'TESS',       href: '/tess' },
  { name: 'Questions',  href: '/questions' },
];

export default function Navbar() {
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { user, logout, isAuthenticated } = useAuthStore();

  // Scroll listener for elevated shadow
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [router.pathname]);

  const isActive = (href: string) =>
    router.pathname === href || (href !== '/' && router.pathname.startsWith(href));

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-white/90 backdrop-blur-xl shadow-navbar border-b border-slate-100/80'
            : 'bg-white/70 backdrop-blur-md border-b border-slate-100/50'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">

            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group flex-shrink-0">
              <div className="relative">
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-xl shadow-sm group-hover:shadow-glow-sm transition-all duration-300">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-white animate-ping-slow opacity-75" />
              </div>
              <div className="flex flex-col leading-none">
                <span className="font-heading font-extrabold text-lg tracking-tight text-slate-900">
                  PrepEdge
                </span>
                <span className="text-[10px] font-semibold text-indigo-600 tracking-widest uppercase -mt-0.5">
                  AI Platform
                </span>
              </div>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-1">
              {NAV_LINKS.map(link => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`relative px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive(link.href)
                      ? 'text-indigo-600 bg-indigo-50'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  {link.name}
                  {isActive(link.href) && (
                    <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-indigo-600 rounded-full" />
                  )}
                </Link>
              ))}

              {/* Leaderboard — highlighted */}
              <Link href="/leaderboard"
                className={`relative flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive('/leaderboard')
                    ? 'text-amber-600 bg-amber-50'
                    : 'text-slate-600 hover:text-amber-600 hover:bg-amber-50'
                }`}>
                <Trophy className="w-3.5 h-3.5" />
                Board
              </Link>
            </nav>

            {/* Desktop Auth */}
            <div className="hidden md:flex items-center gap-3">
              {isAuthenticated && user ? (
                <>
                  {/* Study Plan chip */}
                  <Link href="/prep/study-plan"
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg border border-indigo-100 transition-all">
                    <Sparkles className="w-3 h-3" /> Study Plan
                  </Link>

                  {/* Admin badge */}
                  {user.is_admin && (
                    <Link href="/admin"
                      className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg border border-purple-100 transition-all">
                      <Shield className="w-3 h-3" /> Admin
                    </Link>
                  )}

                  {/* User pill + logout */}
                  <div className="flex items-center gap-2 pl-3 border-l border-slate-200">
                    <Link href="/profile" className="flex items-center gap-2 hover:bg-slate-50 p-1.5 rounded-xl transition-colors">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm">
                        {(user.full_name || user.username || 'U')[0].toUpperCase()}
                      </div>
                      <div className="flex flex-col leading-none">
                        <span className="text-sm font-semibold text-slate-800 truncate max-w-[100px]">
                          {user.full_name?.split(' ')[0] || user.username}
                        </span>
                        <span className="text-[10px] text-slate-400 capitalize">{user.subscription_plan || 'free'}</span>
                      </div>
                    </Link>
                    <button
                      onClick={handleLogout}
                      title="Logout"
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all ml-1">
                      <LogOut className="w-4 h-4" />
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link href="/auth/login"
                    className="text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-100 transition-all">
                    Sign in
                  </Link>
                  <Link href="/auth/register"
                    className="btn-primary text-sm px-4 py-2 rounded-xl shadow-sm">
                    Get Started Free →
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Hamburger */}
            <button
              className="md:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <div className="relative w-5 h-5">
                <Menu className={`absolute inset-0 transition-all duration-300 ${isMobileMenuOpen ? 'opacity-0 rotate-90' : 'opacity-100 rotate-0'}`} />
                <X className={`absolute inset-0 transition-all duration-300 ${isMobileMenuOpen ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'}`} />
              </div>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      <div
        className={`fixed inset-0 z-40 md:hidden transition-all duration-300 ${
          isMobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)} />

        {/* Slide-in panel */}
        <div className={`absolute top-16 left-0 right-0 bg-white/95 backdrop-blur-xl border-b border-slate-200 shadow-xl transition-all duration-300 ${
          isMobileMenuOpen ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
        }`}>
          <div className="px-4 py-4 space-y-1">
            {NAV_LINKS.map(link => (
              <Link key={link.href} href={link.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive(link.href)
                    ? 'text-indigo-600 bg-indigo-50 font-semibold'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}>
                {link.name}
              </Link>
            ))}
            <Link href="/leaderboard"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-100 transition-all">
              <Trophy className="w-4 h-4 text-amber-500" />Leaderboard
            </Link>
            <Link href="/prep/study-plan"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-100 transition-all">
              <Sparkles className="w-4 h-4 text-indigo-500" />Study Plan
            </Link>
          </div>

          <div className="border-t border-slate-100 px-4 py-4">
            {isAuthenticated && user ? (
              <div className="space-y-2">
                <div className="flex items-center gap-3 px-4 py-3 bg-slate-50 rounded-xl">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                    {(user.full_name || user.username || 'U')[0].toUpperCase()}
                  </div>
                  <div>
                    <div className="font-semibold text-slate-900 text-sm">{user.full_name || user.username}</div>
                    <div className="text-xs text-slate-400 capitalize">{user.subscription_plan || 'free'} plan</div>
                  </div>
                </div>
                <button onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-xl transition-all font-medium">
                  <LogOut className="w-4 h-4" />Sign out
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Link href="/auth/login" className="block btn-secondary w-full text-center text-sm py-2.5">Sign in</Link>
                <Link href="/auth/register" className="block btn-primary w-full text-center text-sm py-2.5">Get Started Free</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
