import { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { Building2, IndianRupee, Clock, CheckCircle2, ChevronRight, Briefcase, Plus, Loader2, Award, Calendar } from 'lucide-react';
import PlacementLogModal from '@/components/PlacementLogModal';

export default function MyPlacements() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [placements, setPlacements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }
    fetchPlacements();
  }, [isAuthenticated]);

  const fetchPlacements = async () => {
    setLoading(true);
    try {
      const res = await placementsApi.getMyPlacements();
      setPlacements(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const verifiedCount = placements.filter(p => p.is_verified).length;
  const pendingCount = placements.length - verifiedCount;
  const totalSalaries = placements.filter(p => p.salary_lpa && p.is_verified).map(p => Number(p.salary_lpa));
  const avgSalary = totalSalaries.length > 0 ? (totalSalaries.reduce((a, b) => a + b, 0) / totalSalaries.length).toFixed(1) : 0;

  return (
    <>
      <Head>
        <title>My Placements — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 mb-3 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider">
                Placement Tracker
              </div>
              <h1 className="text-3xl font-heading font-extrabold text-slate-900">
                My <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Placements</span>
              </h1>
              <p className="text-slate-500 mt-1">Track and manage your placement offers and interviews.</p>
            </div>
            <button onClick={() => setModalOpen(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-glow transition-all text-sm">
              <Plus className="w-4 h-4" /> Log Placement
            </button>
          </div>

          {!loading && placements.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
              <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                  <Briefcase className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-900">{placements.length}</p>
                  <p className="text-xs font-semibold text-slate-500 uppercase">Total Logged</p>
                </div>
              </div>
              <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-900">{verifiedCount}</p>
                  <p className="text-xs font-semibold text-slate-500 uppercase">Verified Offers</p>
                </div>
              </div>
              <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-500">
                  <IndianRupee className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-2xl font-black text-slate-900">{avgSalary || '—'} <span className="text-base font-semibold text-slate-500">{avgSalary ? 'LPA' : ''}</span></p>
                  <p className="text-xs font-semibold text-slate-500 uppercase">Avg. Verified Salary</p>
                </div>
              </div>
            </div>
          )}

          <div className="glass-card rounded-3xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            {loading ? (
              <div className="h-64 flex flex-col items-center justify-center">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-4" />
                <p className="text-slate-500">Loading your placements...</p>
              </div>
            ) : placements.length === 0 ? (
              <div className="h-96 flex flex-col items-center justify-center p-8 text-center bg-slate-50/50">
                <div className="w-20 h-20 bg-white border border-slate-200 rounded-full flex items-center justify-center mb-6 shadow-sm">
                  <Award className="w-10 h-10 text-slate-300" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">No Placements Yet</h3>
                <p className="text-slate-500 max-w-sm mb-6">You haven't logged any placements or interview rounds. Your logged placements will appear here once you add them.</p>
                <button onClick={() => setModalOpen(true)}
                  className="px-6 py-3 bg-indigo-50 text-indigo-600 font-bold rounded-xl hover:bg-indigo-100 transition-colors">
                  Log First Placement
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Company & Role</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Salary (LPA)</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {placements.map(p => (
                      <tr key={p.id} className="hover:bg-slate-50/50 transition-colors group">
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
                              <Building2 className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{p.company_name}</p>
                              <p className="text-sm text-slate-500">{p.round_type || 'General Off-Campus'}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          {p.salary_lpa ? (
                            <span className="inline-flex items-center gap-1 font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100">
                              <IndianRupee className="w-3.5 h-3.5" />{p.salary_lpa}
                            </span>
                          ) : (
                            <span className="text-slate-400 font-medium">Undisclosed</span>
                          )}
                        </td>
                        <td className="px-6 py-5 text-sm text-slate-600 flex items-center gap-1.5 mt-2.5">
                          <Calendar className="w-4 h-4 text-slate-400" />
                          {new Date(p.created_at || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        </td>
                        <td className="px-6 py-5">
                          {p.is_verified ? (
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-sm">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                            </div>
                          ) : (
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200 shadow-sm">
                              <Clock className="w-3.5 h-3.5" /> Pending Review
                            </div>
                          )}
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
      
      <PlacementLogModal isOpen={modalOpen} onClose={() => setModalOpen(false)} onSuccess={fetchPlacements} />
    </>
  );
}
