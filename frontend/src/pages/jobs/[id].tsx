import { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { ArrowLeft, ExternalLink, MapPin, Briefcase, DollarSign, Target, Award, Loader2, AlertCircle } from 'lucide-react'
import apiClient from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import MatchBreakdown from '@/components/jobs/MatchBreakdown'
import RichTextRenderer from '@/components/shared/RichTextRenderer'
import Link from 'next/link'

export default function JobDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const { isAuthenticated } = useAuthStore()

  const [job, setJob] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasApplied, setHasApplied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return }
    if (id) fetchJobDetails()
  }, [id, isAuthenticated])

  async function fetchJobDetails() {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.get(`/api/v1/jobs/jobs/${id}`)
      setJob(response.data)

      // Optionally record a view for analytics
      try { await apiClient.post(`/api/v1/jobs/jobs/${id}/click`) } catch(e) {}

    } catch (err: any) {
      console.error('Failed to fetch job:', err)
      setError("Failed to load job details. The job might have been removed.")
    } finally {
      setIsLoading(false)
    }
  }

  async function handleApply() {
    try {
      const response = await apiClient.post(`/api/v1/jobs/jobs/${id}/apply`, {
        applied_through: 'direct_apply'
      })
      
      setHasApplied(true)
      
      // Delay slightly for effect before opening external link
      setTimeout(() => {
        window.open(job.url, '_blank', 'noopener,noreferrer')
      }, 500)
    } catch (error) {
      console.error('Error applying:', error)
      // Fallback
      window.open(job.url, '_blank', 'noopener,noreferrer')
    }
  }

  if (isLoading) return (
    <div className="min-h-screen bg-slate-50 pt-24 pb-16 flex flex-col items-center justify-center">
      <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
      <p className="text-slate-500 font-medium">Fetching job details...</p>
    </div>
  )

  if (error || !job) return (
    <div className="min-h-screen bg-slate-50 pt-24 pb-16 flex flex-col items-center justify-center">
      <AlertCircle className="w-16 h-16 text-slate-300 mb-4" />
      <h1 className="text-2xl font-bold font-heading text-slate-800 mb-2">Job Not Found</h1>
      <p className="text-slate-500 mb-6">{error || "This job listing is no longer available."}</p>
      <button onClick={() => router.back()} className="btn-primary">
        Go Back
      </button>
    </div>
  )

  return (
    <>
      <Head>
        <title>{job.job_title} at {job.company} | PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-fade-in">
          
          {/* Back Navigation */}
          <button
            onClick={() => router.back()}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to matches
          </button>

          {/* Intro Section */}
          <div className="bg-white p-6 md:p-10 rounded-3xl border border-slate-200 shadow-sm relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl opacity-60 -mr-20 -mt-20 pointer-events-none" />
            
            <div className="relative z-10 flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-extrabold font-heading text-slate-900 mb-3 leading-tight">{job.job_title}</h1>
                <p className="text-xl text-slate-600 font-medium">{job.company}</p>
              </div>
              <div className="text-left md:text-right flex items-center md:flex-col gap-4 md:gap-2">
                <div className="inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-indigo-600 text-white font-bold text-xl md:text-2xl shadow-lg shadow-indigo-200">
                  {job.match_score}%
                </div>
                <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Match Score</p>
              </div>
            </div>

            {/* Meta Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pb-2 border-b border-slate-100">
              <div className="space-y-1">
                <p className="text-sm text-slate-400 font-medium flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" />Location</p>
                <p className="font-bold text-slate-800">{job.location || 'Remote'}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-slate-400 font-medium flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" />Job Type</p>
                <p className="font-bold text-slate-800">{job.job_type || 'Full-time'}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-slate-400 font-medium flex items-center gap-1.5"><Award className="w-3.5 h-3.5" />Experience</p>
                <p className="font-bold text-slate-800">{job.experience_required || 'Not specified'}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-slate-400 font-medium flex items-center gap-1.5"><DollarSign className="w-3.5 h-3.5" />Salary</p>
                <p className="font-bold text-slate-800">{job.salary_range || 'Competitive'}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
             {/* Left Column: Description */}
             <div className="lg:col-span-2 space-y-8">
               
               {/* Match Breakdown Component */}
               <MatchBreakdown breakdown={job.match_breakdown || {role: 0, skills: 0, location: 0, company: 0}} />

               {/* Description */}
               <section className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm">
                 <h2 className="text-2xl font-bold font-heading mb-6 flex items-center gap-2">
                   About This Role
                 </h2>
                 <RichTextRenderer source={job.description || '*No detailed description provided by the company.*'} />
               </section>

             </div>

             {/* Right Column: Skills & CTA */}
             <div className="lg:col-span-1 space-y-6 lg:sticky lg:top-24">
               
               {/* Skills Box */}
               <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                 <h2 className="text-lg font-bold font-heading mb-4 flex items-center gap-2">
                   <Target className="w-5 h-5 text-indigo-500" /> Required Skills
                 </h2>
                 <div className="flex flex-wrap gap-2">
                   {(job.skills_required || []).map((skill: string, i: number) => (
                     <span key={i} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-lg text-sm font-semibold">
                       {skill}
                     </span>
                   ))}
                   {(!job.skills_required || job.skills_required.length === 0) && (
                     <p className="text-sm text-slate-500 italic">No specific skills listed.</p>
                   )}
                 </div>
               </div>

               {/* Apply Box */}
               <div className="bg-indigo-600 p-8 rounded-3xl shadow-lg relative overflow-hidden group">
                 <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-indigo-700 opacity-50" />
                 <div className="absolute -right-8 -top-8 w-32 h-32 bg-white rounded-full blur-3xl opacity-10 group-hover:opacity-20 transition-opacity" />
                 
                 <div className="relative z-10">
                   <h3 className="text-xl font-bold text-white mb-2 font-heading">Ready to Apply?</h3>
                   <p className="text-indigo-100 text-sm leading-relaxed mb-6">
                     You strongly match {job.match_score}% of the requirements. Make sure your ResumeAI is updated before pursuing!
                   </p>
                   <button
                     onClick={handleApply}
                     className={`w-full py-3.5 px-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
                       hasApplied 
                         ? 'bg-emerald-500 text-white shadow-emerald-500/30' 
                         : 'bg-white text-indigo-600 hover:bg-slate-50 hover:shadow-lg focus:ring-4 ring-white/20'
                     }`}
                   >
                     {hasApplied ? (
                       <>✓ Application Recorded</>
                     ) : (
                       <>Apply on {job.source || 'Company Site'} <ExternalLink className="w-4 h-4 ml-1" /></>
                     )}
                   </button>
                 </div>
               </div>
             </div>
          </div>

        </div>
      </div>
    </>
  )
}
