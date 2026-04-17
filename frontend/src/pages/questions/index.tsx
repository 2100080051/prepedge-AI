import { useState } from 'react';
import Head from 'next/head';
import { Search, SlidersHorizontal, BookOpen, Building2, Loader2, AlertCircle, ChevronDown, Zap, Code2, Users, BrainCircuit } from 'lucide-react';
import { questionsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';
import Link from 'next/link';

const COMPANIES = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Cognizant', 'Amazon', 'Google', 'Microsoft', 'Flipkart', 'Zoho'];
const ROUNDS = ['All', 'Online Test', 'Technical Round', 'HR Round'];
const DIFFICULTIES = ['All', 'Easy', 'Medium', 'Hard'];

const DIFF_BADGE: Record<string, string> = {
  Easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Hard:   'bg-rose-100 text-rose-700 border-rose-200',
};

const ROUND_ICON: Record<string, any> = {
  'Online Test': <Zap className="w-4 h-4" />,
  'Technical Round': <Code2 className="w-4 h-4" />,
  'HR Round': <Users className="w-4 h-4" />,
};

const COMPANY_COLORS: Record<string, string> = {
  TCS: 'from-blue-600 to-blue-800', Infosys: 'from-indigo-600 to-indigo-800',
  Wipro: 'from-purple-600 to-purple-800', Accenture: 'from-cyan-600 to-cyan-800',
  Cognizant: 'from-teal-600 to-teal-800', Amazon: 'from-orange-500 to-amber-600',
  Google: 'from-red-500 to-rose-600', Microsoft: 'from-sky-500 to-blue-600',
  Flipkart: 'from-yellow-500 to-orange-500', Zoho: 'from-green-600 to-emerald-700',
};

interface Question {
  id: number;
  question: string;
  company: string;
  round_type: string;
  difficulty: string;
  frequency_score: number;
  topic: string;
}

export default function QuestionBank() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedRound, setSelectedRound] = useState('All');
  const [selectedDiff, setSelectedDiff] = useState('All');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    if (!selectedCompany) { setError('Please select a company.'); return; }
    setLoading(true);
    setError('');
    setSearched(true);
    try {
      const res = await questionsApi.getByCompany(
        selectedCompany,
        selectedRound !== 'All' ? selectedRound : undefined,
        selectedDiff !== 'All' ? selectedDiff : undefined,
      );
      // Backend returns {success, questions, count, total} — extract the array
      const data = res.data;
      setQuestions(Array.isArray(data) ? data : (data?.questions || []));
    } catch (e: any) {
      const detail = e.response?.data?.detail;
      setError(detail || 'Failed to load questions. Please ensure the backend question service is running.');
      setQuestions([]);
    } finally {
      setLoading(false);
    }
  };

  const FreqDots = ({ score }: { score: number }) => (
    <div className="flex gap-0.5 items-center">
      {Array.from({ length: 10 }).map((_, i) => (
        <div key={i} className={`w-1.5 h-4 rounded-full ${i < score ? 'bg-indigo-500' : 'bg-slate-100'}`} />
      ))}
      <span className="ml-1.5 text-xs text-slate-500">{score}/10</span>
    </div>
  );

  return (
    <>
      <Head>
        <title>Question Bank — PrepEdge AI</title>
        <meta name="description" content="Practice real interview questions from TCS, Infosys, Google and more. Curated by company, round and difficulty." />
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Hero */}
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-indigo-200 mb-6">
              <BrainCircuit className="w-5 h-5 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-900">Real Interview Questions, Verified by Community</span>
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Company Question <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Bank</span>
            </h1>
            <p className="text-lg text-slate-600">Practice with real questions from top companies. Curated by round and difficulty to match how companies actually interview.</p>
          </div>

          {/* Company Grid */}
          <div className="glass-card p-8 rounded-3xl border border-slate-200 shadow-sm mb-6">
            <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2">
              <Building2 className="w-4 h-4" /> Choose Company
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-8">
              {COMPANIES.map(co => (
                <button key={co} onClick={() => setSelectedCompany(co)}
                  className={`py-3 px-2 rounded-xl font-semibold text-sm border-2 transition-all duration-200 ${
                    selectedCompany === co
                      ? `bg-gradient-to-br ${COMPANY_COLORS[co] || 'from-indigo-600 to-purple-600'} text-white border-transparent shadow-lg scale-105`
                      : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                  }`}>{co}</button>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mb-5">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1"><SlidersHorizontal className="w-3 h-3" />Round</label>
                <div className="flex gap-2 flex-wrap">
                  {ROUNDS.map(r => (
                    <button key={r} onClick={() => setSelectedRound(r)}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold border transition-all ${selectedRound === r ? 'bg-indigo-600 text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'}`}>{r}</button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Difficulty</label>
                <div className="flex gap-2">
                  {DIFFICULTIES.map(d => (
                    <button key={d} onClick={() => setSelectedDiff(d)}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold border transition-all ${selectedDiff === d ? 'bg-indigo-600 text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'}`}>{d}</button>
                  ))}
                </div>
              </div>
            </div>

            {error && !loading && (
              <div className="mb-4 p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />{error}
              </div>
            )}

            <button onClick={handleSearch} disabled={!selectedCompany || loading}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl disabled:opacity-40 hover:shadow-glow transition-all flex items-center justify-center gap-2 text-base">
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Loading Questions...</> : <><Search className="w-5 h-5" />Find Questions</>}
            </button>
          </div>

          {/* Questions List */}
          {searched && !loading && (
            <div className="space-y-3">
              {questions.length === 0 ? (
                <div className="text-center py-16 glass-card rounded-2xl border border-slate-200">
                  <BookOpen className="w-16 h-16 text-slate-200 mx-auto mb-4" />
                  <h3 className="text-xl font-medium text-slate-500">No questions found</h3>
                  <p className="text-slate-400 mt-2">Try a different company, round, or difficulty — or the question bank may still be loading data.</p>
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-bold text-slate-900">{questions.length} Questions found for {selectedCompany}</h2>
                  </div>
                  {questions.map(q => (
                    <div key={q.id} className="glass-card p-5 rounded-2xl border border-slate-200 bg-white hover:border-indigo-200 hover:shadow-sm transition-all flex flex-col sm:flex-row sm:items-center gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-slate-900 font-medium leading-relaxed line-clamp-2 mb-3">{q.question}</p>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`px-2.5 py-1 rounded-lg text-xs border font-semibold ${DIFF_BADGE[q.difficulty] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>{q.difficulty}</span>
                          <span className="flex items-center gap-1 px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium border border-slate-200">
                            {ROUND_ICON[q.round_type] || <BookOpen className="w-4 h-4" />}{q.round_type}
                          </span>
                          {q.topic && <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-xs font-medium border border-indigo-100">{q.topic}</span>}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-3 flex-shrink-0">
                        <div className="hidden md:block"><FreqDots score={q.frequency_score || 0} /></div>
                        <Link href={`/questions/${q.id}/practice`}
                          className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold rounded-xl hover:shadow-glow transition-all">
                          Practice →
                        </Link>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}

          {!searched && (
            <div className="text-center py-16 border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
              <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-500">Select a company to see questions</h3>
              <p className="text-slate-400 mt-2">Questions are curated from Glassdoor, Reddit, and our community.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
