import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Shield, Loader2, RefreshCw, Search, SlidersHorizontal, CheckCircle2, XCircle, Edit3, ChevronDown, ChevronUp, BookOpen, AlertCircle } from 'lucide-react';
import { adminApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

const DIFF_BADGE: Record<string, string> = {
  Easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Hard:   'bg-rose-100 text-rose-700 border-rose-200',
};

export default function AdminQuestionsPage() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [companyFilter, setCompanyFilter] = useState('');
  const [actionId, setActionId] = useState<number | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [editData, setEditData] = useState<any>({});
  const [toast, setToast] = useState('');
  const [stats, setStats] = useState({ total: 0, pending: 0, verified: 0 });

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    loadData();
  }, [isAuthenticated]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getPendingQuestions();
      const data = res.data || [];
      setQuestions(data);
      setStats({ total: data.length, pending: data.filter((q: any) => q.status === 'pending').length, verified: data.filter((q: any) => q.status === 'verified').length });
    } catch (e: any) {
      showToast(e.response?.data?.detail || 'Failed to load questions.');
    } finally { setLoading(false); }
  };

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(''), 3500); };

  const handleVerify = async (id: number) => {
    setActionId(id);
    try {
      const data = editing === id ? editData : undefined;
      await adminApi.verifyQuestion(id, data);
      setQuestions(prev => prev.map(q => q.id === id ? { ...q, status: 'verified' } : q));
      setEditing(null);
      showToast('✅ Question verified!');
    } catch (e: any) { showToast(e.response?.data?.detail || 'Verification failed.'); }
    finally { setActionId(null); }
  };

  const handleReject = async (id: number) => {
    setActionId(id);
    try {
      await adminApi.rejectQuestion(id);
      setQuestions(prev => prev.map(q => q.id === id ? { ...q, status: 'rejected' } : q));
      showToast('Question rejected.');
    } catch (e: any) { showToast(e.response?.data?.detail || 'Rejection failed.'); }
    finally { setActionId(null); }
  };

  const handleSaveEdit = async (id: number) => {
    try {
      await adminApi.updateQuestion(id, editData);
      setQuestions(prev => prev.map(q => q.id === id ? { ...q, ...editData } : q));
      setEditing(null);
      showToast('Edits saved.');
    } catch (e: any) { showToast(e.response?.data?.detail || 'Save failed.'); }
  };

  const filtered = questions.filter(q => {
    const s = search.toLowerCase();
    const matchSearch = !s || q.question?.toLowerCase().includes(s) || q.company?.toLowerCase().includes(s);
    const matchCompany = !companyFilter || q.company === companyFilter;
    return matchSearch && matchCompany;
  });

  const companies = Array.from(new Set(questions.map((q: any) => q.company).filter(Boolean)));

  return (
    <>
      <Head><title>Admin — Question Verification | PrepEdge AI</title></Head>
      {toast && (<div className="fixed top-6 right-6 z-[200] px-6 py-3 bg-slate-900 text-white rounded-xl shadow-2xl font-medium text-sm">{toast}</div>)}

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="flex items-center justify-between mb-8">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-purple-600 p-2 rounded-xl"><Shield className="w-5 h-5 text-white" /></div>
                <h1 className="text-2xl font-heading font-extrabold text-slate-900">Question Verification</h1>
              </div>
              <p className="text-slate-500 text-sm">Review, edit, and verify community-submitted questions</p>
            </div>
            <button onClick={loadData} className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-100 text-sm font-medium">
              <RefreshCw className="w-4 h-4" />Refresh
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[{ label: 'Total', val: stats.total, c: 'text-slate-900' }, { label: 'Pending', val: stats.pending, c: 'text-amber-600' }, { label: 'Verified', val: stats.verified, c: 'text-emerald-600' }].map(s => (
              <div key={s.label} className="glass-card p-5 rounded-2xl border border-slate-200 bg-white text-center">
                <div className={`text-2xl font-extrabold ${s.c}`}>{s.val}</div>
                <div className="text-xs text-slate-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Filters */}
          <div className="glass-card rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search questions..."
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500" />
              </div>
              <select value={companyFilter} onChange={e => setCompanyFilter(e.target.value)}
                className="px-4 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500/20 min-w-36">
                <option value="">All Companies</option>
                {companies.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            {loading ? (
              <div className="py-20 flex flex-col items-center"><Loader2 className="w-10 h-10 text-purple-600 animate-spin mb-4" /></div>
            ) : filtered.length === 0 ? (
              <div className="py-20 text-center"><BookOpen className="w-16 h-16 text-slate-200 mx-auto mb-4" /><p className="text-lg font-medium text-slate-500">No questions in queue</p></div>
            ) : (
              <div className="divide-y divide-slate-50">
                {filtered.map(q => {
                  const isExp = expanded === q.id;
                  const isEdit = editing === q.id;
                  return (
                    <div key={q.id} className="hover:bg-slate-50/50 transition-colors">
                      <div className="flex items-center gap-3 px-5 py-4">
                        <span className="text-xs text-slate-400 font-mono flex-shrink-0">#{q.id}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-900 font-medium line-clamp-2 mb-1">{q.question}</p>
                          <div className="flex flex-wrap items-center gap-1.5">
                            <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-lg">{q.company}</span>
                            <span className={`text-xs font-semibold border px-2 py-0.5 rounded-lg ${DIFF_BADGE[q.difficulty] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>{q.difficulty}</span>
                            <span className="text-xs text-slate-400 border border-slate-100 px-2 py-0.5 rounded-lg bg-slate-50">{q.round_type}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-bold capitalize ${q.status === 'pending' ? 'bg-amber-100 text-amber-700' : q.status === 'verified' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>{q.status}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {q.status === 'pending' && (
                            <>
                              <button onClick={() => { setEditing(isEdit ? null : q.id); setEditData({ company: q.company, difficulty: q.difficulty, round_type: q.round_type, question: q.question }); }}
                                className={`p-2 rounded-lg border text-xs font-medium transition-all ${isEdit ? 'bg-indigo-600 text-white border-transparent' : 'border-slate-200 text-slate-500 hover:bg-slate-100'}`}>
                                <Edit3 className="w-4 h-4" />
                              </button>
                              <button onClick={() => handleVerify(q.id)} disabled={actionId === q.id}
                                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-semibold disabled:opacity-50">
                                {actionId === q.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />}Verify
                              </button>
                              <button onClick={() => handleReject(q.id)} disabled={actionId === q.id}
                                className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 rounded-lg text-xs font-semibold disabled:opacity-50">
                                <XCircle className="w-3 h-3" />Reject
                              </button>
                            </>
                          )}
                          <button onClick={() => setExpanded(isExp ? null : q.id)} className="p-2 text-slate-400 hover:text-slate-700">
                            {isExp ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>

                      {isExp && (
                        <div className="px-5 pb-5 border-t border-slate-50 bg-slate-50/30">
                          {isEdit ? (
                            <div className="grid grid-cols-2 gap-4 pt-4">
                              <div>
                                <label className="text-xs font-bold text-slate-500 mb-1 block">Company</label>
                                <input value={editData.company || ''} onChange={e => setEditData((p: any) => ({...p, company: e.target.value}))}
                                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                              </div>
                              <div>
                                <label className="text-xs font-bold text-slate-500 mb-1 block">Difficulty</label>
                                <select value={editData.difficulty || ''} onChange={e => setEditData((p: any) => ({...p, difficulty: e.target.value}))}
                                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white">
                                  {['Easy', 'Medium', 'Hard'].map(d => <option key={d}>{d}</option>)}
                                </select>
                              </div>
                              <div>
                                <label className="text-xs font-bold text-slate-500 mb-1 block">Round Type</label>
                                <input value={editData.round_type || ''} onChange={e => setEditData((p: any) => ({...p, round_type: e.target.value}))}
                                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                              </div>
                              <div className="col-span-2">
                                <label className="text-xs font-bold text-slate-500 mb-1 block">Question Text</label>
                                <textarea rows={3} value={editData.question || ''} onChange={e => setEditData((p: any) => ({...p, question: e.target.value}))}
                                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                              </div>
                              <div className="col-span-2 flex gap-2">
                                <button onClick={() => handleSaveEdit(q.id)} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700">Save Changes</button>
                                <button onClick={() => setEditing(null)} className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm">Cancel</button>
                              </div>
                            </div>
                          ) : (
                            <div className="pt-4 space-y-2">
                              <p className="text-sm text-slate-700"><span className="font-semibold">Full question:</span> {q.question}</p>
                              {q.solution && <p className="text-sm text-slate-700"><span className="font-semibold">Solution:</span> {q.solution}</p>}
                              {q.source && <p className="text-sm text-slate-500"><span className="font-semibold">Source:</span> {q.source}</p>}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
