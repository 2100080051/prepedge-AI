import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Lightbulb, Code2, Users, Target, BookOpen, CheckCircle, ArrowRight } from 'lucide-react';

const CATEGORIES = [
  { id: 'technical', label: 'Technical Round', icon: <Code2 className="w-5 h-5" /> },
  { id: 'hr', label: 'HR Round', icon: <Users className="w-5 h-5" /> },
  { id: 'behavioral', label: 'Behavioral', icon: <Target className="w-5 h-5" /> },
  { id: 'gd', label: 'Group Discussion', icon: <Lightbulb className="w-5 h-5" /> },
];

const CONTENT = {
  technical: {
    title: "Acing the Technical Interview",
    description: "The technical round is where your core engineering skills are tested. It focuses on Data Structures, Algorithms, Core CS Subjects, and your domain knowledge.",
    tips: [
      {
        title: "Master DSA Patterns, Not Just Problems",
        text: "Instead of memorizing 500 LeetCode problems, study the 15 core patterns (Sliding Window, Two Pointers, BFS/DFS, etc.). If you know the pattern, you can solve any related question."
      },
      {
        title: "Think Out Loud",
        text: "The interviewer wants to see your thought process, not just the final compiled code. Talk through your brute force approach first, then explain how you plan to optimize it before writing any code."
      },
      {
        title: "Know Your Core CS Subjects",
        text: "For service-based and product-based companies alike, Operating Systems, DBMS (ACID properties, Normalization), and Computer Networks are just as important as coding."
      },
      {
        title: "Prepare Your Projects Recursively",
        text: "You should know every single technology used in your resume projects. Why did you use MongoDB instead of SQL? What was the hardest bug you fixed? Never put a tech stack on your resume you can't defend."
      }
    ]
  },
  hr: {
    title: "Winning the HR Round",
    description: "The HR round is to check your cultural fit, communication skills, and verify your background. Don't take this round lightly; many students are rejected here.",
    tips: [
      {
        title: "Nail 'Tell Me About Yourself'",
        text: "Keep it under 90 seconds. Structure it as Present-Past-Future: What you're doing now (degree), what you did in the past (internships/projects), and what you want to do in the future (why you want this job)."
      },
      {
        title: "Research the Company",
        text: "Know the CEO, recent news acquisitions, their core products, and their mission statement. When asked 'Why us?', your answer should be specific to their recent work, not generic."
      },
      {
        title: "Have Questions Ready",
        text: "When they ask 'Do you have any questions for us?', always say yes. Ask about the team culture, what project you'd be working on, or their tech stack evolution."
      }
    ]
  },
  behavioral: {
    title: "Mastering Behavioral Questions",
    description: "Behavioral questions test how you react to stressful situations, team conflicts, and tight deadlines.",
    tips: [
      {
        title: "Use the STAR Method",
        text: "Always format your answers using Situation (context), Task (your responsibility), Action (what YOU did), and Result (quantifiable outcome)."
      },
      {
        title: "Prepare for 'Weakness' Questions",
        text: "Don't say 'I work too hard'. Pick a real weakness that isn't fatal to the job, and immediately follow up with the actionable steps you are taking to fix it."
      },
      {
        title: "Highlight Teamwork",
        text: "Most software engineering is collaborative. Even if you coded the whole project yourself, highlight instances where you gathered feedback, delegated, or helped a peer."
      }
    ]
  },
  gd: {
    title: "Dominating Group Discussions",
    description: "GDs are used as an elimination round when there are too many candidates. It tests leadership, listening, and articulation.",
    tips: [
      {
        title: "Initiate if Confident, Conclude if Not",
        text: "Starting the GD gives you bonus points, but only if you have a valid point. If you don't know the topic, listen for 2 minutes and then summarize what others have said to enter the discussion."
      },
      {
        title: "Don't Be Aggressive",
        text: "It is a discussion, not a debate. Instead of shouting down someone, say 'I partially agree with my friend here, but I'd like to add...'"
      },
      {
        title: "Use Facts and Data",
        text: "Statements backed by numbers or recent news always hold more weight than emotional opinions."
      }
    ]
  }
};

export default function InterviewTips() {
  const [activeTab, setActiveTab] = useState('technical');
  const activeData = CONTENT[activeTab as keyof typeof CONTENT];

  return (
    <>
      <Head>
        <title>Interview Tips & Strategies — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-6 tracking-tight leading-tight">
              Master the Interview with <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
                Actionable Strategies
              </span>
            </h1>
            <p className="text-lg text-slate-600">
              Read our curated guides to understanding exactly what recruiters are looking for across every stage of the placement process.
            </p>
          </div>

          <div className="flex flex-col md:flex-row gap-8">
            
            {/* Sidebar Navigation */}
            <div className="w-full md:w-64 flex-shrink-0">
              <div className="bg-white rounded-2xl border border-slate-200 p-2 shadow-sm sticky top-24">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveTab(cat.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left mb-1
                      ${activeTab === cat.id 
                        ? 'bg-indigo-50 text-indigo-700 shadow-sm border border-indigo-100' 
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 border border-transparent'}`}
                  >
                    <span className={`${activeTab === cat.id ? 'text-indigo-600' : 'text-slate-400'}`}>
                      {cat.icon}
                    </span>
                    {cat.label}
                  </button>
                ))}
                
                <div className="mt-6 pt-6 border-t border-slate-100 px-2">
                  <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-4 text-white relative overflow-hidden group hover:shadow-lg transition-all">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 opacity-30 group-hover:opacity-50 transition-opacity"></div>
                    <BookOpen className="w-6 h-6 text-indigo-300 mb-3" />
                    <h4 className="font-bold text-sm mb-1">Company Guides</h4>
                    <p className="text-xs text-slate-300 mb-3">View specific interview processes for top companies.</p>
                    <Link href="/questions/companies" className="flex items-center gap-1 text-xs font-bold text-indigo-300 hover:text-indigo-200 transition-colors">
                      View Hub <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1">
              <div className="glass-card bg-white rounded-3xl border border-slate-200 p-8 md:p-10 shadow-sm animate-fade-in relative overflow-hidden">
                {/* Decorative background blob */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 opacity-50 pointer-events-none"></div>

                <div className="relative z-10">
                  <h2 className="text-3xl font-bold text-slate-900 mb-4">{activeData.title}</h2>
                  <p className="text-slate-600 text-lg mb-10 leading-relaxed border-b border-slate-100 pb-8">
                    {activeData.description}
                  </p>

                  <div className="space-y-8">
                    {activeData.tips.map((tip, idx) => (
                      <div key={idx} className="flex gap-4 group">
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm border border-indigo-200 group-hover:scale-110 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300 shadow-sm">
                            {idx + 1}
                          </div>
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-indigo-600 transition-colors">
                            {tip.title}
                          </h3>
                          <p className="text-slate-600 leading-relaxed">
                            {tip.text}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </>
  );
}
