import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { questionsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { ArrowLeft, Building2, Search, Filter, Loader2, Target, CheckCircle2, ChevronRight, BarChart } from 'lucide-react';

export default function CompanyQuestions() {
  const router = useRouter();
  const { companyName } = router.query;
  const { isAuthenticated } = useAuthStore();
  
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('All');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }
    if (companyName) {
      fetchQuestions();
    }
  }, [companyName, isAuthenticated]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const res = await questionsApi.getByCompany(companyName as string);
      setQuestions(res.data.questions || []);
    } catch (e) {
      console.error('Failed to fetch company questions', e);
    } finally {
      setLoading(false);
    }
  };

  const filteredQuestions = questions.filter(q => {
    const matchesSearch = q.question_text.toLowerCase().includes(search.toLowerCase()) || 
                         (q.round_type && q.round_type.toLowerCase().includes(search.toLowerCase()));
    const matchesDiff = difficultyFilter === 'All' || q.difficulty === difficultyFilter;
    return matchesSearch && matchesDiff;
  });

  const getDifficultyColor = (diff: string) => {
    switch(diff) {
      case 'Easy': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'Medium': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'Hard': return 'bg-rose-50 text-rose-700 border-rose-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <>
      <Head>
        <title>{companyName} Interview Questions — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Header */}
          <div className="mb-8">
            <Link href="/questions/companies" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-6">
              <ArrowLeft className="w-4 h-4" /> Back to Companies
            </Link>
            
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div className="flex items-center gap-5">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 border-2 border-indigo-50 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <span className="text-3xl font-black text-indigo-700">{(companyName as string)?.charAt(0)}</span>
                </div>
                <div>
                  <h1 className="text-3xl font-heading font-extrabold text-slate-900 mb-2">
                    {companyName} <span className="text-slate-400 font-medium">Questions</span>
                  </h1>
                  <p className="text-slate-600 flex items-center gap-2">
                    <Target className="w-4 h-4" /> Practice exact questions asked in recent interviews.
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-center px-4">
                  <span className="block text-xl font-black text-slate-900">{questions.length}</span>
                  <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Total</span>
                </div>
                <div className="w-px h-10 bg-slate-200"></div>
                <div className="text-center px-4">
                  <span className="block text-xl font-black text-indigo-600">High</span>
                  <span className="text-xs font-semibold uppercase text-indigo-400 tracking-wider">Relevance</span>
                </div>
              </div>
            </div>
          </div>

          {/* Filtering & Search */}
          <div className="glass-card bg-white p-4 rounded-2xl border border-slate-200 shadow-sm mb-8 flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search by keyword or round (e.g., Array, HR)..."
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium"
              />
            </div>
            <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
              <Filter className="w-4 h-4 text-slate-400 hidden sm:block" />
              {['All', 'Easy', 'Medium', 'Hard'].map(d => (
                <button 
                  key={d}
                  onClick={() => setDifficultyFilter(d)}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all border
                    ${difficultyFilter === d 
                      ? 'bg-slate-900 text-white border-slate-900 shadow-md' 
                      : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Questions List */}
          {loading ? (
            <div className="py-24 flex flex-col items-center justify-center space-y-4">
              <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
              <p className="text-slate-500 font-medium">Loading {companyName} question bank...</p>
            </div>
          ) : filteredQuestions.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border border-slate-200 shadow-sm">
              <Building2 className="w-16 h-16 text-slate-200 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-slate-900 mb-2">No questions found</h3>
              <p className="text-slate-500">We don't have questions matching your criteria for {companyName} yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredQuestions.map(q => (
                <Link key={q.id} href={`/questions/${q.id}/practice`}
                  className="block group bg-white rounded-2xl border border-slate-200 p-5 hover:border-indigo-300 hover:shadow-lg transition-all duration-300 relative overflow-hidden">
                  
                  {/* Hover gradient effect */}
                  <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                  <div className="relative z-10">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2 leading-snug">
                        {q.question_text}
                      </h3>
                      <span className={`flex-shrink-0 px-3 py-1 rounded-lg text-xs font-bold border uppercase tracking-wide inline-flex items-center justify-center self-start ${getDifficultyColor(q.difficulty)}`}>
                        {q.difficulty}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-y-3 gap-x-6 text-sm text-slate-500">
                      <div className="flex items-center gap-1.5">
                        <BarChart className="w-4 h-4 text-slate-400" />
                        <span className="font-semibold text-slate-700">{q.round_type || 'General Round'}</span>
                      </div>
                      
                      <div className="flex items-center gap-1.5" title="Frequency Score (1-10)">
                        <span className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <svg key={i} className={`w-3.5 h-3.5 ${i < Math.ceil(q.frequency_score/2) ? 'text-amber-400' : 'text-slate-200'}`} fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                            </svg>
                          ))}
                        </span>
                        <span className="hidden sm:inline">Frequency</span>
                      </div>

                      {q.total_attempts > 0 && (
                        <div className="flex items-center gap-1.5 ml-auto sm:ml-0 font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded-md">
                          <CheckCircle2 className="w-4 h-4 text-indigo-500" />
                          {Math.round((q.correct_attempts / q.total_attempts) * 100)}% Pass Rate
                        </div>
                      )}
                      
                      <div className="sm:ml-auto flex items-center gap-1 text-indigo-600 font-bold group-hover:translate-x-1 transition-transform">
                        Practice <ChevronRight className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

        </div>
      </div>
    </>
  );
}
