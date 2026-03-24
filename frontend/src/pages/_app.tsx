import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import Layout from '../components/Layout';
import '../styles/globals.css';
import { useAuthStore } from '@/store/auth';

export default function App({ Component, pageProps }: AppProps) {
  const loadAuthFromStorage = useAuthStore((state) => state.loadAuthFromStorage);

  useEffect(() => {
    // Load auth state from localStorage on app mount
    loadAuthFromStorage();
  }, [loadAuthFromStorage]);

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}
