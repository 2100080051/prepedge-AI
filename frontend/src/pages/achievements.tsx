import { useState, useEffect } from 'react';
import Head from 'next/head';
import { Trophy, Star, Shield, Zap, Target, Flame, Loader2, Lock, Hexagon } from 'lucide-react';
import { gamificationApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useImageGeneration } from '@/hooks/useImageGeneration';

const ALL_ACHIEVEMENTS = [
  { id: 'first_blood', title: 'First Blood', desc: 'Solve your first interview question.', xp: 50, icon: <Target className="w-6 h-6"/>, color: 'from-blue-400 to-indigo-500' },
  { id: 'streak_3', title: 'Consistent Learner', desc: 'Maintain a 3-day learning streak.', xp: 100, icon: <Flame className="w-6 h-6"/>, color: 'from-orange-400 to-red-500' },
  { id: 'streak_7', title: 'Unstoppable', desc: 'Maintain a 7-day learning streak.', xp: 300, icon: <Flame className="w-6 h-6"/>, color: 'from-rose-400 to-pink-600' },
  { id: 'placement_logged', title: 'Career Mover', desc: 'Log your first placement or offer.', xp: 500, icon: <Trophy className="w-6 h-6"/>, color: 'from-emerald-400 to-teal-500' },
  { id: 'level_10', title: 'Rising Star', desc: 'Reach Level 10.', xp: 1000, icon: <Star className="w-6 h-6"/>, color: 'from-amber-400 to-orange-500' },
  { id: 'hard_solver', title: 'Brainiac', desc: 'Solve 10 Hard difficulty questions.', xp: 800, icon: <Zap className="w-6 h-6"/>, color: 'from-purple-400 to-fuchsia-500' },
  { id: 'mock_master', title: 'Interview Ready', desc: 'Complete 5 MockMate sessions.', xp: 400, icon: <Shield className="w-6 h-6"/>, color: 'from-cyan-400 to-blue-500' },
];

const BadgeImage = ({ achievement, isUnlocked, defaultIcon, defaultColor }: any) => {
  const { generateBadge, loading, imageUrl } = useImageGeneration();

  useEffect(() => {
    if (isUnlocked && !imageUrl && !loading) {
      generateBadge(achievement.title, 'gold_medal');
    }
  }, [isUnlocked]);

  if (!isUnlocked) {
    return (
      <div className="w-20 h-20 rounded-2xl bg-slate-200 flex items-center justify-center text-slate-400">
        <Lock className="w-8 h-8" />
      </div>
    );
  }

  if (loading || !imageUrl) {
    return (
      <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${defaultColor} flex items-center justify-center text-white shadow-lg shadow-current/30 rotate-3 animate-pulse`}>
        <Loader2 className="w-6 h-6 animate-spin opacity-50" />
      </div>
    );
  }

  return (
    <div className="relative w-28 h-28 transform transition-transform hover:scale-110 duration-300">
      <img src={imageUrl} alt={achievement.title} className="w-full h-full object-contain filter drop-shadow-xl" loading="lazy" />
    </div>
  );
};


export default function AchievementsPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const res = await gamificationApi.getUserStats();
      if (res.data?.success) {
        setStats(res.data.stats);
      }
    } catch (e) {
      console.error(e);
      // Fallback for visual testing
      setStats({
        level: 5,
        total_xp: 5400,
        current_streak: 2,
        unlocked: ['first_blood', 'streak_3']
      });
    } finally {
      setLoading(false);
    }
  };

  const unlockedIds = stats?.unlocked || ['first_blood']; // Mock fallback

  return (
    <>
      <Head>
        <title>Achievements | PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center p-3 bg-amber-100 text-amber-700 rounded-2xl mb-4 shadow-sm border border-amber-200">
              <Star className="w-8 h-8 fill-amber-500 text-amber-500" />
            </div>
            <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-slate-900 mb-4 tracking-tight">Your Achievements</h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Unlock badges, earn XP bonuses, and show off your progress to recruiters.
            </p>
          </div>

          {loading ? (
            <div className="py-32 flex flex-col items-center justify-center glass-card bg-white rounded-3xl border border-slate-200">
              <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
              <p className="text-slate-500 font-medium">Loading your trophy room...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {ALL_ACHIEVEMENTS.map(ach => {
                const isUnlocked = unlockedIds.includes(ach.id);
                
                return (
                  <div 
                    key={ach.id} 
                    className={`relative overflow-hidden rounded-3xl border-2 transition-all duration-300 p-6 flex flex-col items-center text-center
                      ${isUnlocked 
                        ? 'bg-white border-transparent shadow-xl shadow-slate-200/50 hover:-translate-y-1' 
                        : 'bg-slate-50 border-slate-200 opacity-60 grayscale-[0.5] hover:grayscale-0'}`}
                  >
                    {/* Glowing background for unlocked */}
                    {isUnlocked && (
                      <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-32 h-32 bg-gradient-to-br ${ach.color} opacity-20 blur-3xl rounded-full`}></div>
                    )}
                    
                    <div className="relative mb-4 min-h-[112px] flex items-center justify-center">
                      <BadgeImage 
                        achievement={ach} 
                        isUnlocked={isUnlocked} 
                        defaultIcon={ach.icon}
                        defaultColor={ach.color}
                      />
                    </div>
                    
                    <h3 className={`text-lg font-extrabold mb-2 ${isUnlocked ? 'text-slate-900' : 'text-slate-500'}`}>
                      {ach.title}
                    </h3>
                    <p className="text-sm text-slate-600 mb-6 flex-1">
                      {ach.desc}
                    </p>
                    
                    <div className={`px-4 py-1.5 rounded-full text-xs font-bold w-full uppercase tracking-wider
                      ${isUnlocked ? 'bg-indigo-50 text-indigo-700' : 'bg-slate-200 text-slate-500'}`}>
                      {isUnlocked ? 'Unlocked' : `Reward: +${ach.xp} XP`}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

        </div>
      </div>
    </>
  );
}
