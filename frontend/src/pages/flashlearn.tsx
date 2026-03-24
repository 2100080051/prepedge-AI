import { useState, useEffect } from 'react';
import Head from 'next/head';
import { flashLearnApi } from '@/lib/api';
import { 
  Brain, ChevronLeft, ChevronRight, Loader2, Sparkles, 
  Building2, BookOpen, Tag, RefreshCw, AlertCircle
} from 'lucide-react';

const COMPANIES = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Cognizant'];
const TOPICS = ['Aptitude', 'Coding', 'HR Interview'];
const COMPANY_COLORS: Record<string, string> = {
  TCS:        'from-blue-600 to-blue-800',
  Infosys:    'from-indigo-600 to-indigo-800',
  Wipro:      'from-purple-600 to-purple-800',
  Accenture:  'from-cyan-600 to-cyan-800',
  Cognizant:  'from-teal-600 to-teal-800',
};
const DIFFICULTY_BADGE: Record<string, string> = {
  easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  hard:   'bg-rose-100 text-rose-700 border-rose-200',
};
const TOPIC_BADGE: Record<string, string> = {
  Aptitude:       'bg-orange-100 text-orange-700',
  Coding:         'bg-indigo-100 text-indigo-700',
  'HR Interview': 'bg-pink-100 text-pink-700',
};

