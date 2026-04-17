import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { placementsApi } from '@/lib/api';
import {
  Brain, FileText, Mic, Zap, BookOpen, Trophy, TrendingUp,
  Plus, ChevronRight, Shield, Target, Sparkles, IndianRupee, Building2
} from 'lucide-react';
import PlacementLogModal from '@/components/PlacementLogModal';

const MODULES = [
  { href: '/learnai',    emoji: '🧠', icon: <Brain className="w-6 h-6" />, title: 'LearnAI Hub',  desc: 'Master any concept with AI explanations & PDF summarizer',             color: 'from-indigo-500 to-purple-600',  bg: 'from-indigo-50 to-purple-50', border: 'border-indigo-200' },
  { href: '/flashlearn', emoji: '⚡', icon: <Zap className="w-6 h-6" />,   title: 'FlashLearn',   desc: 'Company-specific flashcards for TCS, Infosys, Wipro & more',          color: 'from-amber-500 to-orange-600',   bg: 'from-amber-50 to-orange-50',  border: 'border-amber-200' },
  { href: '/resumeai',   emoji: '📄', icon: <FileText className="w-6 h-6" />, title: 'ResumeAI',   desc: 'AI resume screening with ATS optimization & suggestions',              color: 'from-emerald-500 to-teal-600',   bg: 'from-emerald-50 to-teal-50',  border: 'border-emerald-200' },
  { href: '/mockmate',   emoji: '🎙️', icon: <Mic className="w-6 h-6" />,   title: 'MockMate',     desc: 'Practice interviews with AI + anti-cheat proctoring system',          color: 'from-rose-500 to-pink-600',      bg: 'from-rose-50 to-pink-50',     border: 'border-rose-200' },
  { href: '/questions',  emoji: '📚', icon: <BookOpen className="w-6 h-6" />, title: 'Question Bank', desc: 'Real interview questions from top companies, by round & difficulty',  color: 'from-cyan-500 to-sky-600',       bg: 'from-cyan-50 to-sky-50',      border: 'border-cyan-200' },
  { href: '/prep/study-plan', emoji: '📅', icon: <Target className="w-6 h-6" />, title: 'Study Plan', desc: 'AI-generated day-by-day preparation plan for your target company',   color: 'from-violet-500 to-purple-600',  bg: 'from-violet-50 to-purple-50', border: 'border-violet-200' },
];

export default function Dashboard() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [placementModalOpen, setPlacementModalOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }
    setLoadingStats(true);
    placementsApi.getStats()
      .then(r => setStats(r.data))
      .catch(() => setStats(null))
      .finally(() => setLoadingStats(false));
  }, [isAuthenticated]);

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Dashboard — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

          {/* Welcome Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
            <div>
              <h1 className="text-3xl font-heading font-extrabold text-slate-900">
                Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">{user.full_name || user.username}</span> 👋
              </h1>
              <p className="text-slate-500 mt-1">
                Continue your placement preparation journey.
                <span className="ml-2 px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded-full font-semibold uppercase">{user.subscription_plan || 'Free'}</span>
              </p>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setPlacementModalOpen(true)}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-glow transition-all text-sm">
                <Plus className="w-4 h-4" /> Log Placement
              </button>
              {user.is_admin && (
                <Link href="/admin" className="flex items-center gap-2 px-5 py-2.5 border border-purple-200 text-purple-700 font-semibold rounded-xl hover:bg-purple-50 transition-all text-sm">
                  <Shield className="w-4 h-4" /> Admin
                </Link>
              )}
            </div>
          </div>

          {/* Stats Row */}
          {loadingStats ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
              {[1, 2, 3].map(i => (
                <div key={i} className="glass-card p-5 rounded-2xl border border-slate-200 bg-white/50 animate-pulse h-[116px]"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
              {[
                { label: 'Verified Placements', value: stats?.verified_placements ?? '—', icon: <Trophy className="w-5 h-5 text-amber-500" />, color: 'from-amber-50 to-yellow-50 border-amber-200' },
                { label: 'Average Salary', value: stats?.avg_salary_lpa ? `${Number(stats.avg_salary_lpa).toFixed(1)} LPA` : '—', icon: <IndianRupee className="w-5 h-5 text-emerald-500" />, color: 'from-emerald-50 to-teal-50 border-emerald-200' },
                { label: 'Top Company', value: stats?.top_company ?? '—', icon: <Building2 className="w-5 h-5 text-indigo-500" />, color: 'from-indigo-50 to-purple-50 border-indigo-200' },
              ].map(s => (
                <div key={s.label} className={`glass-card p-5 rounded-2xl border bg-gradient-to-br ${s.color} text-center shadow-sm`}>
                  <div className="flex justify-center mb-2">{s.icon}</div>
                  <div className="text-2xl font-extrabold text-slate-900">{s.value}</div>
                  <div className="text-xs font-medium text-slate-600 mt-1">{s.label}</div>
                </div>
              ))}
            </div>
          )}

          {/* Modules Grid */}
          <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-500" /> Your Tools
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-10">
            {MODULES.map(mod => (
              <Link key={mod.href} href={mod.href}
                className={`glass-card p-6 rounded-2xl border-2 ${mod.border} bg-gradient-to-br ${mod.bg} hover:shadow-md transition-all duration-200 group flex flex-col`}>
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${mod.color} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                  {mod.icon}
                </div>
                <h3 className="font-bold text-slate-900 text-lg mb-1">{mod.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed flex-1">{mod.desc}</p>
                <div className="flex items-center gap-1 mt-4 text-indigo-600 text-sm font-semibold">
                  Open <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>

          {/* Quick Links */}
          <div className="flex flex-wrap gap-3">
            <Link href="/placements/leaderboard" className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:border-indigo-300 hover:text-indigo-600 transition-all">
              <TrendingUp className="w-4 h-4" /> Placement Leaderboard
            </Link>
            <Link href="/prep/study-plan" className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:border-indigo-300 hover:text-indigo-600 transition-all">
              <Target className="w-4 h-4" /> Generate Study Plan
            </Link>
            <Link href="/questions" className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:border-indigo-300 hover:text-indigo-600 transition-all">
              <BookOpen className="w-4 h-4" /> Browse Questions
            </Link>
          </div>
        </div>
      </div>

      <PlacementLogModal isOpen={placementModalOpen} onClose={() => setPlacementModalOpen(false)} />
    </>
  );
}
