import { useState } from 'react';
import Head from 'next/head';
import { MapPin, Calendar, Target, Loader2, BrainCircuit, CheckSquare, Square, ChevronRight, AlertCircle, Sparkles, Flag, Clock } from 'lucide-react';
import { questionsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

const COMPANIES = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Cognizant', 'Amazon', 'Google', 'Microsoft', 'Flipkart', 'Zoho'];
const ROLES = ['Software Engineer', 'Data Analyst', 'Business Analyst', 'System Analyst', 'Full Stack Developer', 'DevOps Engineer', 'QA Engineer', 'Product Manager'];
const WEAK_AREAS_OPTIONS = ['Data Structures', 'Algorithms', 'SQL', 'OOPs', 'System Design', 'Aptitude', 'HR Questions', 'Networking', 'OS Concepts', 'Communication'];

interface StudyItem {
  question: string;
  difficulty: string;
  topic: string;
  completed: boolean;
}
interface StudyPhase {
  phase: string;
  description: string;
  days: string;
  items: StudyItem[];
}

export default function StudyPlan() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  const [form, setForm] = useState({ target_company: '', target_role: '', days_until_interview: '14' });
  const [weakAreas, setWeakAreas] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);
  const [error, setError] = useState('');
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const toggleWeak = (area: string) =>
    setWeakAreas(prev => prev.includes(area) ? prev.filter(a => a !== area) : [...prev, area]);

  const toggleCheck = (key: string) =>
    setChecked(prev => ({ ...prev, [key]: !prev[key] }));

  const handleGenerate = async () => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    if (!form.target_company || !form.target_role) { setError('Please fill Company and Role.'); return; }
    setLoading(true); setError(''); setPlan(null);
    try {
      const res = await questionsApi.generateStudyPlan({
        target_company: form.target_company,
        target_role: form.target_role,
        days_until_interview: parseInt(form.days_until_interview),
        weak_areas: weakAreas,
      });
      setPlan(res.data);
      setChecked({});
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to generate plan. The study plan API may not be ready yet.');
    } finally { setLoading(false); }
  };

  const allItems = plan?.phases?.flatMap((p: StudyPhase, pi: number) => p.items?.map((_: any, ii: number) => `${pi}-${ii}`)) || [];
  const completedCount = Object.values(checked).filter(Boolean).length;
  const totalCount = allItems.length;
  const progressPct = totalCount ? Math.round((completedCount / totalCount) * 100) : 0;

  const DIFF_COLOR: Record<string, string> = { Easy: 'text-emerald-600', Medium: 'text-amber-600', Hard: 'text-rose-600' };

  return (
    <>
      <Head>
        <title>Study Plan Generator — PrepEdge AI</title>
        <meta name="description" content="Get an AI-generated personalized study plan for your target company interview. Phase-by-phase preparation guide." />
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-indigo-200 mb-6">
              <BrainCircuit className="w-5 h-5 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-900">AI-Powered Preparation</span>
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Your Personalized <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Study Plan</span>
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">Tell us your target company, role, and available days. Our AI will create a structured day-by-day preparation plan.</p>
          </div>

          {/* Plan Generator Form */}
          <div className="glass-card p-8 rounded-3xl border border-slate-200 shadow-sm mb-8">
            <div className="grid sm:grid-cols-3 gap-5 mb-6">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1"><Target className="w-3 h-3" />Target Company</label>
                <select value={form.target_company} onChange={e => setForm(p => ({ ...p, target_company: e.target.value }))}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-800 bg-white">
                  <option value="">Select Company...</option>
                  {COMPANIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1"><Flag className="w-3 h-3" />Target Role</label>
                <select value={form.target_role} onChange={e => setForm(p => ({ ...p, target_role: e.target.value }))}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-800 bg-white">
                  <option value="">Select Role...</option>
                  {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1"><Clock className="w-3 h-3" />Days Until Interview</label>
                <input type="number" min="3" max="90" value={form.days_until_interview}
                  onChange={e => setForm(p => ({ ...p, days_until_interview: e.target.value }))}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Weak Areas (optional — helps tailor your plan)</label>
              <div className="flex flex-wrap gap-2">
                {WEAK_AREAS_OPTIONS.map(area => (
                  <button key={area} onClick={() => toggleWeak(area)}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold border transition-all ${weakAreas.includes(area) ? 'bg-indigo-600 text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'}`}>
                    {area}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <div className="mb-5 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />{error}
              </div>
            )}

            <button onClick={handleGenerate} disabled={loading || !form.target_company || !form.target_role}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl disabled:opacity-40 hover:shadow-glow transition-all flex items-center justify-center gap-2 text-base">
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Generating Your Plan...</> : <><Sparkles className="w-5 h-5" />Generate Study Plan</>}
            </button>
          </div>

          {/* Generated Plan */}
          {plan && (
            <div className="space-y-6 animate-fade-in">
              {/* Plan Header */}
              <div className="glass-card p-6 rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50 to-purple-50">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-extrabold text-slate-900">{plan.title || `${form.target_company} ${form.target_role} Plan`}</h2>
                    <p className="text-slate-600 mt-1 text-sm">{form.days_until_interview} days • {totalCount} questions • {plan.phases?.length} phases</p>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-extrabold text-indigo-600">{progressPct}%</div>
                    <div className="text-xs text-slate-500">{completedCount}/{totalCount} done</div>
                  </div>
                </div>
                <div className="mt-4 h-3 bg-white/60 rounded-full overflow-hidden border border-indigo-100">
                  <div className="h-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                    style={{ width: `${progressPct}%` }} />
                </div>
              </div>

              {/* Phases */}
              {plan.phases?.map((phase: StudyPhase, pi: number) => (
                <div key={pi} className="glass-card rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm">
                  <div className="p-5 border-b border-slate-50 bg-gradient-to-r from-slate-50 to-white flex items-start gap-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl flex items-center justify-center font-extrabold text-lg flex-shrink-0">
                      {pi + 1}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900 text-lg">{phase.phase}</h3>
                      <p className="text-slate-500 text-sm">{phase.description}</p>
                      {phase.days && <span className="mt-1 inline-flex items-center gap-1 text-xs text-indigo-600 font-semibold"><Calendar className="w-3 h-3" />{phase.days}</span>}
                    </div>
                  </div>
                  <div className="divide-y divide-slate-50">
                    {phase.items?.map((item: StudyItem, ii: number) => {
                      const key = `${pi}-${ii}`;
                      const done = checked[key];
                      return (
                        <div key={ii} className={`flex items-center gap-4 px-5 py-3 hover:bg-slate-50 transition-colors ${done ? 'opacity-60' : ''}`}>
                          <button onClick={() => toggleCheck(key)} className="flex-shrink-0 text-indigo-500 hover:text-indigo-700 transition-colors">
                            {done ? <CheckSquare className="w-5 h-5" /> : <Square className="w-5 h-5 text-slate-300" />}
                          </button>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium text-slate-800 ${done ? 'line-through' : ''}`}>{item.question}</p>
                            {item.topic && <span className="text-xs text-slate-400">{item.topic}</span>}
                          </div>
                          <span className={`text-xs font-bold flex-shrink-0 ${DIFF_COLOR[item.difficulty] || 'text-slate-500'}`}>{item.difficulty}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}

              <div className="text-center pt-4">
                <a href="/questions" className="inline-flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors">
                  Start Next Question <ChevronRight className="w-5 h-5" />
                </a>
              </div>
            </div>
          )}

          {!plan && !loading && (
            <div className="text-center py-16 border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
              <BrainCircuit className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-500">Your study plan will appear here</h3>
              <p className="text-slate-400 mt-2">Fill in your details above and click Generate.</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