export default function FlashLearn() {
  const [step, setStep] = useState<'setup' | 'cards'>('setup');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');

  const [flashcards, setFlashcards] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // On first load, seed the database
  useEffect(() => {
    flashLearnApi.seed().catch(() => {});
  }, []);

  const handleStart = async () => {
    if (!selectedCompany || !selectedTopic) return;
    setIsLoading(true);
    setError('');
    try {
      const res = await flashLearnApi.getRandomFlashcards(10, undefined, selectedTopic, selectedCompany);
      if (!res.data || res.data.length === 0) {
        setError(`No cards found for ${selectedCompany} — ${selectedTopic}. Try a different combination.`);
        return;
      }
      setFlashcards(res.data);
      setCurrentIndex(0);
      setIsFlipped(false);
      setStep('cards');
    } catch (err: any) {
      setError('Failed to load flashcards. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    setIsFlipped(false);
    setTimeout(() => setCurrentIndex(prev => Math.min(prev + 1, flashcards.length - 1)), 120);
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setTimeout(() => setCurrentIndex(prev => Math.max(prev - 1, 0)), 120);
  };

  const handleRestart = () => {
    setStep('setup');
    setFlashcards([]);
    setIsFlipped(false);
    setCurrentIndex(0);
  };

  const currentCard = flashcards[currentIndex];

  // ── Setup Screen ──────────────────────────────────────────────────────────
  if (step === 'setup') {
    return (
      <>
        <Head><title>FlashLearn — PrepEdge AI</title></Head>
        <div className="min-h-screen bg-slate-50 pt-24 pb-12">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 border border-indigo-200">
                <Brain className="w-5 h-5 text-indigo-600" />
                <span className="text-sm font-medium text-indigo-900">Company + Topic Based Practice</span>
              </div>
              <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
                FlashLearn <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Visualizer</span>
              </h1>
              <p className="text-lg text-slate-600">
                Select your target company and what you want to practice. Cards are curated specifically for that company's interview pattern.
              </p>
            </div>

            <div className="glass-card p-8 sm:p-10 rounded-3xl border border-slate-200 max-w-3xl mx-auto shadow-sm">
              {/* Company Selector */}
              <div className="mb-10">
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2">
                  <Building2 className="w-4 h-4" /> Target Company
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  {COMPANIES.map(company => (
                    <button
                      key={company}
                      onClick={() => setSelectedCompany(company)}
                      className={`py-3 px-2 rounded-xl font-semibold text-sm border-2 transition-all duration-200 ${
                        selectedCompany === company
                          ? `bg-gradient-to-br ${COMPANY_COLORS[company]} text-white border-transparent shadow-lg scale-105`
                          : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300 hover:text-indigo-600'
                      }`}
                    >
                      {company}
                    </button>
                  ))}
                </div>
              </div>

              {/* Topic Selector */}
              <div className="mb-10">
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-5 flex items-center gap-2">
                  <Tag className="w-4 h-4" /> Topic
                </h2>
                <div className="grid grid-cols-3 gap-4">
                  {TOPICS.map(topic => (
                    <button
                      key={topic}
                      onClick={() => setSelectedTopic(topic)}
                      className={`py-4 rounded-xl font-semibold text-sm border-2 transition-all duration-200 flex flex-col items-center gap-2 ${
                        selectedTopic === topic
                          ? 'bg-indigo-50 border-indigo-500 text-indigo-700 shadow-sm'
                          : 'bg-white border-slate-200 text-slate-700 hover:border-indigo-300'
                      }`}
                    >
                      {topic === 'Aptitude' && <span className="text-2xl">🧮</span>}
                      {topic === 'Coding' && <span className="text-2xl">💻</span>}
                      {topic === 'HR Interview' && <span className="text-2xl">🎤</span>}
                      {topic}
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-center gap-2 text-sm">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  {error}
                </div>
              )}

              <button
                onClick={handleStart}
                disabled={!selectedCompany || !selectedTopic || isLoading}
                className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl disabled:opacity-40 hover:shadow-glow transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2 text-lg"
              >
                {isLoading ? (
                  <><Loader2 className="w-5 h-5 animate-spin" /> Loading Cards...</>
                ) : (
                  <><Sparkles className="w-6 h-6" /> Start Practice Session</>
                )}
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  // ── Card Study Screen ─────────────────────────────────────────────────────
  return (
    <>
      <Head><title>FlashLearn — {selectedCompany} {selectedTopic}</title></Head>
      <div className="min-h-screen bg-slate-50 pt-24 pb-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-heading font-extrabold text-slate-900">FlashLearn Visualizer</h1>
              <p className="text-slate-500 text-sm mt-1">
                <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold mr-2 ${TOPIC_BADGE[selectedTopic]}`}>{selectedTopic}</span>
                <span className="font-semibold text-slate-700">{selectedCompany}</span> — {flashcards.length} cards loaded
              </p>
            </div>
            <button onClick={handleRestart} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
              <RefreshCw className="w-4 h-4" /> Change Topic
            </button>
          </div>

          {/* Flashcard */}
          <div
            className="cursor-pointer relative perspective-1000 mb-6"
            style={{ perspective: '1200px' }}
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div
              className="relative w-full transition-transform duration-500"
              style={{ transformStyle: 'preserve-3d', transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0)' }}
            >
              {/* Front — Question */}
              <div
                className={`glass-card rounded-2xl p-10 min-h-[280px] flex flex-col justify-between border border-slate-200 shadow-lg bg-gradient-to-br ${COMPANY_COLORS[selectedCompany]}`}
                style={{ backfaceVisibility: 'hidden' }}
              >
                <div className="flex justify-between items-center mb-6">
                  <span className="text-xs font-bold uppercase tracking-widest text-white/60">Question</span>
                  <Sparkles className="w-5 h-5 text-white/50" />
                </div>
                <p className="text-xl sm:text-2xl font-bold text-white text-center leading-relaxed flex-1 flex items-center justify-center">
                  {currentCard?.question}
                </p>
                <p className="text-center text-white/40 text-xs mt-6">Click anywhere to reveal answer</p>
              </div>

              {/* Back — Answer */}
              <div
                className="absolute inset-0 glass-card rounded-2xl p-10 min-h-[280px] flex flex-col justify-between bg-white border border-indigo-100 shadow-lg"
                style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
              >
                <div className="flex justify-between items-center mb-6">
                  <span className="text-xs font-bold uppercase tracking-widest text-emerald-600">Answer</span>
                  <BookOpen className="w-5 h-5 text-emerald-500" />
                </div>
                <p className="text-base sm:text-lg text-slate-800 leading-relaxed flex-1">
                  {currentCard?.answer}
                </p>
              </div>
            </div>
          </div>

          {/* Metadata & Nav */}
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              {currentCard?.difficulty && (
                <span className={`px-3 py-1.5 text-xs border rounded-lg font-semibold ${DIFFICULTY_BADGE[currentCard.difficulty] || ''}`}>
                  Diff: {currentCard.difficulty.charAt(0).toUpperCase() + currentCard.difficulty.slice(1)}
                </span>
              )}
              {currentCard?.company && (
                <span className="px-3 py-1.5 text-xs border border-slate-200 rounded-lg text-slate-600 font-semibold">
                  Co: {currentCard.company}
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handlePrev}
                disabled={currentIndex === 0}
                className="w-10 h-10 flex items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 disabled:opacity-30 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm font-semibold text-slate-700 w-16 text-center">
                {currentIndex + 1} / {flashcards.length}
              </span>
              <button
                onClick={handleNext}
                disabled={currentIndex === flashcards.length - 1}
                className="w-10 h-10 flex items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 disabled:opacity-30 transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-6 w-full bg-slate-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full bg-gradient-to-r ${COMPANY_COLORS[selectedCompany]} transition-all duration-300`}
              style={{ width: `${((currentIndex + 1) / flashcards.length) * 100}%` }}
            />
          </div>
          <p className="text-center text-xs text-slate-400 mt-2 font-medium">
            {currentIndex + 1} of {flashcards.length} cards completed
          </p>

        </div>
      </div>
    </>
  );
}
