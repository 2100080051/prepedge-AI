import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Shield, CheckCircle2, Clock, XCircle, Filter, Search, Eye, Loader2, RefreshCw, Building2, User, IndianRupee, ExternalLink, CheckCheck, ArrowUpDown } from 'lucide-react';
import { adminApi, placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

interface Placement {
  id: number;
  user_id: number;
  username: string;
  full_name: string;
  company_name: string;
  salary_lpa: number | null;
  offer_letter_url: string | null;
  round_type: string | null;
  total_rounds: number | null;
  status: 'pending' | 'verified' | 'rejected';
  created_at: string;
}

const STATUS_BADGE = {
  pending:  'bg-amber-100 text-amber-800 border-amber-200',
  verified: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  rejected: 'bg-red-100 text-red-800 border-red-200',
};

export default function AdminPlacementsPage() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [placements, setPlacements] = useState<Placement[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [search, setSearch] = useState('');
  const [sortConfig, setSortConfig] = useState<{key: keyof Placement, direction: 'asc'|'desc'} | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [toast, setToast] = useState('');

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    loadData();
  }, [isAuthenticated]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [allRes, statsRes] = await Promise.allSettled([
        adminApi.getAllPlacements(statusFilter !== 'all' ? statusFilter : undefined),
        placementsApi.getStats(),
      ]);
      if (allRes.status === 'fulfilled') setPlacements(allRes.value.data || []);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
    } catch (e) {}
    finally { setLoading(false); }
  };

  useEffect(() => { loadData(); }, [statusFilter]);

  const handleVerify = async (id: number) => {
    setActionLoading(id);
    try {
      await adminApi.verifyPlacement(id);
      setPlacements(prev => prev.map(p => p.id === id ? { ...p, status: 'verified' } : p));
      showToast('✅ Placement verified successfully!');
    } catch (e: any) {
      showToast(e.response?.data?.detail || 'Verification failed.');
    } finally { setActionLoading(null); }
  };

  const handleReject = async (id: number) => {
    setActionLoading(id);
    try {
      await adminApi.rejectPlacement(id);
      setPlacements(prev => prev.map(p => p.id === id ? { ...p, status: 'rejected' } : p));
      showToast('Placement rejected.');
    } catch (e: any) {
      showToast(e.response?.data?.detail || 'Rejection failed.');
    } finally { setActionLoading(null); }
  };

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const filtered = placements.filter(p => {
    const q = search.toLowerCase();
    return !q || p.company_name.toLowerCase().includes(q) || p.username?.toLowerCase().includes(q) || p.full_name?.toLowerCase().includes(q);
  });

  const sortedPlacements = [...filtered].sort((a, b) => {
    if (!sortConfig) return 0;
    const { key, direction } = sortConfig;
    if (a[key] === null) return 1;
    if (b[key] === null) return -1;
    if (a[key]! < b[key]!) return direction === 'asc' ? -1 : 1;
    if (a[key]! > b[key]!) return direction === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSort = (key: keyof Placement) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') direction = 'desc';
    setSortConfig({ key, direction });
  };

  const pendingCount = placements.filter(p => p.status === 'pending').length;

  return (
    <>
      <Head><title>Admin — Placement Verification | PrepEdge AI</title></Head>
      {toast && (
        <div className="fixed top-6 right-6 z-[200] px-6 py-3 bg-slate-900 text-white rounded-xl shadow-2xl font-medium text-sm animate-fade-in">{toast}</div>
      )}

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-indigo-600 p-2 rounded-xl"><Shield className="w-5 h-5 text-white" /></div>
                <h1 className="text-2xl font-heading font-extrabold text-slate-900">Placement Verification</h1>
              </div>
              <p className="text-slate-500 text-sm">Review and verify student placement submissions</p>
            </div>
            <button onClick={loadData} className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
          </div>

          {/* Stats Grid */}
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Total Placements', value: stats.total_placements ?? '—', color: 'text-slate-900' },
                { label: 'Verified', value: stats.verified_placements ?? '—', color: 'text-emerald-600' },
                { label: 'Pending', value: pendingCount, color: 'text-amber-600' },
                { label: 'Avg Salary', value: stats.avg_salary_lpa ? `${stats.avg_salary_lpa.toFixed(1)} LPA` : '—', color: 'text-indigo-600' },
              ].map(s => (
                <div key={s.label} className="glass-card p-5 rounded-2xl border border-slate-200 bg-white text-center">
                  <div className={`text-2xl font-extrabold ${s.color}`}>{s.value}</div>
                  <div className="text-xs text-slate-500 font-medium mt-1">{s.label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Table Card */}
          <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white">
            {/* Filters Bar */}
            <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Search by company or student name..."
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-400 flex-shrink-0" />
                {['pending', 'verified', 'rejected', 'all'].map(s => (
                  <button key={s} onClick={() => setStatusFilter(s)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold border capitalize transition-all ${statusFilter === s ? 'bg-indigo-600 text-white border-transparent' : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'}`}>
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {loading ? (
              <div className="py-20 flex flex-col items-center"><Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" /><p className="text-slate-500">Loading placements...</p></div>
            ) : sortedPlacements.length === 0 ? (
              <div className="py-20 text-center"><CheckCheck className="w-16 h-16 text-slate-200 mx-auto mb-4" /><p className="text-lg font-medium text-slate-500">No placements to show</p></div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 border-b border-slate-100">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">ID</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Student</th>
                      <th onClick={() => handleSort('company_name')} className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100"><div className="flex items-center gap-1">Company <ArrowUpDown className="w-3 h-3"/></div></th>
                      <th onClick={() => handleSort('salary_lpa')} className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100"><div className="flex items-center gap-1">Salary <ArrowUpDown className="w-3 h-3"/></div></th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Round</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                      <th onClick={() => handleSort('created_at')} className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100"><div className="flex items-center gap-1">Date <ArrowUpDown className="w-3 h-3"/></div></th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {sortedPlacements.map(p => (
                      <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-4 py-4 text-slate-500 font-mono text-xs">#{p.id}</td>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                              {(p.full_name || p.username || '?')[0].toUpperCase()}
                            </div>
                            <div>
                              <div className="font-semibold text-slate-900">{p.full_name || p.username}</div>
                              <div className="text-xs text-slate-400">@{p.username}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 font-semibold text-slate-800">{p.company_name}</td>
                        <td className="px-4 py-4 text-emerald-600 font-bold">{p.salary_lpa ? `${p.salary_lpa} LPA` : '—'}</td>
                        <td className="px-4 py-4 text-slate-500 text-xs">{p.round_type || '—'}</td>
                        <td className="px-4 py-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold border capitalize ${STATUS_BADGE[p.status]}`}>{p.status}</span>
                        </td>
                        <td className="px-4 py-4 text-slate-500 text-xs">{p.created_at ? new Date(p.created_at).toLocaleDateString('en-IN') : '—'}</td>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-2">
                            {p.offer_letter_url && (
                              <a href={p.offer_letter_url} target="_blank" rel="noopener noreferrer"
                                className="p-1.5 text-slate-400 hover:text-indigo-600 transition-colors" title="View offer letter">
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            )}
                            {p.status === 'pending' && (
                              <>
                                <button onClick={() => handleVerify(p.id)} disabled={actionLoading === p.id}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-semibold transition-all disabled:opacity-50">
                                  {actionLoading === p.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />}Verify
                                </button>
                                <button onClick={() => handleReject(p.id)} disabled={actionLoading === p.id}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 rounded-lg text-xs font-semibold transition-all disabled:opacity-50">
                                  {actionLoading === p.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <XCircle className="w-3 h-3" />}Reject
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
