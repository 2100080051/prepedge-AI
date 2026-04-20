import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { Brain, Loader2 } from 'lucide-react';

export default function GitHubCallback() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const { code, state } = router.query;

        if (!code) {
          setError('No authorization code received from GitHub');
          setLoading(false);
          return;
        }

        // Verify state to prevent CSRF attacks
        const savedState = localStorage.getItem('github_oauth_state');
        if (state !== savedState) {
          setError('Invalid state parameter. Security check failed.');
          localStorage.removeItem('github_oauth_state');
          setLoading(false);
          return;
        }

        localStorage.removeItem('github_oauth_state');

        // Exchange code for access token using our backend
        // Use the actual domain this callback is being accessed from
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.prepedgeai.in/api/v1';
        const exchangeUrl = `${backendUrl}/auth/github-exchange`;
        
        // Match the redirect_uri to exactly what is configured in GitHub API
        const redirect_uri = 'https://www.prepedgeai.in/auth/github/callback';
        
        console.log('GitHub callback exchange:', { exchangeUrl, redirect_uri });
        
        const response = await fetch(exchangeUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, redirect_uri }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to exchange code for access token');
        }

        const { access_token } = await response.json();

        // Now authenticate with our backend using the access token
        const authResponse = await authApi.githubLogin(access_token);
        localStorage.setItem('access_token', authResponse.data.access_token);

        try {
          const userRes = await authApi.getCurrentUser();
          login(userRes.data, authResponse.data.access_token);
        } catch (e) {
          login(
            {
              id: authResponse.data.user_id,
              email: '',
              username: authResponse.data.user_name,
              full_name: '',
              subscription_plan: 'free',
            },
            authResponse.data.access_token
          );
        }

        router.push('/dashboard');
      } catch (err: any) {
        console.error('GitHub callback error:', err);
        setError(err.message || 'GitHub login failed. Please try again.');
        setLoading(false);
      }
    };

    if (router.isReady) {
      handleCallback();
    }
  }, [router.isReady, router.query, login]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-4">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-xl">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
          <p className="text-slate-600 font-medium">Completing your GitHub sign-in...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white px-4">
        <div className="flex flex-col items-center gap-4 max-w-md">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-xl">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-2xl font-heading font-bold text-slate-900">Sign-in Failed</h1>
            <p className="text-slate-600 mt-2">{error}</p>
          </div>
          <a
            href="/auth/register"
            className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Try Again
          </a>
        </div>
      </div>
    );
  }

  return null;
}
