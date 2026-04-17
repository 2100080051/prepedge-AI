import Head from 'next/head';
import Link from 'next/link';
import { Shield, CheckCircle2, BookOpen, Activity, Users, BarChart, TrendingUp, ChevronRight } from 'lucide-react';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

const ADMIN_MODULES = [
  {
    href: '/admin/placements',
    icon: <CheckCircle2 className="w-7 h-7 text-emerald-500" />,
    title: 'Placement Verification',
    description: 'Review, verify, or reject student placement submissions. View students\' offer details and salary info.',
    color: 'border-emerald-200 hover:border-emerald-400',
    badge: 'Core',
    badgeColor: 'bg-emerald-50 text-emerald-700',
  },
  {
    href: '/admin/questions',
    icon: <BookOpen className="w-7 h-7 text-indigo-500" />,
    title: 'Question Verification',
    description: 'Moderate community-submitted interview questions. Edit, approve or reject from the verification queue.',
    color: 'border-indigo-200 hover:border-indigo-400',
    badge: 'Queue',
    badgeColor: 'bg-indigo-50 text-indigo-700',
  },
  {
    href: '/placements/leaderboard',
    icon: <TrendingUp className="w-7 h-7 text-amber-500" />,
    title: 'Public Leaderboard',
    description: 'View the placement leaderboard as students see it. Track verified placements and rankings.',
    color: 'border-amber-200 hover:border-amber-400',
    badge: 'Public',
    badgeColor: 'bg-amber-50 text-amber-700',
  },
];

export default function AdminDashboard() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) router.push('/auth/login');
  }, [isAuthenticated]);

  return (
    <>
      <Head><title>Admin Dashboard — PrepEdge AI</title></Head>
      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mb-12">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-purple-600 p-2.5 rounded-xl shadow-sm"><Shield className="w-6 h-6 text-white" /></div>
              <h1 className="text-3xl font-heading font-extrabold text-slate-900">Admin Dashboard</h1>
            </div>
            <p className="text-slate-500">Manage platform content, verify placements and questions. Welcome, {user?.full_name || 'Admin'}.</p>
          </div>

          <div className="grid gap-5">
            {ADMIN_MODULES.map(mod => (
              <Link key={mod.href} href={mod.href}
                className={`glass-card p-6 rounded-2xl border-2 bg-white transition-all duration-200 hover:shadow-md flex items-center gap-5 group ${mod.color}`}>
                <div className="w-14 h-14 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0">
                  {mod.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h2 className="text-lg font-bold text-slate-900">{mod.title}</h2>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${mod.badgeColor}`}>{mod.badge}</span>
                  </div>
                  <p className="text-sm text-slate-500 leading-relaxed">{mod.description}</p>
                </div>
                <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-slate-500 flex-shrink-0 transition-colors" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
