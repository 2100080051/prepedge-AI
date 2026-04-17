import type { AppProps } from 'next/app';
import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import '../styles/globals.css';
import { useAuthStore } from '@/store/auth';

export default function App({ Component, pageProps }: AppProps) {
  const loadAuthFromStorage = useAuthStore((state) => state.loadAuthFromStorage);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Load auth state from localStorage on app mount
    loadAuthFromStorage();
    
    // Load dark mode preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (savedTheme === null && prefersDark);
    
    setIsDark(shouldBeDark);
    if (shouldBeDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [loadAuthFromStorage]);

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}
