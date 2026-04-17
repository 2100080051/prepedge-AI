import { useEffect, useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { ArrowLeft, Search, Filter, Database } from 'lucide-react'
import apiClient from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'next/router'
import UnansweredQuestions from '@/components/admin/answer-manager/UnansweredQuestions'
import AnswerForm from '@/components/admin/answer-manager/AnswerForm'
import AnswerStats from '@/components/admin/answer-manager/AnswerStats'

export default function AnswerManagerPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuthStore()

  const [questions, setQuestions] = useState<any[]>([])
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterDifficulty, setFilterDifficulty] = useState('all')

  // Auth Guard
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
    } else if (user && !user.is_admin) {
      router.push('/dashboard')
    } else if (user && user.is_admin) {
      fetchUnanswered()
      fetchStats()
    }
  }, [isAuthenticated, user])

  async function fetchUnanswered() {
    try {
      const response = await apiClient.get('/api/v1/questions/admin/unanswered')
      setQuestions(response.data.questions || response.data)
    } catch (error) {
      console.error('Failed to fetch unanswered questions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  async function fetchStats() {
    try {
      const response = await apiClient.get('/api/v1/questions/stats/answer-coverage')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  async function handleSaveAnswer(questionId: number, answerData: object) {
    try {
      setIsSaving(true)
      await apiClient.post(`/api/v1/questions/${questionId}/answer`, answerData)

      // Update local state by removing answered question
      setQuestions(prev => prev.filter(q => q.id !== questionId))
      setSelectedQuestion(null)
      
      // Refresh stats
      fetchStats()

      // In real app, standard toast plugin here
      alert('Answer saved successfully!')
    } catch (error) {
      console.error('Error saving answer:', error)
      alert('Failed to save answer')
    } finally {
      setIsSaving(false)
    }
  }

  const filteredQuestions = questions.filter(q => {
    const title = q.title || q.question_text || q.question || ''
    const matchesSearch = title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDifficulty = filterDifficulty === 'all' || q.difficulty === filterDifficulty
    return matchesSearch && matchesDifficulty
  })

  // Block rendering until auth resolves
  if (!user || !user.is_admin) return null

  return (
    <>
      <Head>
        <title>Answer Manager | Admin PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          
          {/* Header */}
          <div>
            <Link href="/admin" className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium mb-4 transition-colors">
              <ArrowLeft className="w-4 h-4" /> Back to Admin Hub
            </Link>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold font-heading text-slate-900">Answer Manager</h1>
                <p className="text-slate-500 mt-1">Review unanswered questions and build the knowledge base.</p>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && <AnswerStats stats={stats} />}

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            {/* Left Column: Filter & List */}
            <div className="lg:col-span-1 space-y-4">
              
              {/* Filters */}
              <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 space-y-3">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-4 w-4 text-slate-400" />
                  </div>
                  <input
                    type="text"
                    placeholder="Search questions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                  />
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Filter className="h-4 w-4 text-slate-400" />
                  </div>
                  <select
                    value={filterDifficulty}
                    onChange={(e) => setFilterDifficulty(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all appearance-none"
                  >
                    <option value="all">All Difficulties</option>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              {/* List */}
              <UnansweredQuestions
                questions={filteredQuestions}
                selectedId={selectedQuestion?.id}
                onSelectQuestion={setSelectedQuestion}
                isLoading={isLoading}
              />
            </div>

            {/* Right Column: Answer Form */}
            <div className="lg:col-span-2">
              {selectedQuestion ? (
                <AnswerForm
                  question={selectedQuestion}
                  onSave={handleSaveAnswer}
                  isSaving={isSaving}
                />
              ) : (
                <div className="flex flex-col items-center justify-center p-12 h-96 bg-white border border-slate-200 border-dashed rounded-2xl text-center">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                    <Database className="w-8 h-8 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-800 mb-1">Select a Question</h3>
                  <p className="text-slate-500 max-w-sm">Choose an unanswered question from the left panel to provide its answer, explanation, and code solution.</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </>
  )
}
