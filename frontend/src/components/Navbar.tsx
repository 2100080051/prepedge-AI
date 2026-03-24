import Link from 'next/link';
import { useRouter } from 'next/router';
import { Brain, LogIn, Menu, X, LogOut } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '@/store/auth';

export default function Navbar() {
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuthStore();

  const isActive = (path: string) => router.pathname === path;

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const navLinks = [
    { name: 'LearnAI', href: '/learnai' },
    { name: 'FlashLearn', href: '/flashlearn' },
    { name: 'ResumeAI', href: '/resumeai' },
    { name: 'MockMate', href: '/mockmate' },
  ];

  return (
    <nav className="fixed w-full z-50 glass border-b border-gray-200/50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-xl group-hover:scale-105 transition-transform duration-300 shadow-glow">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="font-heading font-bold text-xl tracking-tight text-slate-800">
              PrepEdge <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">AI</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                className={`font-medium transition-colors hover:text-indigo-600 ${
                  isActive(link.href) ? 'text-indigo-600' : 'text-slate-600'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="flex items-center space-x-4">
                <span className="text-slate-600 font-medium">{user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-slate-600 hover:text-indigo-600 font-medium transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <>
                <Link href="/auth/login" className="text-slate-600 hover:text-indigo-600 font-medium transition-colors">
                  Log in
                </Link>
                <Link
                  href="/auth/register"
                  className="px-5 py-2.5 rounded-full font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 hover:shadow-glow transition-all duration-300 transform hover:-translate-y-0.5"
                >
                  Sign Up Free
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-slate-600 hover:text-indigo-600 focus:outline-none"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-xl border-b border-gray-200">
          <div className="px-4 pt-2 pb-6 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                className={`block px-3 py-2 rounded-lg text-base font-medium ${
                  isActive(link.href)
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-slate-700 hover:bg-slate-50 hover:text-indigo-600'
                }`}
              >
                {link.name}
              </Link>
            ))}
            {isAuthenticated && user ? (
              <div className="pt-4 flex flex-col gap-3 border-t border-slate-200">
                <div className="px-3 py-2">
                  <p className="text-sm text-slate-600">Signed in as</p>
                  <p className="font-medium text-slate-800">{user.full_name}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="pt-4 flex flex-col gap-3">
                <Link
                  href="/auth/login"
                  className="w-full border border-slate-200 text-center px-4 py-2.5 rounded-lg font-medium text-slate-700 hover:bg-slate-50"
                >
                  Log in
                </Link>
                <Link
                  href="/auth/register"
                  className="w-full text-center px-4 py-2.5 rounded-lg font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600"
                >
                  Sign Up Free
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
