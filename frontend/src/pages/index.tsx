import Head from 'next/head';
import Image from 'next/image';
import Link from 'next/link';
import { Sparkles, Brain, FileText, Mic, ArrowRight, CheckCircle2 } from 'lucide-react';
import FeatureCard from '../components/FeatureCard';

export default function Home() {
  return (
    <>
      <Head>
        <title>PrepEdge AI - India's Premier AI Placement Platform</title>
        <meta name="description" content="Master interviews, optimize resumes, and ace your placement prep with AI-powered tools." />
      </Head>

      <div className="relative overflow-hidden bg-slate-50">
        {/* Decorative Background Elements */}
        <div className="absolute top-0 left-1/2 -ml-[39rem] w-[81.25rem] max-w-none opacity-40 mix-blend-multiply pointer-events-none" aria-hidden="true">
          <svg viewBox="0 0 1300 1300" className="w-[81.25rem] h-[81.25rem]">
            <defs>
              <radialGradient id="grad1" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#e0e7ff" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="650" cy="650" r="650" fill="url(#grad1)" />
          </svg>
        </div>
        <div className="absolute -top-32 right-0 w-[50rem] max-w-none opacity-40 mix-blend-multiply pointer-events-none" aria-hidden="true">
          <svg viewBox="0 0 800 800" className="w-[50rem] h-[50rem] animate-pulse-slow">
            <defs>
              <radialGradient id="grad2" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                <stop offset="0%" stopColor="#ec4899" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fdf2f8" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="400" cy="400" r="400" fill="url(#grad2)" />
          </svg>
        </div>

        {/* Hero Section */}
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
              <Link 
                href="/auth/register" 
                className="inline-flex justify-center items-center gap-2 px-8 py-4 rounded-full text-lg font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 hover:shadow-glow transition-all duration-300 transform hover:-translate-y-1"
              >
                Start For Free
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                href="/demo" 
                className="inline-flex justify-center items-center gap-2 px-8 py-4 rounded-full text-lg font-medium text-slate-700 glass border-slate-200 hover:bg-white hover:text-indigo-600 transition-all duration-300"
              >
                View Demo
              </Link>
            </div>

            <div className="flex flex-wrap justify-center items-center gap-x-8 gap-y-4 text-sm font-medium text-slate-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                No credit card required
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                TCS, Infosys, Wipro prep
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                Real-time AI feedback
              </div>
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
            
            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard 
                icon={<Brain className="w-8 h-8" />}
                title="LearnAI Hub"
                description="Master any concept across Engineering, Business, Science, and more. AI-generated lessons, real-world analogies, and explanatory visuals in your native language."
                href="/learnai"
                ctaText="Start Learning"
                delay={0}
              />
              <FeatureCard 
                icon={<FileText className="w-8 h-8" />}
                title="ResumeAI"
                description="Upload your resume and get instant, actionable feedback to bypass ATS filters and catch recruiters' attention."
                href="/resumeai"
                ctaText="Analyze Resume"
                delay={150}
              />
              <FeatureCard 
                icon={<Mic className="w-8 h-8" />}
                title="MockMate"
                description="Practice with highly realistic AI interviewers tailored to specific companies like TCS, Infosys, Wipro, and Accenture."
                href="/mockmate"
                ctaText="Start Interview"
                delay={300}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
