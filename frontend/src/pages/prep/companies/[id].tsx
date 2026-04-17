import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, Clock, Search, Target, Briefcase, GraduationCap, CheckCircle } from 'lucide-react';

const COMPANY_DATA: any = {
  'TCS': {
    name: 'Tata Consultancy Services (TCS)',
    type: 'Service Based',
    roles: ['Ninja (3.36 LPA)', 'Digital (7.0 LPA)', 'Prime (9.0-11.5 LPA)'],
    rounds: [
      {
        title: 'Cognitive & Technical Assessment (NQT)',
        desc: 'A comprehensive online test covering Numerical Ability, Verbal Ability, Reasoning Ability, and Programming Logic. For Digital/Prime, advanced coding questions are included.',
        duration: '120-180 Mins'
      },
      {
        title: 'Technical Interview',
        desc: 'Focuses heavily on your resume, final year project, basic DSA, OOPs concepts, SQL queries, and core CS fundamentals (OS, CN, DBMS).',
        duration: '45-60 Mins'
      },
      {
        title: 'Managerial & HR Interview',
        desc: 'Often combined into one phase. Focuses on situational questions, adaptability, willingness to relocate, bond agreements, and night shifts.',
        duration: '15-30 Mins'
      }
    ],
    proTip: "TCS places huge emphasis on your Final Year Project and basic OOPs. If you know core Java/C++ well, you can clear the Ninja profile easily."
  },
  'Amazon': {
    name: 'Amazon',
    type: 'Product Based',
    roles: ['SDE-1 (25-45 LPA)', 'Cloud Support (15-20 LPA)'],
    rounds: [
      {
        title: 'Online Assessment (OA)',
        desc: 'Usually 2 medium-hard LeetCode style questions (focus on Graphs, Trees, DP, Arrays) and a behavioral Amazon Leadership Principles assessment.',
        duration: '90 Mins'
      },
      {
        title: 'Technical Rounds (2-3x)',
        desc: 'Live coding on a shared editor. High emphasis on edge cases, time/space complexity, and clean code. Topics: Trees, Graphs, HashMaps, Sliding Window.',
        duration: '60 Mins Each'
      },
      {
        title: 'Bar Raiser / System Design',
        desc: 'Focuses on Object Oriented Design (LLD) or basic High-Level Design for freshers, heavily intertwined with Amazon Leadership Principles (e.g., "Tell me a time you disagreed with your manager").',
        duration: '60 Mins'
      }
    ],
    proTip: "You cannot pass Amazon without heavily studying their 16 Leadership Principles. The STAR method is mandatory for behavioral questions."
  }
};

export default function CompanyGuide() {
  const router = useRouter();
  const { id } = router.query;
  const company = id ? COMPANY_DATA[id as string] || COMPANY_DATA['TCS'] : COMPANY_DATA['TCS'];

  return (
    <>
      <Head>
        <title>{company.name} Interview Process — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <Link href="/prep/interview-tips" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-8">
            <ArrowLeft className="w-4 h-4" /> Back to Prep Base
          </Link>

          {/* Header */}
          <div className="glass-card bg-white rounded-3xl p-8 border border-slate-200 shadow-sm relative overflow-hidden mb-8">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-60"></div>
            
            <div className="relative z-10">
              <div className="flex flex-col sm:flex-row gap-6 sm:items-center">
                <div className="w-24 h-24 bg-gradient-to-br from-slate-100 to-slate-200 border-2 border-white shadow-md rounded-2xl flex items-center justify-center text-4xl font-black text-slate-800 flex-shrink-0">
                  {company.name.charAt(0)}
                </div>
                <div>
                  <div className="flex gap-2 mb-2">
                    <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-lg border border-indigo-200 uppercase tracking-wide">
                      {company.type}
                    </span>
                  </div>
                  <h1 className="text-3xl font-heading font-extrabold text-slate-900 mb-2">{company.name}</h1>
                  <p className="text-slate-600 flex items-center gap-2">
                    <GraduationCap className="w-4 h-4" /> Comprehensive Campus Hiring Guide
                  </p>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-slate-100">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3">Target Roles</h3>
                <div className="flex flex-wrap gap-2">
                  {company.roles.map((r: string) => (
                    <span key={r} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-700 font-semibold text-sm rounded-xl border border-slate-200">
                      <Briefcase className="w-4 h-4 text-indigo-500" /> {r}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Core Content */}
          <div className="glass-card bg-white rounded-3xl p-8 border border-slate-200 shadow-sm mb-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-8 flex items-center gap-3">
              <Target className="w-6 h-6 text-indigo-500" /> Hiring Process Timeline
            </h2>

            <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
              {company.rounds.map((round: any, idx: number) => (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-indigo-500 text-white font-bold shadow-sm shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-transform group-hover:scale-110">
                    {idx + 1}
                  </div>
                  
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-slate-50 border border-slate-100 rounded-2xl p-6 shadow-sm group-hover:bg-white group-hover:border-indigo-100 group-hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-slate-900 text-lg">{round.title}</h3>
                    </div>
                    <p className="text-slate-600 text-sm leading-relaxed mb-4">{round.desc}</p>
                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-md text-xs font-semibold text-slate-500">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" /> {round.duration}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pro Tip */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-8 text-white shadow-md relative overflow-hidden">
            <div className="absolute right-0 bottom-0 opacity-10 transform translate-x-1/4 translate-y-1/4">
              <Target className="w-48 h-48" />
            </div>
            <div className="relative z-10">
              <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-indigo-200" /> Insider Pro-Tip
              </h3>
              <p className="text-indigo-50 leading-relaxed max-w-2xl font-medium">
                {company.proTip}
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <Link href={`/questions/company/${company.name.split(' ')[0]}`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 text-indigo-600 font-bold rounded-xl hover:bg-slate-50 transition-colors shadow-sm">
              <Search className="w-4 h-4" /> View {company.name.split(' ')[0]} Question Bank
            </Link>
          </div>

        </div>
      </div>
    </>
  );
}
