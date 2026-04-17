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
    phone_number: '',
    college: '',
    graduation_year: new Date().getFullYear() + 4,
    course: '',
    years_of_experience: 0,
  });
  
  const calculateStrength = (pass: string) => {
    let score = 0;
    if (!pass) return 0;
    if (pass.length > 7) score += 1;
    if (/[A-Z]/.test(pass)) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;
    return score;
  };
  
  const strength = calculateStrength(formData.password);
  const strengthColors = ['bg-slate-200', 'bg-red-500', 'bg-amber-500', 'bg-indigo-500', 'bg-emerald-500'];
  const strengthLabels = ['Too weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { login } = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    // Convert years_of_experience to number
    if (name === 'years_of_experience' || name === 'graduation_year') {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value, 10) }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
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

          {/* Social Login Buttons */}
          <div className="mt-6 grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              onClick={() => {
                alert('Google OAuth would connect here - configure Google OAuth in backend');
              }}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors font-medium text-sm text-slate-700 shadow-sm"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </button>
            <button
              type="button"
              onClick={() => {
                alert('GitHub OAuth would connect here - configure GitHub OAuth in backend');
              }}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors font-medium text-sm text-slate-700 shadow-sm"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.49.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.603-3.369-1.343-3.369-1.343-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.544 2.914 1.181.092-.916.35-1.544.636-1.9-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482C19.138 20.195 22 16.44 22 12.017 22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
              </svg>
              GitHub
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-slate-500 font-medium">Or continue with email</span>
            </div>
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
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm mb-2"
                    placeholder="••••••••"
                    required
                  />
                  {formData.password && (
                    <div className="w-full">
                      <div className="flex gap-1 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden mb-1.5">
                        {[1, 2, 3, 4].map(idx => (
                          <div 
                            key={idx} 
                            className={`h-full flex-1 transition-colors duration-300 ${strength >= idx ? strengthColors[strength] : 'bg-transparent'}`}
                          />
                        ))}
                      </div>
                      <p className={`text-xs font-semibold ${strength >= 3 ? 'text-emerald-600' : 'text-slate-500'}`}>
                        {strengthLabels[strength]}
                      </p>
                    </div>
                  )}
                </div>

                {/* NEW FIELDS */}
                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Phone Number (Optional)</label>
                  <input
                    type="tel"
                    name="phone_number"
                    placeholder="+91 98765 43210"
                    value={formData.phone_number}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">College/University (Optional)</label>
                  <input
                    type="text"
                    name="college"
                    placeholder="IIT Delhi, Stanford, etc."
                    value={formData.college}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Graduation Year (Optional)</label>
                  <select
                    name="graduation_year"
                    value={formData.graduation_year}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                  >
                    {[2024, 2025, 2026, 2027, 2028, 2029, 2030].map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Course/Major (Optional)</label>
                  <input
                    type="text"
                    name="course"
                    placeholder="B.Tech Computer Science, B.E. Electronics, etc."
                    value={formData.course}
                    onChange={handleChange}
                    className="appearance-none block w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="block text-sm font-medium text-slate-700">Years of Experience (Optional)</label>
                  <div className="flex items-center gap-4">
                    <select
                      name="years_of_experience"
                      value={formData.years_of_experience}
                      onChange={handleChange}
                      className="appearance-none w-full px-4 py-3 border border-slate-200 rounded-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
                    >
                      <option value={0}>Fresher (0 years)</option>
                      {Array.from({length: 30}, (_, i) => i + 1).map(year => (
                        <option key={year} value={year}>{year} {year === 1 ? 'year' : 'years'}</option>
                      ))}
                    </select>
                    <span className="text-sm text-slate-500 whitespace-nowrap font-medium">
                      {formData.years_of_experience === 0 ? '👶 Fresher' : formData.years_of_experience < 3 ? '📚 Junior' : formData.years_of_experience < 7 ? '⭐ Senior' : '👑 Lead'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">This helps us recommend the right jobs for you</p>
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
