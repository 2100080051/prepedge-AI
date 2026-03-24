import { useState } from 'react';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { Brain, Loader2 } from 'lucide-react';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { login } = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authApi.register(formData);
      // Wait for token to be stored
      localStorage.setItem('access_token', response.data.access_token);
      
      try {
        // Immediately fetch user
        const userRes = await authApi.getCurrentUser();
        login(userRes.data, response.data.access_token);
        router.push('/dashboard');
      } catch (e) {
        // Fallback if fetch fails
        login({ id: 0, email: formData.email, username: formData.username, full_name: formData.full_name, subscription_plan: 'free' }, response.data.access_token);
        router.push('/dashboard');
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different email/username.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-row-reverse">
      {/* Right side Form */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 bg-white relative">
        <div className="absolute top-8 right-8 lg:left-auto lg:right-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-xl">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="font-heading font-bold text-xl tracking-tight text-slate-800">
               PrepEdge AI
            </span>
          </Link>
        </div>

        <div className="mx-auto w-full max-w-sm lg:w-[28rem]">
          <div className="mb-8 text-center sm:text-left pt-8 lg:pt-0">
            <h2 className="text-3xl font-heading font-extrabold text-slate-900 tracking-tight">
              Create an account
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Start your journey to crack top product companies.
            </p>
          </div>

          <div className="mt-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-100 text-sm text-red-600 flex items-start">
                  <span className="block sm:inline">{error}</span>
                </div>
              )}

              <div className="grid grid-cols-1 gap-y-5 gap-x-4 sm:grid-cols-2">
                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Full Name</label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Username</label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                    placeholder="johndoe_99"
                    required
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Email address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                    placeholder="john@example.com"
                    required
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Password</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-glow"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create Account'}
              </button>
            </form>

            <div className="mt-8 text-center text-sm">
              <span className="text-slate-600">Already have an account? </span>
              <Link href="/auth/login" className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors">
                Log in instead
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Left side Gradient Background */}
      <div className="hidden lg:flex flex-1 relative bg-slate-50 items-center justify-center p-12 overflow-hidden border-r border-slate-200">
        <div className="absolute inset-0 bg-white" />
        
        {/* Soft Decorative Background */}
        <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-indigo-100 via-transparent to-transparent opacity-80" />
        <div className="absolute bottom-0 left-0 w-full h-full bg-[radial-gradient(circle_at_bottom_left,_var(--tw-gradient-stops))] from-pink-100 via-transparent to-transparent opacity-80" />

        <div className="relative z-10 w-full max-w-lg">
           <div className="glass-card p-10 rounded-3xl">
             <div className="mb-6 flex gap-2">
               {[1,2,3,4,5].map(i => (
                 <svg key={i} className="w-5 h-5 text-yellow-500 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
               ))}
             </div>
             <p className="text-xl text-slate-700 font-medium mb-8 leading-relaxed">
               "PrepEdge AI completely changed how I prepare. The MockMate feature felt just like the real TCS interview."
             </p>
             <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xl shadow-md">
                  R
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Rahul Sharma</p>
                  <p className="text-sm text-slate-500">Placed at TCS Digital</p>
                </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}
