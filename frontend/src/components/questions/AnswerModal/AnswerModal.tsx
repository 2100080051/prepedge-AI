import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import apiClient from '@/lib/api'
import AnswerModalContent from './AnswerModalContent'
import { X, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'

interface AnswerModalProps {
  isOpen: boolean
  questionId: number
  totalQuestions?: number
  currentIdx?: number // 1-indexed for display
  onClose: () => void
  onNavigate?: (direction: 'prev' | 'next') => void
}

export default function AnswerModal({
  isOpen,
  questionId,
  totalQuestions,
  currentIdx,
  onClose,
  onNavigate
}: AnswerModalProps) {
  const [answer, setAnswer] = useState(null)
  const [question, setQuestion] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!isOpen) return

    fetchData()
  }, [isOpen, questionId])

  async function fetchData() {
    try {
      setIsLoading(true)
      setAnswer(null)      
      
      // Fetch question details
      const qRes = await apiClient.get(`/api/v1/questions/${questionId}`)
      setQuestion(qRes.data)

      // Fetch answer (this uses your existing API endpoint)
      const aRes = await apiClient.get(`/api/v1/questions/${questionId}/reveal-answer`)
      setAnswer(aRes.data)
    } catch (error) {
      console.error('Failed to fetch:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft') onNavigate?.('prev')
      if (e.key === 'ArrowRight') onNavigate?.('next')
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose, onNavigate])

  // Prevent background scrolling
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => { document.body.style.overflow = 'unset' }
  }, [isOpen])

  if (!isOpen) return null

  const modalContent = (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 animate-fade-in">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-4xl bg-white rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-scale-in">
        
        {/* Header */}
        <div className="flex-shrink-0 bg-slate-50 border-b border-slate-200 p-5 sm:p-6 flex justify-between items-start gap-4">
          <h2 className="text-xl sm:text-2xl font-bold font-heading text-slate-900 leading-snug">
            {question?.question_text || 'Loading question...'}
          </h2>
          <button
            onClick={onClose}
            className="flex-shrink-0 p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-xl transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 custom-scrollbar">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
              <p>Loading the correct answer...</p>
            </div>
          ) : answer ? (
            <AnswerModalContent answer={answer} />
          ) : (
            <div className="text-center py-20">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
                <X className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-1">Answer Not Available</h3>
              <p className="text-slate-500">The correct answer for this question has not been provided yet.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {onNavigate && (
          <div className="flex-shrink-0 bg-slate-50 border-t border-slate-200 p-5 sm:p-6 flex justify-between items-center gap-4">
            <button
              onClick={() => onNavigate('prev')}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl font-medium shadow-sm transition-colors focus:ring-2 outline-none"
            >
              <ChevronLeft className="w-4 h-4 ml--1" />
              <span className="hidden sm:inline">Previous Question</span>
            </button>
            
            {totalQuestions && currentIdx && (
              <span className="text-sm font-medium text-slate-500 bg-slate-200 px-3 py-1 rounded-full">
                {currentIdx} of {totalQuestions}
              </span>
            )}
            
            <button
              onClick={() => onNavigate('next')}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium shadow-sm shadow-indigo-200 transition-colors focus:ring-2 outline-none focus:ring-indigo-500/20"
            >
              <span className="hidden sm:inline">Next Question</span>
              <ChevronRight className="w-4 h-4 mr--1" />
            </button>
          </div>
        )}
      </div>
    </div>
  )

  // Use portal if document is defined (browser mode)
  if (typeof document !== 'undefined') {
    return createPortal(modalContent, document.body)
  }
  return null
}
