import { useState } from 'react'

interface AnswerFormProps {
  question: any
  onSave: (id: number, data: any) => Promise<void>
  isSaving: boolean
}

export default function AnswerForm({ question, onSave, isSaving }: AnswerFormProps) {
  const [formData, setFormData] = useState({
    answer_text: '',
    explanation: '',
    solution_code: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validateForm() {
    const newErrors: Record<string, string> = {}
    if (!formData.answer_text.trim()) newErrors.answer_text = 'Correct Answer text is required'
    if (!formData.explanation.trim()) newErrors.explanation = 'Explanation is required'
    return newErrors
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const newErrors = validateForm()
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    await onSave(question.id, formData)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6 animate-scale-in">
      <div className="border-b border-slate-100 pb-5">
        <h2 className="text-sm font-semibold text-indigo-600 uppercase tracking-wider mb-2">Provide Answer For:</h2>
        <h3 className="text-xl font-bold text-slate-900 leading-snug">
          {question.question_text || question.title || question.question}
        </h3>
      </div>

      {/* Answer Text */}
      <div>
        <label className="block text-sm font-bold text-slate-700 mb-2">Correct Answer <span className="text-rose-500">*</span></label>
        <textarea
          value={formData.answer_text}
          onChange={(e) => {
            setFormData({ ...formData, answer_text: e.target.value })
            if (errors.answer_text) setErrors({ ...errors, answer_text: '' })
          }}
          placeholder="Enter the correct answer..."
          rows={4}
          className={`w-full px-4 py-3 border rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all ${
            errors.answer_text ? 'border-rose-300 focus:border-rose-500 ring-rose-500/20' : 'border-slate-200 focus:border-indigo-500'
          }`}
        />
        {errors.answer_text && <p className="text-rose-500 text-sm mt-1.5 font-medium">{errors.answer_text}</p>}
      </div>

      {/* Explanation */}
      <div>
        <label className="block text-sm font-bold text-slate-700 mb-2">Explanation <span className="text-rose-500">*</span></label>
        <textarea
          value={formData.explanation}
          onChange={(e) => {
            setFormData({ ...formData, explanation: e.target.value })
            if (errors.explanation) setErrors({ ...errors, explanation: '' })
          }}
          placeholder="Explain why this is the correct answer and the approach..."
          rows={4}
          className={`w-full px-4 py-3 border rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all ${
            errors.explanation ? 'border-rose-300 focus:border-rose-500 ring-rose-500/20' : 'border-slate-200 focus:border-indigo-500'
          }`}
        />
        {errors.explanation && <p className="text-rose-500 text-sm mt-1.5 font-medium">{errors.explanation}</p>}
      </div>

      {/* Code Solution */}
      <div>
        <label className="block text-sm font-bold text-slate-700 mb-2">
          Code Solution <span className="text-slate-400 font-normal">(Optional)</span>
        </label>
        <textarea
          value={formData.solution_code}
          onChange={(e) => setFormData({ ...formData, solution_code: e.target.value })}
          placeholder="def solution():\n    return 'best answers'"
          rows={6}
          spellCheck={false}
          className="w-full px-4 py-3 border border-slate-700 rounded-xl bg-slate-900 text-slate-100 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
        />
      </div>

      {/* Buttons */}
      <div className="flex gap-3 pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={() => {
            setFormData({ answer_text: '', explanation: '', solution_code: '' })
            setErrors({})
          }}
          className="px-6 py-3 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-xl font-bold transition-colors"
        >
          Clear
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-bold shadow-sm shadow-indigo-200 transition-colors flex items-center justify-center gap-2"
        >
          {isSaving && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
          {isSaving ? 'Saving Answer...' : 'Save Answer'}
        </button>
      </div>
    </form>
  )
}
