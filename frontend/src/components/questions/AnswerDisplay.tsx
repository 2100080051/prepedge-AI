import { useState, useEffect } from 'react'
import CodeBlock from '@/components/shared/CodeBlock'
import { CheckCircle2, Lightbulb, Code2, AlertTriangle, AlertCircle } from 'lucide-react'
import apiClient from '@/lib/api'

interface AnswerDisplayProps {
  questionId: number
}

interface Answer {
  answer_text: string
  explanation: string
  solution_code?: string
  difficulty: string
}

export default function AnswerDisplay({ questionId }: AnswerDisplayProps) {
  const [answer, setAnswer] = useState<Answer | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnswer()
  }, [questionId])

  async function fetchAnswer() {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.get<Answer>(`/api/v1/questions/${questionId}/reveal-answer`)
      setAnswer(response.data)
    } catch (err: any) {
      console.error('Failed to fetch answer:', err)
      setError(err.response?.data?.detail || 'Failed to load the answer. It might not be available yet.')
    } finally {
      setIsLoading(false)
    }
  }

  function getDifficultyColor(diff: string) {
    if (diff === 'easy') return 'bg-green-100 text-green-700 border-green-200'
    if (diff === 'medium') return 'bg-amber-100 text-amber-700 border-amber-200'
    if (diff === 'hard') return 'bg-red-100 text-red-700 border-red-200'
    return 'bg-slate-100 text-slate-700 border-slate-200'
  }

  if (isLoading) {
    return (
      <div className="mt-4 p-6 bg-slate-50 border border-slate-100 rounded-xl space-y-4 animate-pulse">
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-full"></div>
        <div className="h-4 bg-slate-200 rounded w-5/6"></div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="mt-4 p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl flex items-start gap-3 text-sm">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <p>{error}</p>
      </div>
    )
  }

  if (!answer) return null

  return (
    <div className="mt-5 space-y-5 p-6 bg-slate-50/80 rounded-2xl border border-slate-200">
      
      {/* Correct Answer */}
      <div>
        <h4 className="font-semibold text-emerald-600 flex items-center gap-2 mb-2 pb-2 border-b border-emerald-100">
          <CheckCircle2 className="w-5 h-5" /> Correct Answer
        </h4>
        <div className="text-slate-700 leading-relaxed whitespace-pre-wrap pl-[28px]">
          {answer.answer_text}
        </div>
      </div>

      {/* Explanation */}
      {answer.explanation && (
        <div className="pt-2">
          <h4 className="font-semibold text-amber-600 flex items-center gap-2 mb-2 pb-2 border-b border-amber-100">
            <Lightbulb className="w-5 h-5" /> Explanation
          </h4>
          <div className="text-slate-700 leading-relaxed whitespace-pre-wrap pl-[28px]">
            {answer.explanation}
          </div>
        </div>
      )}

      {/* Code Solution */}
      {answer.solution_code && (
        <div className="pt-2">
          <h4 className="font-semibold text-indigo-600 flex items-center gap-2 mb-3 pb-2 border-b border-indigo-100">
            <Code2 className="w-5 h-5" /> Code Solution
          </h4>
          <div className="pl-[28px]">
            <CodeBlock 
              code={answer.solution_code} 
              language="javascript" // Can be made dynamic if API provides language
            />
          </div>
        </div>
      )}

      {/* Meta Footer */}
      <div className="pt-4 mt-2 border-t border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Difficulty</span>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize ${getDifficultyColor(answer.difficulty)}`}>
            {answer.difficulty}
          </span>
        </div>
      </div>
      
    </div>
  )
}
