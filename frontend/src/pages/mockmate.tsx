import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { 
  Building2, Briefcase, Play, Send, Bot, User as UserIcon, 
  CheckCircle2, XCircle, Lightbulb, TrendingUp, Award, 
  Target, GraduationCap, MessageSquare, Lock, AlertTriangle
} from 'lucide-react';
import { mockMateApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import ProctoringMonitor from '@/components/ProctoringMonitor';
import ProctoringReportModal from '@/components/ProctoringReportModal';

// Helper: clean up raw AI response that may be JSON-encoded
function parseAIMessage(raw: string): string {
  if (!raw) return '';
  const trimmed = raw.trim();
  // Detect if the response is a JSON string or wrapped in code fences
  let jsonCandidate = trimmed;
  // Strip markdown code fences  ```json ... ```
  if (jsonCandidate.startsWith('```')) {
    jsonCandidate = jsonCandidate.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '').trim();
  }
  try {
    const parsed = JSON.parse(jsonCandidate);
    if (typeof parsed === 'object' && parsed !== null) {
      // Extract the question text from a structured JSON response
      const question = parsed.question || parsed.text || parsed.content || parsed.message;
      if (question) {
        let result = question;
        // Optionally append hints
        if (Array.isArray(parsed.hints) && parsed.hints.length) {
          result += '\n\n💡 Hints:\n' + parsed.hints.map((h: string, i: number) => `${i + 1}. ${h}`).join('\n');
        }
        return result;
      }
      // If no known key, stringify nicely
      return question || JSON.stringify(parsed, null, 2);
    }
  } catch {
    // Not JSON — return as-is
  }
  return raw;
}

type Message = {
  role: 'assistant' | 'user';
  content: string;
};

type Coaching = {
  what_was_good: string;
  what_was_missing: string;
  how_to_improve: string;
  score: number;
};

type FinalReport = {
  overall_score: number;
  communication_score: number;
  technical_depth_score: number;
  confidence_score: number;
  strengths: string[];
  areas_to_improve: string[];
  top_3_topics_to_study: string[];
  hiring_verdict: string;
  personalized_message: string;
  next_steps: string;
};

