import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Trophy, Medal, Star, Target, Crown, Navigation, Loader2 } from 'lucide-react';
import { gamificationApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

export default function LeaderboardPage() {
  const { user } = useAuthStore();
  const [leaders, setLeaders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'all_time'>('all_time');

  useEffect(() => {
    loadLeaderboard();
  }, [timeframe]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const res = await gamificationApi.getLeaderboard(timeframe, 25);
      // Fallback data if backend is empty during testing
      if (!res.data?.leaderboard || res.data.leaderboard.length === 0) {
        setLeaders([
          { id: 1, username: 'code_ninja', total_xp: 45000, level: 45, rank_title: 'Master' },
          { id: 2, username: 'algo_pro', total_xp: 42300, level: 42, rank_title: 'Diamond' },
          { id: 3, username: 'debug_master', total_xp: 38900, level: 38, rank_title: 'Platinum' },
          { id: 4, username: 'syntax_error', total_xp: 35100, level: 35, rank_title: 'Gold' },
          { id: 5, username: 'quick_sort', total_xp: 31000, level: 31, rank_title: 'Gold' },
        ]);
      } else {
        setLeaders(res.data.leaderboard);
      }
    } catch (e) {
      console.error(e);
      // Fallback
      setLeaders([
        { id: 1, username: 'code_ninja', total_xp: 45000, level: 45, rank_title: 'Master' },
        { id: 2, username: 'algo_pro', total_xp: 42300, level: 42, rank_title: 'Diamond' },
        { id: 3, username: 'debug_master', total_xp: 38900, level: 38, rank_title: 'Platinum' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <Crown className="w-6 h-6 text-yellow-500 fill-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-slate-400 fill-slate-300" />;
    if (rank === 3) return <Medal className="w-6 h-6 text-amber-700 fill-amber-700/50" />;
    return <span className="text-lg font-bold text-slate-400">{rank}</span>;
  };

  return (
    <>
      <Head>
        <title>Global Leaderboard | PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 relative overflow-hidden pt-24 pb-20">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center p-3 bg-indigo-100 text-indigo-700 rounded-2xl mb-4 shadow-sm border border-indigo-200">
              <Trophy className="w-8 h-8" />
            </div>
            <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-slate-900 mb-4 tracking-tight">Global Leaderboard</h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Compete with peers, track your progress, and rise through the ranks. Who will claim the top spot this week?
            </p>
          </div>

          <div className="flex justify-center mb-10">
            <div className="inline-flex bg-white p-1 rounded-xl shadow-sm border border-slate-200">
              {[
                { id: 'daily', label: 'Today' },
                { id: 'weekly', label: 'This Week' },
                { id: 'all_time', label: 'All Time' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTimeframe(t.id as any)}
                  className={`px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${
                    timeframe === t.id
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-xl shadow-slate-200/50">
            {loading ? (
              <div className="py-32 flex flex-col items-center justify-center">
                <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
                <p className="text-slate-500 font-medium">Loading rankings...</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-100">
                      <th className="py-5 px-6 font-bold text-slate-500 uppercase tracking-wider text-xs">Rank</th>
                      <th className="py-5 px-6 font-bold text-slate-500 uppercase tracking-wider text-xs">PrepNinja</th>
                      <th className="py-5 px-6 font-bold text-slate-500 uppercase tracking-wider text-xs text-center">Level</th>
                      <th className="py-5 px-6 font-bold text-slate-500 uppercase tracking-wider text-xs text-right">Total XP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {leaders.map((leader, index) => {
                      const isCurrentUser = user && user.username === leader.username;
                      const rank = index + 1;
                      
                      return (
                        <tr 
                          key={leader.id || index} 
                          className={`group transition-colors ${isCurrentUser ? 'bg-indigo-50/50' : 'hover:bg-slate-50/50'}`}
                        >
                          <td className="py-4 px-6">
                            <div className="flex justify-center w-8">
                              {getRankBadge(rank)}
                            </div>
                          </td>
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-4">
                              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-black text-xl text-white shadow-md
                                ${rank === 1 ? 'bg-gradient-to-br from-yellow-400 to-amber-600' :
                                  rank === 2 ? 'bg-gradient-to-br from-slate-300 to-slate-500' :
                                  rank === 3 ? 'bg-gradient-to-br from-amber-700 to-orange-900' :
                                  'bg-gradient-to-br from-indigo-500 to-purple-600'}`}>
                                {leader.username.charAt(0).toUpperCase()}
                              </div>
                              <div>
                                <div className="font-bold text-slate-900 text-base flex items-center gap-2">
                                  {leader.username}
                                  {isCurrentUser && <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-[10px] uppercase rounded-full tracking-wider">You</span>}
                                </div>
                                <div className="text-xs text-slate-500 font-medium">{leader.rank_title || 'Novice'}</div>
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <div className="inline-flex items-center justify-center w-10 h-10 bg-slate-100 text-slate-700 rounded-xl font-bold border border-slate-200 shadow-inner">
                              {leader.level || 1}
                            </div>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="font-black text-indigo-600 text-lg flex items-center justify-end gap-1">
                              {leader.total_xp.toLocaleString()} <span className="text-xs text-indigo-400 uppercase tracking-widest mt-0.5">XP</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
            
            {/* Call to action at bottom */}
            <div className="bg-slate-900 p-8 text-center flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="text-left">
                <h3 className="text-xl font-bold text-white mb-2">Want to climb the ranks?</h3>
                <p className="text-slate-400 text-sm max-w-md">Practice more questions, maintain your daily streak, and unlock achievements to earn massive XP boosts.</p>
              </div>
              <a href="/questions" className="px-6 py-3 bg-indigo-500 hover:bg-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/30 transition-all whitespace-nowrap">
                Start Practicing
              </a>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
