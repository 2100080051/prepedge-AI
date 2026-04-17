import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { ArrowLeft, BookOpen, Star, Code2, Users, Zap, Loader2, Eye, EyeOff, CheckCircle2, XCircle, ChevronRight, BarChart, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { questionsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import CodeEditor from '@/components/CodeEditor';
import AnswerDisplay from '@/components/questions/AnswerDisplay';
import PracticeSidebar from '@/components/questions/PracticeSidebar';

const DIFF_BADGE: Record<string, string> = {
  Easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Hard:   'bg-rose-100 text-rose-700 border-rose-200',
};

export default function QuestionPractice() {
  const router = useRouter();
  const { id } = router.query;
  const { isAuthenticated } = useAuthStore();

  const [question, setQuestion] = useState<any>(null);
  const [solution, setSolution] = useState<any>(null);
  const [similar, setSimilar] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [answer, setAnswer] = useState('');
  const [codeAnswer, setCodeAnswer] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python3');
  const [answerMode, setAnswerMode] = useState<'code' | 'text'>('code');
  const [showSolution, setShowSolution] = useState(false);
  const [submitted, setSubmitted] = useState<'correct' | 'incorrect' | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());
  const [timeSpent, setTimeSpent] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    if (!id) return;
    loadQuestion();
  }, [id, isAuthenticated]);

  useEffect(() => {
    if (submitted) return;
    const interval = setInterval(() => {
      setTimeSpent(Math.round((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime, submitted]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const loadQuestion = async () => {
    setLoading(true);
    setError('');
    try {
      const [qRes, simRes] = await Promise.allSettled([
        questionsApi.getById(Number(id)),
        questionsApi.getSimilar(Number(id)),
      ]);
      // Extract question data from API response
      if (qRes.status === 'fulfilled') {
        const questionData = qRes.value.data?.question || qRes.value.data;
        setQuestion(questionData);
      }
      // Extract similar questions
      if (simRes.status === 'fulfilled') {
        const similarData = Array.isArray(simRes.value.data) 
          ? simRes.value.data 
          : simRes.value.data?.questions || [];
        setSimilar(similarData);
      }
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load question.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewSolution = () => setShowSolution(!showSolution);

  const handleSubmit = async (isCorrect: boolean) => {
    setSubmitting(true);
    try {
      const finalAnswer = answerMode === 'code' ? codeAnswer : answer;
      await questionsApi.attempt(Number(id), finalAnswer, isCorrect);
    } catch (e) {}
    setSubmitted(isCorrect ? 'correct' : 'incorrect');
    setSubmitting(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.target as HTMLTextAreaElement;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      setAnswer(answer.substring(0, start) + '  ' + answer.substring(end));
      setTimeout(() => {
          target.selectionStart = target.selectionEnd = start + 2;
      }, 0);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-slate-50 pt-24 flex flex-col items-center justify-center">
      <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
      <p className="text-slate-500">Loading question...</p>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-slate-50 pt-24 flex flex-col items-center justify-center">
      <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
      <h2 className="text-xl font-bold text-slate-700 mb-2">Question Not Found</h2>
      <p className="text-slate-500 mb-6">{error}</p>
      <Link href="/questions" className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors">← Back to Question Bank</Link>
    </div>
  );

  return (
    <>
      <Head>
        <title>{question?.company || 'Question'} Practice — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Back + breadcrumb */}
          <div className="flex items-center gap-3 mb-8 text-sm">
            <Link href="/questions" className="flex items-center gap-1.5 text-slate-500 hover:text-indigo-600 font-medium transition-colors">
              <ArrowLeft className="w-4 h-4" /> Question Bank
            </Link>
            <span className="text-slate-300">/</span>
            <span className="text-slate-700 font-semibold">{question?.company_name || question?.company}</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-500">Practice</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Question Area */}
            <div className="lg:col-span-2 space-y-6">
              {/* Question Card */}
              <div className="glass-card p-8 rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-wrap items-center gap-2 mb-6">
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider">{question?.company_name || question?.company}</span>
                  <span className={`px-2.5 py-1 rounded-lg text-xs border font-semibold ${DIFF_BADGE[question?.difficulty] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>{question?.difficulty}</span>
                  <span className="px-2.5 py-1 bg-slate-100 text-slate-600 border border-slate-200 rounded-lg text-xs font-medium">{question?.round_type}</span>
                  {question?.topic && <span className="px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg text-xs border border-purple-100">{question?.topic}</span>}
                </div>
                <h1 className="text-2xl font-bold text-slate-900 leading-relaxed mb-4">{question?.question || question?.question_text}</h1>
                {question?.frequency_score && (
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <BarChart className="w-4 h-4" />
                    <span>Asked {question.frequency_score}/10 times — relatively {question.frequency_score >= 7 ? 'common' : 'uncommon'}</span>
                  </div>
                )}
              </div>

              {/* Answer Area */}
              {submitted ? (
                <div className={`p-6 rounded-2xl border-2 ${submitted === 'correct' ? 'bg-emerald-50 border-emerald-300' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-3 mb-3">
                    {submitted === 'correct' ? <CheckCircle2 className="w-8 h-8 text-emerald-500" /> : <XCircle className="w-8 h-8 text-red-400" />}
                    <div>
                      <h3 className="text-lg font-bold text-slate-900">{submitted === 'correct' ? '🎉 Correct! Great job!' : '🤔 Not quite — keep practicing!'}</h3>
                      <p className="text-sm text-slate-500">Time taken: {formatTime(timeSpent)}</p>
                    </div>
                  </div>
                  <div className="flex gap-3 mt-4">
                    <button onClick={handleViewSolution} className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold hover:bg-slate-50 transition-colors">
                      {showSolution ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      {showSolution ? 'Hide' : 'View'} Solution
                    </button>
                    <Link href="/questions" className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors">
                      Next Question <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              ) : (
                <>
                  {/* Answer Mode Tabs */}
                  <div className="glass-card rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                    <div className="flex border-b border-slate-200">
                      <button
                        onClick={() => setAnswerMode('code')}
                        className={`flex-1 py-4 px-6 font-semibold transition-all ${
                          answerMode === 'code'
                            ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        <Code2 className="w-4 h-4 inline mr-2" />
                        Code Editor
                      </button>
                      <button
                        onClick={() => setAnswerMode('text')}
                        className={`flex-1 py-4 px-6 font-semibold transition-all ${
                          answerMode === 'text'
                            ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        <BookOpen className="w-4 h-4 inline mr-2" />
                        Text Response
                      </button>
                    </div>

                    <div className="p-6">
                      {answerMode === 'code' ? (
                        <>
                          <h2 className="text-base font-bold text-slate-900 mb-4">Write Your Solution</h2>
                          <CodeEditor
                            initialCode={codeAnswer}
                            language={selectedLanguage}
                            onTest={(code, output) => setCodeAnswer(code)}
                            showPlayground={true}
                            isForProgrammingQuestion={true}
                          />
                          <div className="flex flex-col sm:flex-row gap-3 mt-6">
                            <button onClick={() => handleSubmit(true)} disabled={submitting || !codeAnswer.trim()}
                              className="flex-1 py-3 bg-emerald-500 text-white font-semibold rounded-xl hover:bg-emerald-600 disabled:opacity-40 transition-all flex items-center justify-center gap-2">
                              <CheckCircle2 className="w-5 h-5" />Submit Solution
                            </button>
                            <button onClick={() => handleSubmit(false)} disabled={submitting || !codeAnswer.trim()}
                              className="flex-1 py-3 bg-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-300 disabled:opacity-40 transition-all flex items-center justify-center gap-2">
                              <XCircle className="w-5 h-5" />Mark Unsure
                            </button>
                            <button onClick={handleViewSolution}
                              className="px-5 py-3 border border-slate-200 text-slate-600 font-semibold rounded-xl hover:bg-slate-50 transition-colors flex items-center gap-2">
                              {showSolution ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              {showSolution ? 'Hide' : 'View'} Solution
                            </button>
                          </div>
                        </>
                      ) : (
                        <>
                          <h2 className="text-base font-bold text-slate-900 mb-3">Your Answer / Approach</h2>
                          <textarea value={answer} onChange={e => setAnswer(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Type your answer, approach, or explanation here..."
                            spellCheck={false}
                            rows={12}
                            className="w-full p-5 bg-slate-900 text-slate-50 border border-slate-700 rounded-xl font-mono text-sm focus:ring-2 focus:ring-indigo-500/50 transition-all resize-y leading-relaxed" />
                          <div className="flex flex-col sm:flex-row gap-3 mt-4">
                            <button onClick={() => handleSubmit(true)} disabled={submitting || !answer.trim()}
                              className="flex-1 py-3 bg-emerald-500 text-white font-semibold rounded-xl hover:bg-emerald-600 disabled:opacity-40 transition-all flex items-center justify-center gap-2">
                              <CheckCircle2 className="w-5 h-5" />Mark Correct
                            </button>
                            <button onClick={() => handleSubmit(false)} disabled={submitting || !answer.trim()}
                              className="flex-1 py-3 bg-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-300 disabled:opacity-40 transition-all flex items-center justify-center gap-2">
                              <XCircle className="w-5 h-5" />Mark Incorrect
                            </button>
                            <button onClick={handleViewSolution}
                              className="px-5 py-3 border border-slate-200 text-slate-600 font-semibold rounded-xl hover:bg-slate-50 transition-colors flex items-center gap-2">
                              {showSolution ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              {showSolution ? 'Hide' : 'Solution'}
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </>
              )}

              {/* Solution */}
              {showSolution && (
                <div className="animate-fade-in">
                  <AnswerDisplay questionId={Number(id)} />
                </div>
              )}
            </div>

            {/* Sidebar Component */}
            <PracticeSidebar 
              timeSpent={timeSpent}
              question={question}
              similar={similar}
            />
          </div>
        </div>
      </div>
    </>
  );
}