export default function MockMate() {
  // Setup State
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  
  // Chat State
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Feedback State
  const [lastCoaching, setLastCoaching] = useState<Coaching | null>(null);
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);
  
  // Proctoring State
  const [showProctoringMonitor, setShowProctoringMonitor] = useState(false);
  const [showProctoringReport, setShowProctoringReport] = useState(false);
  const [proctoringFlagged, setProctoringFlagged] = useState(false);
  const [proctoringFlagReason, setProctoringFlagReason] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const COMPANIES = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Cognizant'];
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  // Auth guard - redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated]);

  // Scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!company || !role.trim()) return;

    setLoading(true);
    try {
      const res = await mockMateApi.startInterview(company, role);
      
      // Validate response
      if (!res.data || !res.data.session_id) {
        throw new Error('Failed to initialize interview session.');
      }
      
      setSessionId(res.data.session_id);
      // Backend returns 'first_message' key for the opening question
      const rawMsg = res.data.first_message || res.data.response || res.data.message || 'Hello! I am your AI interviewer. Let us begin.';
      setMessages([{ role: 'assistant', content: parseAIMessage(rawMsg) }]);
      setSessionActive(true);
      
      // Start proctoring for this session
      setShowProctoringMonitor(true);
    } catch (err: any) {
      // Specific error handling
      if (err.response?.status === 429) {
        alert('Too many requests. Please wait a moment and try again.');
      } else if (err.response?.status === 503) {
        alert('AI service is temporarily unavailable. Please try again in a moment.');
      } else {
        alert(err.response?.data?.detail || err.message || 'Failed to start interview. Please ensure you are logged in.');
      }
      console.error('Interview start error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !sessionId || loading) return;

    const userMsg = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await mockMateApi.submitAnswer(sessionId, userMsg);
      
      // Validate response
      if (!res.data) {
        throw new Error('No response received from AI interviewer.');
      }
      
      const data = res.data;
      
      // Validate response content
      if (!data.response || data.response.trim().length === 0) {
        throw new Error('Received empty response from interviewer.');
      }

      setLastCoaching(data.coaching);
      setMessages(prev => [...prev, { role: 'assistant', content: parseAIMessage(data.response) }]);

      if (data.is_complete && data.final_report) {
        setFinalReport(data.final_report);
      }
    } catch (err: any) {
      // Enhanced error handling
      let errorMsg = "Sorry, I had trouble processing that. Could you try answering again?";
      
      if (err.response?.status === 429) {
        errorMsg = "Rate limited. Please wait a moment before continuing.";
      } else if (err.response?.status === 503) {
        errorMsg = "AI service temporarily unavailable. Please retry your answer.";
      } else if (err.message?.includes('empty')) {
        errorMsg = "Couldn't understand that response. Please provide more details.";
      }
      
      setMessages(prev => [...prev, { role: 'assistant', content: errorMsg }]);
      console.error('Message submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFlagSession = (reason: string) => {
    setProctoringFlagged(true);
    setProctoringFlagReason(reason);
    setShowProctoringMonitor(false);
    setSessionActive(false);
  };

  const handleEndSession = async () => {
    if (!sessionId) return;
    
    try {
      // Close proctoring and show report
      setShowProctoringMonitor(false);
      setShowProctoringReport(true);
    } catch (err) {
      console.error('Error ending session:', err);
    }
  };

  // 1. SETUP UI
  if (!sessionActive) {
    return (
      <div className="min-h-screen bg-slate-50 pt-32 pb-12 flex items-center justify-center">
        <Head><title>MockMate - AI Interviews</title></Head>
        <div className="max-w-md w-full px-4">
          <div className="glass-card p-8 rounded-3xl border border-slate-200">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/20">
              <Bot className="w-8 h-8 text-white" />
            </div>
            
            <h1 className="text-3xl font-heading font-extrabold text-slate-900 mb-2">
              MockMate
            </h1>
            <p className="text-slate-600 mb-8">
              Configure your AI interviewer. We'll tailor the questions to this exact company and role.
            </p>

            <form onSubmit={handleStart} className="space-y-5">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-slate-400" /> Target Company
                </label>
                <select
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                >
                  <option value="">Select a company...</option>
                  {COMPANIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-slate-400" /> Target Role
                </label>
                <input
                  type="text"
                  value={role}
                  onChange={e => setRole(e.target.value)}
                  required
                  placeholder="e.g. Software Engineer, Data Analyst"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !company || !role.trim()}
                className="w-full py-4 px-4 bg-slate-900 text-white font-semibold rounded-xl hover:bg-indigo-600 disabled:opacity-50 transition-all duration-300 flex items-center justify-center gap-2 mt-4"
              >
                {loading ? "Warming up AI..." : "Start Interview"} <Play className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // 2. FINAL REPORT UI
  if (finalReport) {
    return (
      <div className="min-h-screen bg-slate-50 pt-24 pb-24">
        <Head><title>Interview Report - MockMate</title></Head>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center mb-12">
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Interview Final Report
            </h1>
            <p className="text-lg text-slate-600">Company: {company} • Role: {role}</p>
          </div>

          <div className="space-y-6">
            
            {/* Top Scores */}
            <div className="glass-card p-8 rounded-2xl border border-slate-200 shadow-sm bg-white relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 opacity-50 rounded-bl-full" />
              <div className="relative z-10 flex flex-col md:flex-row items-center gap-8 justify-between">
                <div className="flex-1">
                  <span className={`inline-flex items-center gap-1 px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider mb-4 ${
                    finalReport.hiring_verdict.includes("Strong") ? "bg-emerald-100 text-emerald-700" :
                    finalReport.hiring_verdict.includes("Hire") ? "bg-indigo-100 text-indigo-700" :
                    "bg-amber-100 text-amber-700"
                  }`}>
                    Verdict: {finalReport.hiring_verdict}
                  </span>
                  <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl italic text-slate-700">
                    "{finalReport.personalized_message}"
                  </div>
                </div>
                
                <div className="flex gap-4">
                   <div className="text-center p-5 bg-indigo-50 rounded-2xl border border-indigo-100">
                     <p className="text-4xl font-black text-indigo-600">{finalReport.overall_score}<span className="text-xl text-indigo-300">/10</span></p>
                     <p className="text-xs font-bold text-indigo-900/60 uppercase tracking-wide mt-2">Overall Score</p>
                   </div>
                </div>
              </div>
            </div>

            {/* Sub-scores Grid */}
            <div className="grid grid-cols-3 gap-6">
               <div className="glass-card p-6 rounded-2xl border border-slate-100 text-center bg-white">
                 <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Communication</p>
                 <p className="text-3xl font-bold text-slate-800">{finalReport.communication_score}/10</p>
               </div>
               <div className="glass-card p-6 rounded-2xl border border-slate-100 text-center bg-white">
                 <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Technical Depth</p>
                 <p className="text-3xl font-bold text-slate-800">{finalReport.technical_depth_score}/10</p>
               </div>
               <div className="glass-card p-6 rounded-2xl border border-slate-100 text-center bg-white">
                 <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Confidence</p>
                 <p className="text-3xl font-bold text-slate-800">{finalReport.confidence_score}/10</p>
               </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="glass-card p-6 rounded-2xl border border-emerald-100 bg-white/60">
                <h3 className="text-lg font-bold text-emerald-900 mb-4 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" /> Great Job On
                </h3>
                <ul className="space-y-3">
                  {finalReport.strengths.map((s, i) => (
                    <li key={i} className="flex gap-3 text-slate-700"><span className="text-emerald-500">•</span>{s}</li>
                  ))}
                </ul>
              </div>
              <div className="glass-card p-6 rounded-2xl border border-amber-100 bg-white/60">
                <h3 className="text-lg font-bold text-amber-900 mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-amber-500" /> Areas to Focus
                </h3>
                <ul className="space-y-3">
                  {finalReport.areas_to_improve.map((s, i) => (
                    <li key={i} className="flex gap-3 text-slate-700"><span className="text-amber-500">•</span>{s}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Next Steps */}
            <div className="glass-card p-8 rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-900 to-slate-900 text-white">
               <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                  <TrendingUp className="w-6 h-6 text-indigo-400" /> Action Plan
               </h3>
               <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <p className="font-semibold text-indigo-300 uppercase tracking-widest text-xs mb-4">Topics to Master</p>
                    <ul className="space-y-2">
                       {finalReport.top_3_topics_to_study.map((t, i) => (
                         <li key={i} className="flex items-center gap-3 font-medium bg-white/10 px-4 py-2 rounded-lg">
                           <GraduationCap className="w-4 h-4 text-indigo-300" /> {t}
                         </li>
                       ))}
                    </ul>
                  </div>
                  <div>
                    <p className="font-semibold text-indigo-300 uppercase tracking-widest text-xs mb-4">Your Next 2 Weeks</p>
                    <p className="text-indigo-50 leading-relaxed font-medium">
                      {finalReport.next_steps}
                    </p>
                  </div>
               </div>
            </div>

            <div className="text-center mt-8">
              <button 
                onClick={() => window.location.reload()}
                className="px-8 py-3 bg-white border border-slate-200 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                Start Another Interview
              </button>
            </div>

          </div>
        </div>
      </div>
    );
  }

  // 3. INTERVIEW CHAT UI
  return (
    <>
      <Head><title>Live Interview - MockMate</title></Head>
      <div className="min-h-screen bg-slate-50 flex flex-col pt-16">
        
        {/* Header Bar */}
        <div className="glass border-b border-slate-200 bg-white/80 sticky top-16 z-30">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-bold shadow-inner">
                {company[0]}
              </div>
              <div>
                <p className="font-semibold text-slate-900">{company} Interview</p>
                <p className="text-xs text-slate-500">{role}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 max-w-6xl mx-auto w-full p-4 flex flex-col lg:flex-row gap-6 relative">
          
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col glass-card rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm h-[calc(100vh-140px)]">
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
                    msg.role === 'user' ? 'bg-slate-100 text-slate-600' : 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
                  }`}>
                    {msg.role === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`px-5 py-3.5 rounded-2xl max-w-[80%] ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-sm' 
                      : 'bg-slate-100 text-slate-800 rounded-tl-sm'
                  }`}>
                    <p className="leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="px-5 py-4 rounded-2xl bg-slate-100 rounded-tl-sm flex gap-1 items-center">
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-slate-100">
              <form onSubmit={handleSendMessage} className="relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  placeholder="Type your answer..."
                  disabled={loading}
                  className="w-full pl-5 pr-14 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || loading}
                  className="absolute right-2 top-2 bottom-2 w-10 flex items-center justify-center bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>

          {/* Side Panel: Live Coaching Feedback */}
          <div className="lg:w-96 flex-shrink-0 hidden lg:block">
            <div className="sticky top-40 space-y-4">
              <div className="flex items-center gap-2 mb-2 px-2">
                <MessageSquare className="w-5 h-5 text-slate-400" />
                <h3 className="font-semibold text-slate-700">Live AI Coach</h3>
              </div>
              
              {!lastCoaching ? (
                <div className="glass-card border border-slate-200 border-dashed rounded-2xl p-6 text-center text-slate-500">
                   <Lightbulb className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                   <p className="text-sm">Submit your first answer to get real-time coaching feedback.</p>
                </div>
              ) : (
                <div className="space-y-4 animate-fade-in">
                  <div className="glass-card p-5 rounded-2xl border border-indigo-100 shadow-sm bg-white">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Last Answer Rating</span>
                      <span className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-700 flex items-center justify-center font-bold text-sm">
                        {lastCoaching.score}
                      </span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <p className="flex items-center gap-2 text-sm font-semibold text-emerald-700 mb-1">
                          <CheckCircle2 className="w-4 h-4" /> What was good
                        </p>
                        <p className="text-sm text-slate-600">{lastCoaching.what_was_good}</p>
                      </div>
                      <div>
                        <p className="flex items-center gap-2 text-sm font-semibold text-rose-700 mb-1">
                          <XCircle className="w-4 h-4" /> What was missing
                        </p>
                        <p className="text-sm text-slate-600">{lastCoaching.what_was_missing}</p>
                      </div>
                      <div className="pt-3 mt-3 border-t border-slate-100">
                        <p className="flex items-center gap-2 text-sm font-semibold text-indigo-700 mb-1">
                          <Lightbulb className="w-4 h-4" /> Tip for next time
                        </p>
                        <p className="text-sm text-slate-600 font-medium">{lastCoaching.how_to_improve}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
        </div>

        {/* Proctoring Monitor floating widget */}
        {sessionActive && showProctoringMonitor && sessionId && !finalReport && (
          <ProctoringMonitor
            sessionId={sessionId}
            isActive={sessionActive && !finalReport}
            onFlagSession={handleFlagSession}
          />
        )}

      </div>

      {/* Proctoring Report Modal */}
      {showProctoringReport && sessionId && (
        <ProctoringReportModal
          sessionId={sessionId}
          onClose={() => setShowProctoringReport(false)}
        />
      )}
    </>
  );
}
