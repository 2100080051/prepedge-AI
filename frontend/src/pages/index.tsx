import Head from 'next/head';
import Link from 'next/link';
import { Sparkles, Brain, FileText, Mic, ArrowRight, CheckCircle2, Trophy, TrendingUp, Building2, IndianRupee, Plus } from 'lucide-react';
import FeatureCard from '../components/FeatureCard';
import PlacementLogModal from '../components/PlacementLogModal';
import { useState, useEffect, useRef } from 'react';
import { placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

function AnimatedCounter({ target, duration = 1800 }: { target: number; duration?: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef<NodeJS.Timeout>();
  useEffect(() => {
    const step = target / (duration / 16);
    let current = 0;
    ref.current = setInterval(() => {
      current += step;
      if (current >= target) { setCount(target); clearInterval(ref.current); }
      else { setCount(Math.floor(current)); }
    }, 16);
    return () => clearInterval(ref.current);
  }, [target]);
  return <>{count}</>;
}

export default function Home() {
  const [modalOpen, setModalOpen] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const loadStats = async () => {
    try { const res = await placementsApi.getStats(); setStats(res.data); }
    catch (e) {}
  };

  useEffect(() => {
    loadStats();
    const t = setInterval(loadStats, 60000);
    return () => clearInterval(t);
  }, []);

  return (
    <>
      <Head>
        <title>PrepEdge AI - India's Premier AI Placement Platform</title>
        <meta name="description" content="Master interviews, optimize resumes, and ace your placement prep with AI-powered tools." />
      </Head>

      <div className="relative overflow-hidden bg-slate-50">
        {/* Decorative Background */}
        <div className="absolute top-0 left-1/2 -ml-[39rem] w-[81.25rem] max-w-none opacity-40 mix-blend-multiply pointer-events-none" aria-hidden="true">
          <svg viewBox="0 0 1300 1300" className="w-[81.25rem] h-[81.25rem]">
            <defs><radialGradient id="grad1" cx="50%" cy="50%" r="50%" fx="50%" fy="50%"><stop offset="0%" stopColor="#4f46e5" stopOpacity="0.4" /><stop offset="100%" stopColor="#e0e7ff" stopOpacity="0" /></radialGradient></defs>
            <circle cx="650" cy="650" r="650" fill="url(#grad1)" />
          </svg>
        </div>
        <div className="absolute -top-32 right-0 w-[50rem] max-w-none opacity-40 mix-blend-multiply pointer-events-none" aria-hidden="true">
          <svg viewBox="0 0 800 800" className="w-[50rem] h-[50rem] animate-pulse-slow">
            <defs><radialGradient id="grad2" cx="50%" cy="50%" r="50%" fx="50%" fy="50%"><stop offset="0%" stopColor="#ec4899" stopOpacity="0.3" /><stop offset="100%" stopColor="#fdf2f8" stopOpacity="0" /></radialGradient></defs>
            <circle cx="400" cy="400" r="400" fill="url(#grad2)" />
          </svg>
        </div>

        {/* Hero */}
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-32 sm:pb-32 lg:pb-40">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 border border-indigo-200 animate-float">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-900">Platform Beta Now Live for 2024 Placements</span>
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-heading font-extrabold tracking-tight text-slate-900 mb-8 leading-tight">
              Unlock Your Dream Job with <span className="text-gradient">PrepEdge AI</span>
            </h1>
            <p className="text-xl sm:text-2xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
              The all-in-one AI platform engineered specifically for Indian engineering students to ace top-tier technical and HR interviews.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 sm:gap-6 mb-16">
              <Link href={mounted && isAuthenticated ? '/dashboard' : '/auth/register'} className="inline-flex justify-center items-center gap-2 px-8 py-4 rounded-full text-lg font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 hover:shadow-glow transition-all duration-300 transform hover:-translate-y-1">
                {mounted && isAuthenticated ? 'Go to Dashboard' : 'Start For Free'} <ArrowRight className="w-5 h-5" />
              </Link>
              <button onClick={() => setModalOpen(true)} className="inline-flex justify-center items-center gap-2 px-8 py-4 rounded-full text-lg font-medium text-slate-700 glass border-slate-200 hover:bg-white hover:text-indigo-600 transition-all duration-300">
                <Plus className="w-5 h-5" /> Log Your Placement
              </button>
            </div>
            <div className="flex flex-wrap justify-center items-center gap-x-8 gap-y-4 text-sm font-medium text-slate-500">
              <div className="flex items-center gap-2"><CheckCircle2 className="w-5 h-5 text-emerald-500" />No credit card required</div>
              <div className="flex items-center gap-2"><CheckCircle2 className="w-5 h-5 text-emerald-500" />TCS, Infosys, Wipro prep</div>
              <div className="flex items-center gap-2"><CheckCircle2 className="w-5 h-5 text-emerald-500" />Real-time AI feedback</div>
            </div>
          </div>
        </div>

        {/* Placement Stats Banner */}
        <div className="relative bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-700 py-16">
          <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Trophy className="w-7 h-7 text-amber-300" />
              <h2 className="text-3xl font-heading font-extrabold text-white">Students Getting Placed</h2>
            </div>
            <p className="text-indigo-200 mb-10 text-lg">Real verified placements from our community — updated live.</p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl mx-auto mb-10">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <div className="flex justify-center mb-3"><Trophy className="w-8 h-8 text-amber-300" /></div>
                <div className="text-4xl font-extrabold text-white mb-2">
                  <AnimatedCounter target={stats?.verified_placements ?? 0} />
                </div>
                <div className="text-indigo-200 font-medium text-sm">Students Placed</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <div className="flex justify-center mb-3"><IndianRupee className="w-8 h-8 text-emerald-300" /></div>
                <div className="text-4xl font-extrabold text-white mb-2">
                  {stats?.avg_salary_lpa ? `${Number(stats.avg_salary_lpa).toFixed(1)} LPA` : '—'}
                </div>
                <div className="text-indigo-200 font-medium text-sm">Average Salary</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <div className="flex justify-center mb-3"><Building2 className="w-8 h-8 text-cyan-300" /></div>
                <div className="text-4xl font-extrabold text-white mb-2">{stats?.top_company ?? '—'}</div>
                <div className="text-indigo-200 font-medium text-sm">Top Company</div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button onClick={() => setModalOpen(true)}
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-700 font-bold rounded-full hover:bg-indigo-50 transition-all shadow-lg text-base">
                <Plus className="w-5 h-5" />Log Your Placement
              </button>
              <Link href="/placements/leaderboard"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 text-white font-semibold rounded-full border border-white/30 hover:bg-white/20 transition-all text-base">
                <TrendingUp className="w-5 h-5" />View Leaderboard
              </Link>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="relative bg-white pt-24 pb-32 border-t border-slate-100">
          <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent" />
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-20">
              <h2 className="text-base text-indigo-600 font-semibold tracking-wide uppercase mb-3">AI Powered Toolkit</h2>
              <p className="text-4xl font-heading font-bold text-slate-900 mb-6">Master every step of your placement.</p>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                Stop using generic practice materials. PrepEdge AI adapts to your weaknesses and simulates real interview scenarios.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              <FeatureCard icon={<Brain className="w-7 h-7" />} title="LearnAI Hub" description="Master any concept across Engineering, Business, Science, and more. AI-generated lessons with real-world analogies in your native language." href="/learnai" ctaText="Start Learning" delay={0} gradient="from-indigo-500 to-purple-600" stats="100+ subjects · PDF summarizer" />
              <FeatureCard icon={<FileText className="w-7 h-7" />} title="ResumeAI" description="Upload your resume and get instant, actionable feedback to bypass ATS filters and catch recruiters' attention." href="/resumeai" ctaText="Analyze Resume" delay={100} gradient="from-emerald-500 to-teal-600" stats="ATS optimized · Domain-agnostic" />
              <FeatureCard icon={<Mic className="w-7 h-7" />} title="MockMate" description="Practice with highly realistic AI interviewers tailored to specific companies like TCS, Infosys, Wipro, and Accenture." href="/mockmate" ctaText="Start Interview" delay={200} gradient="from-rose-500 to-pink-600" stats="AI proctored · Anti-cheat" />
            </div>
          </div>
        </div>
      </div>

      <PlacementLogModal isOpen={modalOpen} onClose={() => setModalOpen(false)} onSuccess={loadStats} />
    </>
  );
}
