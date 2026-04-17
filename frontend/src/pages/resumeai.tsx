import { useState, useRef } from 'react';
import Head from 'next/head';
import { 
  FileText, UploadCloud, AlertCircle, CheckCircle2, 
  XCircle, TrendingUp, Briefcase, Building2, 
  BookOpen, Star, Loader2, Sparkles
} from 'lucide-react';
import { resumeAiApi } from '@/lib/api';

export default function ResumeAI() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState<any>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      if (selectedFile.type !== 'application/pdf' && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
        setError('Invalid file format. Please upload a valid .pdf file.');
        return;
      }
      
      // Validate file size (5MB max)
      const maxSizeMB = 5;
      const fileSizeMB = selectedFile.size / (1024 * 1024);
      if (fileSizeMB > maxSizeMB) {
        setError(`File size too large. Maximum size is ${maxSizeMB}MB. Your file is ${fileSizeMB.toFixed(2)}MB.`);
        return;
      }
      
      // Validate file size minimum (should have some content)
      if (selectedFile.size < 5000) {
        setError('File appears to be empty or corrupted. Please upload a valid resume PDF.');
        return;
      }
      
      setFile(selectedFile);
      setError('');
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      // Validate file type
      if (droppedFile.type !== 'application/pdf' && !droppedFile.name.toLowerCase().endsWith('.pdf')) {
        setError('Invalid file format. Please upload a valid .pdf file.');
        return;
      }
      
      // Validate file size (5MB max)
      const maxSizeMB = 5;
      const fileSizeMB = droppedFile.size / (1024 * 1024);
      if (fileSizeMB > maxSizeMB) {
        setError(`File size too large. Maximum size is ${maxSizeMB}MB. Your file is ${fileSizeMB.toFixed(2)}MB.`);
        return;
      }
      
      setFile(droppedFile);
      setError('');
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload before proceeding.');
      return;
    }
    
    setLoading(true);
    setUploadProgress(0);
    setError('');
    setReport(null);

    const interval = setInterval(() => {
        setUploadProgress(prev => {
            if (prev >= 90) return prev;
            return prev + Math.floor(Math.random() * 10) + 5;
        });
    }, 500);

    try {
      const res = await resumeAiApi.uploadResume(file);
      clearInterval(interval);
      setUploadProgress(100);
      
      // Validate response
      if (!res.data) {
        throw new Error('Received an invalid response from the server.');
      }
      
      if (!res.data.detected_domain) {
        throw new Error('Could not analyze resume. Please ensure it contains readable text.');
      }
      
      setReport(res.data);
    } catch (err: any) {
      clearInterval(interval);
      
      // Handle specific error types
      if (err.response?.status === 413 || err.message?.includes('too large')) {
        setError('File size too large. Please use a smaller PDF file (max 5MB).');
      } else if (err.response?.status === 415 || err.message?.includes('format')) {
        setError('Invalid file format. Please ensure you are uploading a valid PDF file.');
      } else if (err.response?.status === 422 || err.message?.includes('text')) {
        setError('Could not read PDF. Please ensure the PDF contains extracted text (not a scanned image).');
      } else if (err.response?.status === 429) {
        setError('Too many requests. Please wait a moment and try again.');
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to analyze resume. Please try again.');
      }
      
      // Log error for debugging
      console.error('Resume upload error:', err);
    } finally {
      setTimeout(() => {
          setLoading(false);
          setUploadProgress(0);
      }, 500);
    }
  };

  return (
    <>
      <Head>
        <title>ResumeAI - PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 border border-indigo-200">
              <FileText className="w-5 h-5 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-900">Domain-Aware Resume Screening</span>
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4">
              Get Your Resume <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Shortlisted</span>
            </h1>
            <p className="text-lg text-slate-600">
              Upload your resume to get deep, actionable AI feedback tailor-made for your specific domain and target roles.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Upload */}
            <div className="lg:col-span-4 space-y-6">
              <div className="glass-card p-6 rounded-2xl sticky top-28 border border-slate-200 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                  <UploadCloud className="w-5 h-5 text-indigo-600" />
                  Upload Resume
                </h2>

                <div 
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                    isDragging ? 'border-indigo-500 bg-indigo-100 scale-105' :
                    file ? 'border-indigo-400 bg-indigo-50/50' : 'border-slate-300 hover:border-indigo-400 bg-white'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  <input 
                    type="file" 
                    className="hidden" 
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf"
                  />
                  
                  <div className="flex flex-col items-center gap-3">
                    <div className="p-3 bg-indigo-50 text-indigo-600 rounded-full">
                      <FileText className="w-6 h-6" />
                    </div>
                    {file ? (
                      <div>
                        <p className="text-sm font-semibold text-slate-700">{file.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        <button 
                          onClick={() => setFile(null)}
                          className="text-xs text-red-500 hover:text-red-600 font-medium mt-2"
                        >
                          Remove
                        </button>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm text-slate-600 mb-2">
                          <button onClick={() => fileInputRef.current?.click()} className="text-indigo-600 font-semibold hover:underline mr-1">
                            Click to upload
                          </button>
                          or drag and drop
                        </p>
                        <p className="text-xs text-slate-400">PDFs only, up to 5MB</p>
                      </div>
                    )}
                  </div>
                </div>

                {error && (
                  <div className="mt-4 p-4 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        <span>{error}</span>
                      </div>
                      {file && (
                        <button 
                          onClick={handleUpload}
                          disabled={loading}
                          className="ml-4 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded font-semibold text-xs transition-colors disabled:opacity-50 flex-shrink-0"
                        >
                          Retry
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {loading && uploadProgress > 0 && (
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-slate-700">Analyzing Resume</span>
                      <span className="text-indigo-600 font-bold">{uploadProgress}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                <button
                  onClick={handleUpload}
                  disabled={loading || !file}
                  className="w-full mt-6 py-4 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-glow disabled:opacity-50 transition-all duration-300 transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing Resume...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Analyze with AI
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Right Column: Results */}
            <div className="lg:col-span-8">
              {loading && (
                <div className="h-[600px] flex flex-col items-center justify-center glass-card rounded-2xl border border-slate-200">
                  <div className="relative w-20 h-20 mb-6">
                    <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Analyzing your resume...</h3>
                  <div className="w-64 bg-slate-200 rounded-full h-2 mb-2 overflow-hidden shadow-inner">
                    <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-300 ease-out" style={{width: `${uploadProgress}%`}}></div>
                  </div>
                  <p className="text-sm text-indigo-600 font-bold mb-4">{uploadProgress}%</p>
                  <p className="text-slate-500 max-w-md text-center text-sm">Checking ATS compatibility, extracting keywords, and generating domain-specific recommendations.</p>
                </div>
              )}

              {!loading && !report && (
                 <div className="h-[600px] flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
                  <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6">
                     <FileText className="w-10 h-10 text-slate-300" />
                  </div>
                  <h3 className="text-xl font-medium text-slate-500">Awaiting Resume</h3>
                  <p className="text-slate-400 mt-2">Upload your resume to see your personalized AI report card.</p>
                </div>
              )}

              {!loading && report && (
                <div className="space-y-6 animate-fade-in">
                  
                  {/* Top Scorecard */}
                  <div className="glass-card p-8 rounded-2xl border border-slate-200/60 shadow-sm relative overflow-hidden bg-white">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-indigo-100 via-transparent to-transparent opacity-50" />
                    
                    <div className="relative z-10">
                      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                        <div>
                          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-wider mb-1">
                            {report.detected_domain}
                          </p>
                          <h2 className="text-3xl font-heading font-extrabold text-slate-900">
                            {report.candidate_name || "Resume Assessment"}
                          </h2>
                        </div>
                        <div className="flex gap-4">
                           <div className="text-center p-4 bg-indigo-50 rounded-2xl border border-indigo-100 min-w-[120px]">
                             <p className="text-3xl font-black text-indigo-600">{report.score}/10</p>
                             <p className="text-xs font-semibold text-indigo-900/60 uppercase tracking-wide mt-1">Impact Score</p>
                           </div>
                           <div className="text-center p-4 bg-emerald-50 rounded-2xl border border-emerald-100 min-w-[120px]">
                             <p className="text-3xl font-black text-emerald-600">{report.ats_score}%</p>
                             <p className="text-xs font-semibold text-emerald-900/60 uppercase tracking-wide mt-1">ATS Match</p>
                           </div>
                        </div>
                      </div>

                      <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
                        <p className="text-slate-700 italic flex items-start gap-3">
                          <Sparkles className="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" />
                          "{report.encouragement}"
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Recommendations Grid */}
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Strengths */}
                    <div className="glass-card p-6 rounded-2xl border border-emerald-100 shadow-sm bg-white/60">
                      <h3 className="text-lg font-bold text-emerald-900 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        What's Working Well
                      </h3>
                      <ul className="space-y-3">
                        {report.strengths?.map((item: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-3">
                            <span className="text-emerald-500 mt-1">•</span>
                            <span className="text-slate-700 text-sm leading-relaxed">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Gaps */}
                    <div className="glass-card p-6 rounded-2xl border border-rose-100 shadow-sm bg-white/60">
                      <h3 className="text-lg font-bold text-rose-900 mb-4 flex items-center gap-2">
                        <XCircle className="w-5 h-5 text-rose-500" />
                        Critical Gaps
                      </h3>
                      <ul className="space-y-3">
                        {report.gaps?.map((item: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-3">
                            <span className="text-rose-500 mt-1">•</span>
                            <span className="text-slate-700 text-sm leading-relaxed">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Action Plan */}
                  <div className="glass-card p-6 rounded-2xl border border-indigo-100 shadow-sm bg-white">
                     <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-indigo-500" />
                        How to Improve & Action Plan
                     </h3>
                     <div className="space-y-4">
                        {report.improvements?.map((item: string, idx: number) => (
                          <div key={idx} className="flex gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
                             <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm flex-shrink-0">
                               {idx + 1}
                             </div>
                             <p className="text-slate-700 text-sm font-medium leading-relaxed">{item}</p>
                          </div>
                        ))}
                     </div>
                  </div>

                  {/* Keywords & Summary */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="glass-card p-6 rounded-2xl border border-amber-100 shadow-sm bg-amber-50/30">
                      <h3 className="text-sm font-bold text-amber-900 uppercase tracking-widest mb-4">
                        Missing Keywords
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {report.keywords_missing?.map((kw: string) => (
                          <span key={kw} className="px-3 py-1.5 bg-white border border-amber-200 text-amber-800 rounded-lg text-xs font-semibold shadow-sm">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="glass-card p-6 rounded-2xl border border-purple-100 shadow-sm bg-purple-50/30">
                      <h3 className="text-sm font-bold text-purple-900 uppercase tracking-widest mb-3">
                        Suggested Summary
                      </h3>
                      <p className="text-purple-900/80 text-sm italic leading-relaxed">
                        {report.suggested_summary}
                      </p>
                    </div>
                  </div>

                  {/* Career Compass */}
                  <div className="glass-card p-8 rounded-2xl border border-slate-200/60 shadow-sm bg-slate-900 text-white overflow-hidden relative">
                     <div className="absolute top-0 right-0 w-64 h-64 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent" />
                     <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">
                        <Star className="w-6 h-6 text-yellow-500" />
                        Career Compass
                     </h3>
                     
                     <div className="grid md:grid-cols-3 gap-8 relative z-10">
                        <div>
                          <h4 className="flex items-center gap-2 text-indigo-300 font-semibold mb-4 uppercase text-xs tracking-widest">
                            <Briefcase className="w-4 h-4" /> Best Fit Roles
                          </h4>
                          <ul className="space-y-2">
                            {report.best_fit_roles?.map((role: string) => (
                              <li key={role} className="text-slate-300 text-sm font-medium">{role}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="flex items-center gap-2 text-indigo-300 font-semibold mb-4 uppercase text-xs tracking-widest">
                            <Building2 className="w-4 h-4" /> Top Companies
                          </h4>
                          <ul className="space-y-2">
                            {report.top_companies_to_target?.map((co: string) => (
                              <li key={co} className="text-slate-300 text-sm font-medium">{co}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="flex items-center gap-2 text-indigo-300 font-semibold mb-4 uppercase text-xs tracking-widest">
                            <BookOpen className="w-4 h-4" /> What to Learn Next
                          </h4>
                          <ul className="space-y-2">
                            {report.what_to_learn_next?.map((skill: string) => (
                              <li key={skill} className="text-emerald-400 text-sm font-medium flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                {skill}
                              </li>
                            ))}
                          </ul>
                        </div>
                     </div>
                  </div>

                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
