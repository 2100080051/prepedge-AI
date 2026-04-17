import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { Sparkles, Brain, BookOpen, AlertCircle, Image as ImageIcon, Loader2, FileText, UploadCloud, Star, Target, GraduationCap, CheckCircle2, X, Copy, Check } from 'lucide-react';
import { learnAiApi } from '@/lib/api';

export default function LearnAI() {
  const [activeTab, setActiveTab] = useState<'concept' | 'summarizer'>('concept');

  // ── Concept Explainer State ───────
  const [domains, setDomains] = useState<any[]>([]);
  const [languages, setLanguages] = useState<any[]>([]);
  
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [concept, setConcept] = useState('');
  const [language, setLanguage] = useState('English');
  
  const [loading, setLoading] = useState(false);
  const [lesson, setLesson] = useState<any>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  // ── PDF Summarizer State ───────────
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfSummary, setPdfSummary] = useState<any>(null);
  const [pdfError, setPdfError] = useState('');
  const pdfInputRef = useRef<HTMLInputElement>(null);


  useEffect(() => {
    // Fetch domains and languages on mount
    const fetchData = async () => {
      try {
        const [domRes, langRes] = await Promise.all([
          learnAiApi.getDomains(),
          learnAiApi.getLanguages()
        ]);
        setDomains(domRes.data);
        setLanguages(langRes.data);
      } catch (err) {
        console.error("Failed to load LearnAI metadata", err);
      }
    };
    fetchData();
  }, []);

  // When domain changes, reset subject
  useEffect(() => {
    setSelectedSubject('');
  }, [selectedDomain]);

  const currentDomainInfo = domains.find(d => d.domain === selectedDomain);
  const subjects = currentDomainInfo ? currentDomainInfo.subjects : [];

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!selectedDomain || !selectedSubject || !concept.trim()) {
      setError('Please fill in all required fields.');
      return;
    }
    
    setError('');
    setLoading(true);
    setLesson(null);
    setCopied(false);

    let attempts = 0;
    const maxAttempts = 3;

    while (attempts < maxAttempts) {
      try {
        const res = await learnAiApi.explainAndVisualize(selectedDomain, selectedSubject, concept, language);
        
        // Validate response - check for empty explanation
        if (!res.data) {
          throw new Error('No data received from AI. Please try again.');
        }
        
        if (!res.data.explanation || res.data.explanation.trim().length < 10) {
          throw new Error('Received an empty or incomplete response from the AI.');
        }
        
        setLesson(res.data);
        break; // Success
      } catch (err: any) {
        attempts++;
        
        // Handle specific error types
        if (err.response?.status === 429) {
          setError('API rate limit reached. Please wait a moment and try again.');
        } else if (err.response?.status === 500 || err.response?.status === 502 || err.response?.status === 503) {
          setError('AI service temporarily unavailable. Retrying...');
        } else if (attempts >= maxAttempts) {
          setError(err.response?.data?.detail || err.message || 'Failed to generate lesson. Please try again or check your internet connection.');
        }
        
        // Retry with exponential backoff
        if (attempts < maxAttempts) {
          const delayMs = 1000 * Math.pow(2, attempts - 1); // 1s, 2s, 4s
          await new Promise(resolve => setTimeout(resolve, Math.min(delayMs, 5000)));
        }
      }
    }
    setLoading(false);
  };

  const handlePdfSummarize = async () => {
    if (!pdfFile) return;
    setPdfLoading(true);
    setPdfError('');
    setPdfSummary(null);
    
    try {
      const res = await learnAiApi.summarizePdf(pdfFile);
      
      // Validate PDF summary response
      if (!res.data || !res.data.title) {
        throw new Error('Failed to process PDF. Please ensure it is a valid PDF file.');
      }
      
      setPdfSummary(res.data);
    } catch (err: any) {
      // Handle specific error types
      if (err.response?.status === 413 || err.message?.includes('too large')) {
        setPdfError('File size too large. Maximum PDF size is 25MB.');
      } else if (err.response?.status === 415 || err.message?.includes('format')) {
        setPdfError('Invalid file format. Please upload a valid PDF file.');
      } else if (err.response?.status === 429) {
        setPdfError('Too many requests. Please wait a moment and try again.');
      } else {
        setPdfError(err.response?.data?.detail || 'Failed to process PDF. Please try again.');
      }
      console.error('PDF summarization error:', err);
    } finally {
      setPdfLoading(false);
    }
  };


  return (
    <>
      <Head>
        <title>LearnAI - PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto mb-10">
             <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 border border-indigo-200">
              <Brain className="w-5 h-5 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-900">Nvidia Llama 3.1 Powered Learning</span>
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Master Any Concept, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Instantly</span>
            </h1>
            <p className="text-lg text-slate-600">
              AI-powered concept explanations in your native language, or upload a PDF to get structured exam-ready notes.
            </p>
          </div>

          {/* Tab Switcher */}
          <div className="flex justify-center mb-10">
            <div className="inline-flex bg-white border border-slate-200 rounded-xl p-1.5 shadow-sm gap-1">
              <button
                onClick={() => setActiveTab('concept')}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'concept'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-indigo-600'
                }`}
              >
                <Brain className="w-4 h-4" /> Concept Explainer
              </button>
              <button
                onClick={() => setActiveTab('summarizer')}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'summarizer'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-purple-600'
                }`}
              >
                <FileText className="w-4 h-4" /> PDF Summarizer
              </button>
            </div>
          </div>


          {/* Concept Explainer Tab */}
          {activeTab === 'concept' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Form */}
            <div className="lg:col-span-4 space-y-6">
              <div className="glass-card p-6 rounded-2xl sticky top-28 border border-slate-200 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  What do you want to learn?
                </h2>

                <form onSubmit={handleGenerate} className="space-y-5">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Domain</label>
                    <select
                      value={selectedDomain}
                      onChange={(e) => setSelectedDomain(e.target.value)}
                      className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      required
                    >
                      <option value="">Select Domain...</option>
                      {domains.map((d) => (
                        <option key={d.domain} value={d.domain}>{d.icon} {d.domain}</option>
                      ))}
                    </select>
                  </div>

                  {selectedDomain && (
                    <div className="space-y-2">
                      <label className="block text-sm font-medium text-slate-700">Subject</label>
                      <select
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                        required
                      >
                        <option value="">Select Subject...</option>
                        {subjects.map((sub: string) => (
                          <option key={sub} value={sub}>{sub}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Concept</label>
                    <input
                      type="text"
                      value={concept}
                      onChange={(e) => setConcept(e.target.value)}
                      placeholder="e.g. Binary Search Tree, Inflation"
                      className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Language</label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
                    >
                      {languages.map((lang) => (
                        <option key={lang.code} value={lang.code}>{lang.flag} {lang.label}</option>
                      ))}
                    </select>
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 flex items-center justify-between">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        <span>{error}</span>
                      </div>
                      <button
                        onClick={handleGenerate}
                        disabled={loading}
                        className="ml-4 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded font-semibold text-xs transition-colors disabled:opacity-50"
                      >
                        Retry
                      </button>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || !selectedDomain || !selectedSubject || !concept.trim()}
                    className="w-full py-4 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-glow disabled:opacity-50 transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Generating your lesson...
                      </>
                    ) : (
                      <>
                        <Brain className="w-5 h-5" />
                        Generate Lesson
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Right Column: Results */}
            <div className="lg:col-span-8">
              {loading && (
                <div className="h-96 flex flex-col items-center justify-center glass-card rounded-2xl border border-slate-200">
                  <div className="relative w-20 h-20 mb-6">
                    <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                    <Brain className="absolute inset-0 m-auto w-8 h-8 text-indigo-600 animate-pulse" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Analyzing {concept}...</h3>
                  <p className="text-slate-500">Generating plain-english explanation, code examples, and visual diagrams via Nvidia AI.</p>
                </div>
              )}

              {!loading && !lesson && (
                <div className="h-96 flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
                  <BookOpen className="w-16 h-16 text-slate-300 mb-4" />
                  <h3 className="text-xl font-medium text-slate-500">Your AI lesson will appear here</h3>
                  <p className="text-slate-400 mt-2">Select a topic and concept to get started.</p>
                </div>
              )}

              {!loading && lesson && (
                <div className="space-y-6 animate-fade-in">
                  
                  {/* Topic Header */}
                  <div className="glass-card p-8 rounded-2xl border border-slate-200/60 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-indigo-100 to-transparent opacity-50 rounded-bl-[100px]" />
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider">
                            {lesson.domain}
                          </span>
                          <span className="text-slate-400">•</span>
                          <span className="text-slate-600 font-medium">{lesson.subject}</span>
                        </div>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(`${lesson.concept}\n\n${lesson.explanation}`);
                            setCopied(true);
                            setTimeout(() => setCopied(false), 2000);
                          }}
                          className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 border border-indigo-100 hover:bg-indigo-100 text-indigo-600 rounded-lg transition-colors text-sm font-semibold"
                        >
                          {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                          {copied ? 'Copied!' : 'Copy'}
                        </button>
                      </div>
                      <h2 className="text-3xl md:text-5xl font-heading font-extrabold text-slate-900 mb-6">
                        {lesson.concept}
                      </h2>
                      <div className="prose prose-lg text-slate-700 max-w-none">
                        <p className="leading-relaxed text-xl">{lesson.explanation}</p>
                      </div>
                    </div>
                  </div>

                  {/* Generated Image (Nvidia Sana) */}
                  {lesson.image_base64 && (
                    <div className="glass-card p-6 rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
                      <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <ImageIcon className="w-5 h-5 text-pink-500" />
                        AI Visual Concept
                      </h3>
                      <div className="rounded-xl overflow-hidden border border-slate-100 shadow-inner bg-slate-50">
                        <img 
                          src={`data:image/jpeg;base64,${lesson.image_base64}`} 
                          alt={lesson.concept} 
                          className="w-full h-auto object-contain max-h-[500px]"
                        />
                      </div>
                      <p className="text-xs text-center text-slate-400 mt-3 font-medium">Generated by Nvidia Sana Text-to-Image Model</p>
                    </div>
                  )}

                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Analogy */}
                    <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-2xl border border-orange-100/50 shadow-sm">
                      <h3 className="text-lg font-bold text-orange-800 mb-3 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-orange-500" />
                        Real-World Analogy
                      </h3>
                      <p className="text-orange-900/80 leading-relaxed font-medium">
                        {lesson.analogy}
                      </p>
                    </div>

                    {/* Example */}
                    <div className="bg-gradient-to-br from-emerald-50 to-teal-50 p-6 rounded-2xl border border-emerald-100/50 shadow-sm">
                      <h3 className="text-lg font-bold text-emerald-800 mb-3 flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-emerald-500" />
                        Worked Example
                      </h3>
                      <div className="text-emerald-900/80 leading-relaxed">
                        <pre className="whitespace-pre-wrap font-sans font-medium">{lesson.example}</pre>
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Key Points */}
                    <div className="glass-card p-6 rounded-2xl border border-indigo-100 shadow-sm bg-white/60">
                      <h3 className="text-lg font-bold text-indigo-900 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-indigo-500" />
                        Key Takeaways
                      </h3>
                      <ul className="space-y-3">
                        {lesson.key_points?.map((point: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-3">
                            <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0 text-sm font-bold mt-0.5">
                              {idx + 1}
                            </span>
                            <span className="text-slate-700">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Common Mistakes */}
                    <div className="glass-card p-6 rounded-2xl border border-rose-100 shadow-sm bg-white/60">
                      <h3 className="text-lg font-bold text-rose-900 mb-4 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-rose-500" />
                        Common Mistakes to Avoid
                      </h3>
                      <ul className="space-y-3">
                        {lesson.common_mistakes?.map((mistake: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-3">
                            <X className="w-5 h-5 text-rose-500 flex-shrink-0 mt-0.5" />
                            <span className="text-slate-700">{mistake}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                </div>
              )}
            </div>
          </div>
          )}

          {/* PDF Summarizer Tab */}
          {activeTab === 'summarizer' && (
          <div className="max-w-5xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-1">
                <div className="glass-card p-6 rounded-2xl border border-slate-200 shadow-sm sticky top-28">
                  <h2 className="text-xl font-bold text-slate-900 mb-2 flex items-center gap-2"><UploadCloud className="w-5 h-5 text-purple-600" />Upload PDF</h2>
                  <p className="text-sm text-slate-500 mb-5">Upload study PDFs — textbooks, notes, handouts — and get AI-generated exam notes instantly.</p>
                  <div onClick={() => pdfInputRef.current?.click()}
                    className={`cursor-pointer border-2 border-dashed rounded-xl p-8 text-center transition-all mb-5 ${pdfFile ? 'border-purple-400 bg-purple-50/50' : 'border-slate-300 hover:border-purple-400 bg-white'}`}>
                    <input type="file" ref={pdfInputRef} onChange={(e) => { if(e.target.files?.[0]) { setPdfFile(e.target.files[0]); setPdfError(''); }}} accept=".pdf" className="hidden" />
                    <FileText className={`w-10 h-10 mx-auto mb-3 ${pdfFile ? 'text-purple-500' : 'text-slate-300'}`} />
                    {pdfFile ? (<div><p className="font-semibold text-slate-800 text-sm">{pdfFile.name}</p><p className="text-xs text-slate-500 mt-1">{(pdfFile.size/1024/1024).toFixed(2)} MB</p><button onClick={(e) => {e.stopPropagation(); setPdfFile(null);}} className="text-xs text-red-500 hover:text-red-600 font-medium mt-2">Remove</button></div>)
                      : (<p className="text-sm text-slate-500">Click to select PDF or drag &amp; drop</p>)}
                  </div>
                  {pdfError && (<div className="mb-4 p-4 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 flex items-center justify-between"><div className="flex items-start gap-2"><AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /><span>{pdfError}</span></div><button onClick={handlePdfSummarize} disabled={!pdfFile || pdfLoading} className="ml-4 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded font-semibold text-xs transition-colors disabled:opacity-50">Retry</button></div>)}
                  <button onClick={handlePdfSummarize} disabled={!pdfFile || pdfLoading}
                    className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-xl disabled:opacity-50 transition-all flex items-center justify-center gap-2">
                    {pdfLoading ? (<><Loader2 className="w-5 h-5 animate-spin" />Analyzing PDF...</>) : (<><Sparkles className="w-5 h-5" />Generate Exam Notes</>)}
                  </button>
                </div>
              </div>
              <div className="lg:col-span-2">
                {pdfLoading && (<div className="h-96 flex flex-col items-center justify-center glass-card rounded-2xl border border-slate-200"><div className="relative w-20 h-20 mb-6"><div className="absolute inset-0 border-4 border-purple-100 rounded-full"></div><div className="absolute inset-0 border-4 border-purple-600 rounded-full border-t-transparent animate-spin"></div></div><h3 className="text-xl font-bold text-slate-900 mb-2">Reading your PDF...</h3><p className="text-slate-500 text-center">Extracting text and generating exam notes via Nvidia AI.</p></div>)}
                {!pdfLoading && !pdfSummary && (<div className="h-96 flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-2xl bg-white/50"><FileText className="w-16 h-16 text-slate-300 mb-4" /><h3 className="text-xl font-medium text-slate-500">Your exam notes will appear here</h3><p className="text-slate-400 mt-2">Upload a PDF to generate structured revision notes.</p></div>)}
                {!pdfLoading && pdfSummary && (
                  <div className="space-y-6 animate-fade-in">
                    <div className="glass-card p-8 rounded-2xl border border-slate-200 bg-white">
                      <h2 className="text-3xl font-bold text-slate-900 mb-1">{pdfSummary.title}</h2>
                      <p className="text-slate-500 text-sm">{pdfSummary.filename} &bull; {pdfSummary.total_pages_processed} pages processed</p>
                    </div>
                    <div className="glass-card p-6 rounded-2xl border border-indigo-100 bg-indigo-50/30">
                      <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-widest mb-4 flex items-center gap-2"><Target className="w-4 h-4" />Key Topics Covered</h3>
                      <div className="flex flex-wrap gap-2">{pdfSummary.key_topics?.map((t: string) => (<span key={t} className="px-3 py-1.5 bg-white border border-indigo-200 text-indigo-700 rounded-lg text-sm font-semibold shadow-sm">{t}</span>))}</div>
                    </div>
                    <div className="glass-card p-6 rounded-2xl border border-amber-100 bg-amber-50/30">
                      <h3 className="text-sm font-bold text-amber-900 uppercase tracking-widest mb-4 flex items-center gap-2"><Star className="w-4 h-4" />Must-Know for Exam</h3>
                      <ul className="space-y-2">{pdfSummary.exam_tips?.map((tip: string, i: number) => (<li key={i} className="flex items-start gap-3 text-sm text-slate-700 font-medium"><span className="w-5 h-5 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5">{i+1}</span>{tip}</li>))}</ul>
                    </div>
                    <div className="glass-card p-6 rounded-2xl border border-emerald-100 bg-emerald-50/20">
                      <h3 className="text-sm font-bold text-emerald-900 uppercase tracking-widest mb-4 flex items-center gap-2"><GraduationCap className="w-4 h-4" />Quick Revision Points</h3>
                      <ul className="space-y-2">{pdfSummary.quick_revision_points?.map((point: string, i: number) => (<li key={i} className="flex items-start gap-2 text-sm text-slate-700"><span className="text-emerald-500 font-bold mt-0.5">•</span>{point}</li>))}</ul>
                    </div>
                    {pdfSummary.chapter_summaries?.length > 0 && (
                      <div className="glass-card p-6 rounded-2xl border border-slate-100 bg-white">
                        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-widest mb-5">Chapter Summaries</h3>
                        <div className="space-y-4">{pdfSummary.chapter_summaries?.map((ch: any, i: number) => (<div key={i} className="p-4 bg-slate-50 rounded-xl border border-slate-100"><p className="font-semibold text-slate-800 text-sm mb-1">{ch.chapter}</p><p className="text-slate-600 text-sm leading-relaxed">{ch.summary}</p></div>))}</div>
                      </div>
                    )}
                    {pdfSummary.formula_or_concepts?.length > 0 && (
                      <div className="glass-card p-6 rounded-2xl border border-purple-100 bg-purple-50/20">
                        <h3 className="text-sm font-bold text-purple-900 uppercase tracking-widest mb-4">📐 Formulas &amp; Core Concepts</h3>
                        <ul className="space-y-2">{pdfSummary.formula_or_concepts?.map((f: string, i: number) => (<li key={i} className="font-mono text-sm text-purple-800 bg-white border border-purple-100 rounded-lg px-4 py-2">{f}</li>))}</ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
          )}

        </div>
      </div>
    </>
  );
}

