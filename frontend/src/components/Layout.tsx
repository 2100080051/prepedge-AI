import React, { useEffect } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { useAuthStore } from '@/store/auth';
import { authApi } from '@/lib/api';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { token, user, setUser, logout } = useAuthStore();

  useEffect(() => {
    if (token && !user) {
      // If we have a token in local storage but no user loaded, fetch it
      authApi.getCurrentUser()
        .then((res) => {
          setUser(res.data);
        })
        .catch(() => {
          logout();
        });
    }
  }, [token, user, setUser, logout]);

  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900 bg-slate-50 overflow-x-hidden selection:bg-indigo-500 selection:text-white">
      <Navbar />
      <main className="flex-grow pt-16">
        {children}
      </main>
      <Footer />
    </div>
  );
}
