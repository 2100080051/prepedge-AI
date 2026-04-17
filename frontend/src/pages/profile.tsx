import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { User as UserIcon, Mail, Calendar, Trophy, Zap, Target, Star, Briefcase, ChevronRight, Settings, Loader2, Award, Flame, Hexagon, Crosshair } from 'lucide-react';
import { authApi, gamificationApi, questionsApi, placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  
  const [profile, setProfile] = useState<any>(null);
  const [gamification, setGamification] = useState<any>(null);
  const [qStats, setQStats] = useState<any>(null);
  const [placements, setPlacements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    loadProfileDashboard();
  }, [isAuthenticated]);

  const loadProfileDashboard = async () => {
    try {
      const [uRes, gRes, qRes, pRes] = await Promise.allSettled([
        authApi.getCurrentUser(),
        gamificationApi.getUserStats(),
        questionsApi.getUserStats(),
        placementsApi.getMyPlacements()
      ]);
      
      if (uRes.status === 'fulfilled') setProfile(uRes.value.data);
      if (gRes.status === 'fulfilled') setGamification(gRes.value.data?.stats);
      if (qRes.status === 'fulfilled') setQStats(qRes.value.data);
      if (pRes.status === 'fulfilled') setPlacements(pRes.value.data?.data || []);
      
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 pt-24 pb-16 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
          <p className="text-slate-500 font-medium">Assembling your profile dashboard...</p>
        </div>
      </div>
    );
  }

  // Calculate progress to next level
  const currXp = gamification?.total_xp || 0;
  const currLvl = gamification?.level || 1;
  const nextLvlXp = (currLvl * 1000); // Simple progression math to mock next level target if not sent
  const prevLvlXp = ((currLvl - 1) * 1000);
  const progressPct = Math.min(100, Math.max(0, ((currXp - prevLvlXp) / (nextLvlXp - prevLvlXp)) * 100));

  return (
    <>
      <Head>
        <title>My Profile — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Top Hero Section */}
          <div className="relative mb-8 rounded-3xl overflow-hidden glass-card bg-white border border-slate-200 shadow-sm p-8 sm:p-12">
            {/* Background design elements */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-indigo-100 via-purple-50 to-transparent rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-70 pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-emerald-50 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>

            <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center md:items-start text-center md:text-left">
              
              {/* Avatar & Level Badge */}
              <div className="relative group">
                <div className="w-32 h-32 rounded-3xl bg-gradient-to-br from-indigo-600 to-purple-600 p-1 shadow-xl">
                  <div className="w-full h-full bg-slate-900 rounded-[1.4rem] flex items-center justify-center text-5xl font-black text-white outline outline-4 outline-white/20">
                    {profile?.username?.[0]?.toUpperCase() || '?'}
                  </div>
                </div>
                <div className="absolute -bottom-4 -right-4 flex items-center justify-center w-14 h-14 bg-white rounded-full p-1 shadow-lg border-2 border-indigo-100">
                  <div className="w-full h-full bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-inner">
                    {currLvl}
                  </div>
                </div>
              </div>

              {/* Basic Info */}
              <div className="flex-1">
                <div className="flex items-center justify-center md:justify-start gap-4 mb-2">
                  <h1 className="text-4xl font-heading font-extrabold text-slate-900">{profile?.full_name || profile?.username}</h1>
                  <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-lg uppercase tracking-wide border border-indigo-200">
                    Pro Member
                  </span>
                </div>
                <p className="text-slate-500 font-medium mb-6 flex items-center justify-center md:justify-start gap-2">
                  <Mail className="w-4 h-4" /> {profile?.email}
                </p>

                {/* Level Progress Bar */}
                <div className="max-w-md w-full">
                  <div className="flex items-center justify-between text-sm font-bold mb-2">
                    <span className="text-slate-700">Level {currLvl} <span className="text-slate-400 font-medium ml-1">({gamification?.rank_title || 'Novice'})</span></span>
                    <span className="text-indigo-600">{currXp} <span className="text-indigo-300 font-medium">/ {nextLvlXp} XP</span></span>
                  </div>
                  <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200 shadow-inner">
                    <div 
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full relative"
                      style={{ width: `${progressPct}%` }}
                    >
                      <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]"></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-3 w-full md:w-auto mt-4 md:mt-0">
                <Link href="/settings" className="flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors shadow-sm w-full">
                  <Settings className="w-4 h-4" /> Account Settings
                </Link>
                <div className="px-6 py-3 bg-slate-50 border border-slate-100 text-slate-500 font-medium rounded-xl text-center text-sm w-full flex items-center justify-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" /> Joined {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Recently'}
                </div>
              </div>

            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Column: Gamification Stats */}
            <div className="lg:col-span-1 space-y-8">
              <div className="glass-card bg-white rounded-3xl p-6 border border-slate-200 shadow-sm relative overflow-hidden group">
                <div className="absolute -right-10 -top-10 text-orange-50 group-hover:scale-110 transition-transform duration-500">
                  <Flame className="w-48 h-48" />
                </div>
                <div className="relative z-10 flex items-center justify-between">
                  <div>
                    <h3 className="text-slate-500 font-bold uppercase tracking-wider text-xs mb-1">Current Streak</h3>
                    <div className="text-5xl font-black text-slate-900 mb-2 flex items-baseline gap-2">
                      {gamification?.current_streak || 0} <span className="text-xl text-orange-500">Days</span>
                    </div>
                    {gamification?.longest_streak > 0 && (
                      <p className="text-sm font-semibold text-slate-400">Best: {gamification.longest_streak} days</p>
                    )}
                  </div>
                  <div className="w-16 h-16 rounded-full bg-orange-100 flex items-center justify-center border-4 border-white shadow-sm">
                    <Flame className="w-8 h-8 text-orange-500" />
                  </div>
                </div>
              </div>

              <div className="glass-card bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-bold text-slate-900 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-amber-500" /> Badges Earned
                  </h3>
                  <Link href="/achievements" className="text-sm font-bold text-indigo-600 hover:text-indigo-700 flex items-center">
                    View All <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                
                <div className="grid grid-cols-3 gap-3">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="aspect-square rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center flex-col gap-1 p-2 hover:bg-white hover:border-indigo-100 hover:shadow-md transition-all cursor-pointer">
                      <Hexagon className={`w-8 h-8 ${i < (gamification?.achievements_unlocked || 2) ? 'text-indigo-500 fill-indigo-100' : 'text-slate-200'}`} />
                      <span className="text-[10px] font-bold text-slate-400 uppercase">Badge</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Question Analytics & Placement Logs */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* Question Practice Stats */}
              <div className="glass-card bg-white rounded-3xl p-6 md:p-8 border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-8">
                  <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <Crosshair className="w-6 h-6 text-indigo-500" /> Question Accuracy
                  </h2>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                  <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center">
                    <div className="text-4xl font-black text-slate-900 mb-1">{qStats?.total_attempts || 0}</div>
                    <div className="text-xs font-bold text-slate-500 uppercase">Total Solved</div>
                  </div>
                  <div className="bg-emerald-50 rounded-2xl p-4 border border-emerald-100 text-center">
                    <div className="text-4xl font-black text-emerald-600 mb-1">{qStats?.easy_solved || 0}</div>
                    <div className="text-xs font-bold text-emerald-700/70 uppercase">Easy</div>
                  </div>
                  <div className="bg-amber-50 rounded-2xl p-4 border border-amber-100 text-center">
                    <div className="text-4xl font-black text-amber-600 mb-1">{qStats?.medium_solved || 0}</div>
                    <div className="text-xs font-bold text-amber-700/70 uppercase">Medium</div>
                  </div>
                  <div className="bg-rose-50 rounded-2xl p-4 border border-rose-100 text-center">
                    <div className="text-4xl font-black text-rose-600 mb-1">{qStats?.hard_solved || 0}</div>
                    <div className="text-xs font-bold text-rose-700/70 uppercase">Hard</div>
                  </div>
                </div>

                <div className="bg-slate-900 rounded-2xl p-6 text-white flex items-center justify-between relative overflow-hidden">
                  <div className="absolute right-0 top-0 w-64 h-64 bg-indigo-500 rounded-full blur-3xl opacity-20 -translate-y-1/2 translate-x-1/4"></div>
                  <div className="relative z-10">
                    <h3 className="font-bold text-slate-300 mb-1 uppercase tracking-wider text-sm">Overall Accuracy</h3>
                    <div className="text-4xl font-black flex items-baseline gap-2">
                      {qStats?.accuracy_percentage || 0}<span className="text-xl text-slate-400">%</span>
                    </div>
                  </div>
                  <div className="relative z-10 w-16 h-16 rounded-full border-[6px] border-indigo-500/30 flex items-center justify-center">
                    <div className="text-indigo-400 font-bold flex items-center"><Target className="w-6 h-6"/></div>
                  </div>
                </div>
              </div>

              {/* Placement Applications Sync */}
              <div className="glass-card bg-white rounded-3xl p-6 md:p-8 border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <Briefcase className="w-6 h-6 text-indigo-500" /> Tracked Placements
                  </h2>
                  <Link href="/placements/my-placements" className="px-4 py-2 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-600 transition-colors rounded-xl text-sm font-bold text-slate-600 border border-slate-200">
                    Manage Logs
                  </Link>
                </div>

                {placements.length === 0 ? (
                  <div className="p-8 border-2 border-dashed border-slate-200 rounded-2xl text-center bg-slate-50">
                    <Award className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                    <h3 className="font-bold text-slate-700 mb-1">No applications logged</h3>
                    <p className="text-sm text-slate-500 mb-4">Start tracking your job search success to appear on the leaderboard.</p>
                    <Link href="/placements/my-placements" className="inline-flex font-bold text-indigo-600 hover:text-indigo-700 text-sm">
                      Log First Placement <ChevronRight className="w-4 h-4 ml-1" />
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {placements.slice(0, 3).map(p => (
                      <div key={p.id} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-slate-50 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-700 font-black text-lg border border-indigo-100">
                            {p.company_name.charAt(0)}
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-900">{p.company_name}</h4>
                            <p className="text-xs text-slate-500">{new Date(p.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>
                        <div className={`px-3 py-1 text-xs font-bold rounded-full capitalize border 
                          ${p.status === 'verified' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                            p.status === 'rejected' ? 'bg-rose-50 text-rose-700 border-rose-200' : 
                            'bg-amber-50 text-amber-700 border-amber-200'}`}>
                          {p.status}
                        </div>
                      </div>
                    ))}
                    {placements.length > 3 && (
                      <div className="pt-2 text-center">
                        <Link href="/placements/my-placements" className="text-sm font-semibold text-slate-500 hover:text-indigo-600 transition-colors">
                          View {placements.length - 3} more
                        </Link>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          </div>

        </div>
      </div>
    </>
  );
}
