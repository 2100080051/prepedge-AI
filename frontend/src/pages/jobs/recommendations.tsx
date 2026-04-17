import { useEffect, useState } from 'react'
import Head from 'next/head'
import JobCard from '@/components/jobs/JobCard'
import JobFilter from '@/components/jobs/JobFilter'
import JobPreferencesModal from '@/components/jobs/JobPreferencesModal'
import apiClient from '@/lib/api'
import { useRouter } from 'next/router'
import { Settings, Loader2, Sparkles, AlertCircle } from 'lucide-react'
import { useAuthStore } from '@/store/auth'

export default function RecommendationsPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()

  const [jobs, setJobs] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isPrefsOpen, setIsPrefsOpen] = useState(false)
  
  const [filters, setFilters] = useState({
    minScore: 0,
    maxSalary: null,
    jobTypes: [],
    locations: [],
  })

  useEffect(() => {
    if (!isAuthenticated) { router.push('/auth/login'); return }
    fetchRecommendations()
  }, [page, filters, isAuthenticated])

  async function fetchRecommendations() {
    try {
      setIsLoading(true)
      const params = new URLSearchParams({
        limit: '10',
        offset: String((page - 1) * 10),
      })

      // We apply filters locally on the returned list to save API complex queries immediately if it's small, 
      // but ideally the API accepts these filters. For now, fetch standard list:
      const response = await apiClient.get(`/api/v1/jobs/recommendations?${params.toString()}`)
      const data = response.data
      
      let fetchedJobs = data.jobs || data || [] // handle API variability
      
      // Local filter acting as a stand-in if the API doesn't support the full filter params natively
      if (filters.minScore > 0) fetchedJobs = fetchedJobs.filter((j: any) => j.match_score >= filters.minScore)
      if ((filters.jobTypes as string[]).length > 0) fetchedJobs = fetchedJobs.filter((j: any) => (filters.jobTypes as string[]).includes(j.job_type))

      setJobs(fetchedJobs)
      setTotal(data.total || fetchedJobs.length)
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const totalPages = Math.ceil(total / 10) || 1

  return (
    <>
      <Head>
        <title>Curated Jobs | PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 pb-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-widest mb-3">
                <Sparkles className="w-3.5 h-3.5" /> AI Curated Matches
              </div>
              <h1 className="text-3xl font-bold font-heading text-slate-900">Job Recommendations</h1>
              <p className="text-slate-500 mt-1">Based on your skills, experience, and personalized preferences.</p>
            </div>
            <button 
              onClick={() => setIsPrefsOpen(true)}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl font-bold shadow-sm transition-colors"
            >
              <Settings className="w-4 h-4" /> Edit Preferences
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
            {/* Left Col: Filters */}
            <div className="lg:col-span-1 sticky top-24">
              <JobFilter filters={filters} onChange={setFilters} />
            </div>

            {/* Right Col: Jobs List */}
            <div className="lg:col-span-3 space-y-5">
              {isLoading ? (
                // Skeletons
                [...Array(3)].map((_, i) => (
                  <div key={i} className="glass-card p-6 border border-slate-200 rounded-2xl animate-pulse space-y-4">
                    <div className="flex justify-between">
                      <div className="w-1/2 h-6 bg-slate-200 rounded"></div>
                      <div className="w-16 h-16 bg-slate-200 rounded-xl"></div>
                    </div>
                    <div className="w-1/3 h-4 bg-slate-200 rounded"></div>
                    <div className="flex gap-2"><div className="w-20 h-8 bg-slate-200 rounded"></div><div className="w-20 h-8 bg-slate-200 rounded"></div></div>
                  </div>
                ))
              ) : jobs.length === 0 ? (
                // Empty State
                <div className="flex flex-col items-center justify-center p-12 bg-white border border-slate-200 border-dashed rounded-3xl text-center">
                  <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-5">
                     <AlertCircle className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-800 mb-2 font-heading">No perfect matches right now</h3>
                  <p className="text-slate-500 mb-8 max-w-md">We couldn't find active jobs matching your exact criteria. Try adjusting your preferences to see more results.</p>
                  <button onClick={() => setIsPrefsOpen(true)} className="btn-primary px-8">
                     Adjust Preferences
                  </button>
                </div>
              ) : (
                // Job List
                <>
                  <div className="text-sm font-semibold text-slate-500 mb-2">Showing {jobs.length} recommendations</div>
                  <div className="space-y-4">
                    {jobs.map(job => (
                      <JobCard
                        key={job.id}
                        job={job}
                        onViewDetails={(jobId) => router.push(`/jobs/${jobId}`)}
                        onApply={async (jobId) => {
                          try { await apiClient.post(`/api/v1/jobs/jobs/${jobId}/apply`, { applied_through: 'direct_quick' }) } catch(e) {}
                        }}
                      />
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-2 pt-8">
                      <button
                        onClick={() => setPage(Math.max(1, page - 1))}
                        disabled={page === 1}
                        className="px-4 py-2 border border-slate-200 rounded-xl font-bold text-slate-600 disabled:opacity-40 hover:bg-slate-50 transition-colors"
                      >
                        Prev
                      </button>
                      <span className="text-sm font-bold text-slate-700 px-4">Page {page} of {totalPages}</span>
                      <button
                        onClick={() => setPage(Math.min(totalPages, page + 1))}
                        disabled={page === totalPages}
                        className="px-4 py-2 border border-slate-200 rounded-xl font-bold text-slate-600 disabled:opacity-40 hover:bg-slate-50 transition-colors"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <JobPreferencesModal 
        isOpen={isPrefsOpen} 
        onClose={() => setIsPrefsOpen(false)} 
        onSaved={fetchRecommendations}
      />
    </>
  )
}
