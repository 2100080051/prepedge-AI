import { useEffect } from 'react';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

export default function Dashboard() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, router]);

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Welcome, {user.full_name || user.username}!</h1>

      <div className="grid md:grid-cols-3 gap-6">
        <a href="/flashlearn" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg">
          <div className="text-4xl mb-4">⚡</div>
          <h2 className="text-xl font-bold mb-2">FlashLearn</h2>
          <p className="text-gray-600">Practice with AI flashcards</p>
        </a>

        <a href="/resumeai" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg opacity-50">
          <div className="text-4xl mb-4">📄</div>
          <h2 className="text-xl font-bold mb-2">ResumeAI</h2>
          <p className="text-gray-600">Coming Soon - Week 2</p>
        </a>

        <a href="/mockmate" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg opacity-50">
          <div className="text-4xl mb-4">🎙️</div>
          <h2 className="text-xl font-bold mb-2">MockMate</h2>
          <p className="text-gray-600">Coming Soon - Week 3</p>
        </a>
      </div>

      <div className="mt-8 p-6 bg-blue-50 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Subscription Plan</h2>
        <p className="text-gray-700">
          Current: <strong>{user.subscription_plan.toUpperCase()}</strong>
        </p>
        <button className="mt-4 px-6 py-2 bg-primary text-white rounded hover:bg-blue-700">
          Upgrade to Pro
        </button>
      </div>
    </div>
  );
}
