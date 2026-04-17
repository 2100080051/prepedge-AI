import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { Trophy, Medal, Crown, Star, TrendingUp, Users, IndianRupee, Building2, Loader2, ChevronDown } from 'lucide-react';
import { placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

interface LeaderboardEntry {
  rank: number;
  username: string;
  full_name: string;
  placement_count: number;
  avg_salary: number;
  highest_salary: number;
}

const RANK_STYLES: Record<number, { icon: any; bg: string; text: string; border: string }> = {
  1: { icon: <Crown className="w-6 h-6 text-yellow-500" />, bg: 'bg-gradient-to-r from-yellow-50 to-amber-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  2: { icon: <Medal className="w-6 h-6 text-slate-400" />, bg: 'bg-gradient-to-r from-slate-50 to-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
  3: { icon: <Medal className="w-6 h-6 text-amber-600" />, bg: 'bg-gradient-to-r from-orange-50 to-amber-50', text: 'text-amber-700', border: 'border-orange-200' },
};

export default function PlacementLeaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(10);
  const { user } = useAuthStore();
  const refreshRef = useRef<NodeJS.Timeout>();

  const loadData = async () => {
    try {
      const [lbRes, statsRes] = await Promise.allSettled([
        placementsApi.getLeaderboard(limit),
        placementsApi.getStats(),
      ]);
      if (lbRes.status === 'fulfilled') setLeaderboard(lbRes.value.data || []);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
    } catch (e) {
      // silently fail — public page
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    refreshRef.current = setInterval(loadData, 60000);
    return () => clearInterval(refreshRef.current);
  }, [limit]);

  return (
    <>
      <Head>
        <title>Placement Leaderboard — PrepEdge AI</title>
        <meta name="description" content="See which students are getting placed at top companies. Public leaderboard of verified placements." />
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-50 border border-amber-200 mb-6">
              <Trophy className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-semibold text-amber-800">Live Placement Leaderboard</span>
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Who's Getting <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Placed?</span>
            </h1>
            <p className="text-lg text-slate-600">Students who cracked their dream jobs through PrepEdge AI. Verified, real offers.</p>
          </div>

          {/* Stats Strip */}
          {stats && (
            <div className="grid grid-cols-3 gap-4 mb-10">
              {[
                { label: 'Verified Placements', value: stats.verified_placements ?? '—', icon: <Trophy className="w-5 h-5 text-amber-500" />, color: 'from-amber-50 to-yellow-50 border-amber-200' },
                { label: 'Avg Package', value: stats.avg_salary_lpa ? `${stats.avg_salary_lpa.toFixed(1)} LPA` : '—', icon: <IndianRupee className="w-5 h-5 text-emerald-500" />, color: 'from-emerald-50 to-teal-50 border-emerald-200' },
                { label: 'Top Company', value: stats.top_company ?? '—', icon: <Building2 className="w-5 h-5 text-indigo-500" />, color: 'from-indigo-50 to-purple-50 border-indigo-200' },
              ].map(s => (
                <div key={s.label} className={`glass-card p-5 rounded-2xl border bg-gradient-to-br ${s.color} text-center`}>
                  <div className="flex justify-center mb-2">{s.icon}</div>
                  <div className="text-2xl font-extrabold text-slate-900">{s.value}</div>
                  <div className="text-xs font-medium text-slate-600 mt-1">{s.label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Leaderboard Table */}
          <div className="glass-card rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-indigo-600" />Rankings</h2>
              <div className="flex items-center gap-2 text-sm text-slate-500"><Users className="w-4 h-4" />Showing {leaderboard.length} students</div>
            </div>

            {loading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
                <p className="text-slate-500">Loading leaderboard...</p>
              </div>
            ) : leaderboard.length === 0 ? (
              <div className="text-center py-20">
                <Trophy className="w-16 h-16 text-slate-200 mx-auto mb-4" />
                <p className="text-lg font-medium text-slate-500">No placements yet. Be the first!</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {leaderboard.map((entry, idx) => {
                  const rank = idx + 1;
                  const style = RANK_STYLES[rank];
                  const isCurrentUser = user?.username === entry.username;
                  return (
                    <div key={idx} className={`flex items-center gap-4 px-6 py-4 transition-all ${style?.bg ?? ''} ${isCurrentUser ? 'ring-2 ring-indigo-400 ring-offset-0' : ''}`}>
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-extrabold text-lg border ${style?.border ?? 'border-slate-200'} ${style?.text ?? 'text-slate-700'} bg-white flex-shrink-0`}>
                        {style?.icon ?? <span>#{rank}</span>}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-bold text-slate-900 truncate">{entry.full_name || entry.username}</p>
                          {isCurrentUser && <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-semibold flex-shrink-0">You</span>}
                        </div>
                        <p className="text-sm text-slate-500">@{entry.username}</p>
                      </div>
                      <div className="text-center hidden sm:block">
                        <div className="text-xl font-extrabold text-slate-900">{entry.placement_count}</div>
                        <div className="text-xs text-slate-500">Placements</div>
                      </div>
                      <div className="text-center hidden md:block">
                        <div className="text-base font-bold text-emerald-600">{entry.avg_salary ? `${entry.avg_salary.toFixed(1)} LPA` : '—'}</div>
                        <div className="text-xs text-slate-500">Avg Salary</div>
                      </div>
                      <div className="text-center">
                        <div className="text-base font-bold text-indigo-600">{entry.highest_salary ? `${entry.highest_salary.toFixed(1)} LPA` : '—'}</div>
                        <div className="text-xs text-slate-500">Highest</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {leaderboard.length > 0 && leaderboard.length >= limit && (
              <div className="p-6 border-t border-slate-50 text-center">
                <button onClick={() => setLimit(prev => prev + 20)}
                  className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full border border-slate-200 text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 font-medium text-sm transition-all">
                  <ChevronDown className="w-4 h-4" /> Load More
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
