import { useEffect, useState } from 'react'
import Head from 'next/head'
import { Search, Filter, Briefcase, TrendingUp, Users, Award, Loader2, AlertCircle, ExternalLink } from 'lucide-react'
import apiClient from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'next/router'

interface Company {
  id: string
  name: string
  industry: string
  placement_rate: number
  avg_salary?: number
  logo_url?: string
  website?: string
  active_job_openings?: number
}

export default function CompanyBrowser() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  const [companies, setCompanies] = useState<Company[]>([])
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndustry, setSelectedIndustry] = useState('all')
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [companyDetails, setCompanyDetails] = useState<any>(null)
  const [detailsLoading, setDetailsLoading] = useState(false)

  const industries = [
    'all',
    'IT Services',
    'Product',
    'Consulting',
    'Finance',
    'E-commerce',
    'SaaS',
    'Other'
  ]

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
      return
    }
    fetchCompanies()
  }, [isAuthenticated])

  const fetchCompanies = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await apiClient.get('/api/v1/company-data/trending')
      const data = Array.isArray(response.data) ? response.data : response.data.companies || []
      setCompanies(data)
      setFilteredCompanies(data)
    } catch (err: any) {
      console.error('Failed to fetch companies:', err)
      setError('Failed to load companies. Please try again later.')
      // Fallback with sample data
      const sampleCompanies: Company[] = [
        { id: '1', name: 'TCS', industry: 'IT Services', placement_rate: 92, avg_salary: 8.5 },
        { id: '2', name: 'Infosys', industry: 'IT Services', placement_rate: 90, avg_salary: 8.2 },
        { id: '3', name: 'Wipro', industry: 'IT Services', placement_rate: 88, avg_salary: 8.0 },
        { id: '4', name: 'Microsoft India', industry: 'Product', placement_rate: 95, avg_salary: 18.5 },
        { id: '5', name: 'Google India', industry: 'Product', placement_rate: 93, avg_salary: 22.0 },
      ]
      setCompanies(sampleCompanies)
      setFilteredCompanies(sampleCompanies)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCompanyDetails = async (companyName: string) => {
    setDetailsLoading(true)
    try {
      // First try the TESS endpoint since it has more details
      const response = await apiClient.get(`/api/v1/tess/company/${companyName}`)
      setCompanyDetails(response.data)
    } catch (err) {
      console.error('Failed to fetch company details:', err)
      // Fallback - just show basic info
      setCompanyDetails(selectedCompany)
    } finally {
      setDetailsLoading(false)
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    filterCompanies(query, selectedIndustry)
  }

  const handleIndustryFilter = (industry: string) => {
    setSelectedIndustry(industry)
    filterCompanies(searchQuery, industry)
  }

  const filterCompanies = (search: string, industry: string) => {
    let filtered = companies.filter(c =>
      c.name.toLowerCase().includes(search.toLowerCase())
    )

    if (industry !== 'all') {
      filtered = filtered.filter(c => c.industry === industry)
    }

    setFilteredCompanies(filtered)
  }

  const handleViewDetails = (company: Company) => {
    setSelectedCompany(company)
    setShowDetails(true)
    fetchCompanyDetails(company.name)
  }

  const handleCloseDetails = () => {
    setShowDetails(false)
    setSelectedCompany(null)
    setCompanyDetails(null)
  }

  return (
    <>
      <Head>
        <title>Company Explorer | PrepEdge AI</title>
        <meta name="description" content="Browse and explore top companies" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 py-12">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-2">
              Explore Companies
            </h1>
            <p className="text-lg text-slate-600">
              Discover top hiring companies and their interview details
            </p>
          </div>

          {/* Search and Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="md:col-span-2 relative">
              <Search className="absolute left-4 top-3.5 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search companies..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-4 top-3.5 w-5 h-5 text-slate-400" />
              <select
                value={selectedIndustry}
                onChange={(e) => handleIndustryFilter(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-xl appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors shadow-sm"
              >
                {industries.map(industry => (
                  <option key={industry} value={industry}>
                    {industry === 'all' ? 'All Industries' : industry}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <p className="text-amber-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
              <span className="ml-3 text-slate-600">Loading companies...</span>
            </div>
          ) : filteredCompanies.length === 0 ? (
            <div className="text-center py-20">
              <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No companies found</h3>
              <p className="text-slate-600">Try adjusting your search or filters</p>
            </div>
          ) : (
            <>
              {/* Results Count */}
              <div className="mb-6 flex items-center justify-between">
                <p className="text-sm text-slate-600">
                  Showing <span className="font-semibold text-slate-900">{filteredCompanies.length}</span> companies
                </p>
              </div>

              {/* Companies Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCompanies.map((company, idx) => (
                  <div
                    key={company.id}
                    className="group bg-white dark:bg-slate-900 rounded-xl shadow-sm hover:shadow-xl transition-all duration-500 overflow-hidden border border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-400 transform hover:-translate-y-2 hover:scale-105 animate-fade-in"
                    style={{ animationDelay: `${idx * 50}ms` }}
                  >
                    {/* Card Header with Gradient */}
                    <div className="h-24 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative overflow-hidden">
                      <div className="absolute inset-0 opacity-20 group-hover:opacity-40 transition-opacity duration-500" />
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-500 transform group-hover:translate-x-full" />
                    </div>

                    {/* Card Content */}
                    <div className="relative px-6 pb-6">
                      {/* Company Name */}
                      <div className="flex items-start gap-4 -mt-8 mb-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-md group-hover:shadow-lg group-hover:scale-110 transition-all duration-500">
                          {company.name.substring(0, 2).toUpperCase()}
                        </div>
                        <div className="flex-1 pt-2">
                          <h3 className="text-lg font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors duration-300">
                            {company.name}
                          </h3>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{company.industry}</p>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="space-y-3 mb-6">
                        <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors duration-300">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-emerald-600" />
                            <span className="text-sm text-slate-600 dark:text-slate-300">Placement Rate</span>
                          </div>
                          <span className="font-bold text-emerald-600">{company.placement_rate}%</span>
                        </div>

                        {company.avg_salary && (
                          <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors duration-300">
                            <div className="flex items-center gap-2">
                              <Award className="w-4 h-4 text-amber-600" />
                              <span className="text-sm text-slate-600 dark:text-slate-300">Avg Salary</span>
                            </div>
                            <span className="font-bold text-amber-600">₹{company.avg_salary}L</span>
                          </div>
                        )}

                        {company.active_job_openings && (
                          <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 transition-colors duration-300">
                            <div className="flex items-center gap-2">
                              <Users className="w-4 h-4 text-blue-600" />
                              <span className="text-sm text-slate-600 dark:text-slate-300">Active Jobs</span>
                            </div>
                            <span className="font-bold text-blue-600">{company.active_job_openings}</span>
                          </div>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleViewDetails(company)}
                          className="flex-1 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium rounded-lg hover:shadow-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 text-sm group-hover:scale-105 transform"
                        >
                          View Details
                        </button>
                        {company.website && (
                          <a
                            href={company.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-2 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm flex items-center gap-1 group-hover:scale-105 transform"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Company Details Modal */}
        {showDetails && selectedCompany && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
              {/* Modal Header */}
              <div className="sticky top-0 bg-gradient-to-r from-indigo-500 to-purple-600 px-8 py-6 flex items-center justify-between">
                <h2 className="text-2xl font-heading font-bold text-white">
                  {selectedCompany.name}
                </h2>
                <button
                  onClick={handleCloseDetails}
                  className="text-white/80 hover:text-white text-2xl leading-none"
                >
                  ×
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-8">
                {detailsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                    <span className="ml-3 text-slate-600">Loading details...</span>
                  </div>
                ) : companyDetails ? (
                  <div className="space-y-6">
                    {/* Basic Info */}
                    <div>
                      <h3 className="text-lg font-bold text-slate-900 mb-4">Company Profile</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <p className="text-sm text-slate-600 mb-1">Industry</p>
                          <p className="font-semibold text-slate-900">{selectedCompany.industry}</p>
                        </div>
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <p className="text-sm text-slate-600 mb-1">Placement Rate</p>
                          <p className="font-semibold text-emerald-600">{selectedCompany.placement_rate}%</p>
                        </div>
                        {selectedCompany.avg_salary && (
                          <div className="p-4 bg-slate-50 rounded-lg">
                            <p className="text-sm text-slate-600 mb-1">Avg Salary</p>
                            <p className="font-semibold text-amber-600">₹{selectedCompany.avg_salary}L</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Job Openings */}
                    {companyDetails.job_openings && companyDetails.job_openings.length > 0 && (
                      <div>
                        <h3 className="text-lg font-bold text-slate-900 mb-4">
                          Active Job Openings ({companyDetails.job_openings.length})
                        </h3>
                        <div className="space-y-3 max-h-48 overflow-y-auto">
                          {companyDetails.job_openings.map((job: any, idx: number) => (
                            <div key={idx} className="p-3 bg-blue-50 border border-blue-100 rounded-lg">
                              <p className="font-semibold text-slate-900">{job.job_title || job.role}</p>
                              <p className="text-sm text-slate-600">
                                {job.seniority_level} • {job.location}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Interview Questions */}
                    {companyDetails.questions && companyDetails.questions.length > 0 && (
                      <div>
                        <h3 className="text-lg font-bold text-slate-900 mb-4">
                          Interview Questions ({companyDetails.questions.length})
                        </h3>
                        <p className="text-sm text-slate-600 mb-3">
                          This company has {companyDetails.questions.length} interview questions in our database
                        </p>
                        <button className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm font-medium">
                          Browse Questions →
                        </button>
                      </div>
                    )}

                    {/* Salary Data */}
                    {companyDetails.salary_data && companyDetails.salary_data.length > 0 && (
                      <div>
                        <h3 className="text-lg font-bold text-slate-900 mb-4">
                          Salary Ranges by Role
                        </h3>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {companyDetails.salary_data.map((salary: any, idx: number) => (
                            <div key={idx} className="p-3 bg-amber-50 border border-amber-100 rounded-lg text-sm">
                              <p className="font-semibold text-slate-900">{salary.role}</p>
                              <p className="text-slate-600">
                                ₹{salary.min_salary}L - ₹{salary.max_salary}L ({salary.seniority_level})
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-slate-600">Unable to load full company details.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
