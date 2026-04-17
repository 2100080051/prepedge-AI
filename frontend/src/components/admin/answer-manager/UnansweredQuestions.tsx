export default function UnansweredQuestions({
  questions,
  selectedId,
  onSelectQuestion,
  isLoading
}: {
  questions: any[]
  selectedId?: number
  onSelectQuestion: (q: any) => void
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl shadow-sm border border-slate-200">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3" />
        <p className="text-slate-500 font-medium">Loading questions...</p>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="p-8 text-center bg-emerald-50 rounded-2xl border border-emerald-100">
        <div className="inline-flex w-12 h-12 bg-emerald-100 rounded-full items-center justify-center mb-3">
          <span className="text-emerald-600 text-xl">🎉</span>
        </div>
        <h3 className="font-bold text-emerald-800 mb-1">All caught up!</h3>
        <p className="text-emerald-600 font-medium text-sm">All questions have answers assigned.</p>
      </div>
    )
  }

  function getDiffColor(diff: string) {
    if (diff === 'easy') return 'bg-emerald-100 text-emerald-700'
    if (diff === 'medium') return 'bg-amber-100 text-amber-700'
    if (diff === 'hard') return 'bg-rose-100 text-rose-700'
    return 'bg-slate-100 text-slate-700'
  }

  return (
    <div className="space-y-3 max-h-[800px] overflow-y-auto pr-2 custom-scrollbar">
      {questions.map(question => (
        <button
          key={question.id}
          onClick={() => onSelectQuestion(question)}
          className={`w-full text-left p-4 rounded-xl border transition-all ${
            selectedId === question.id
              ? 'bg-indigo-50 border-indigo-300 ring-1 ring-indigo-300 shadow-sm'
              : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
          }`}
        >
          <p className="font-semibold text-slate-800 leading-snug line-clamp-2 mb-3">
            {question.question_text || question.title || question.question}
          </p>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ${getDiffColor(question.difficulty)}`}>
              {question.difficulty}
            </span>
            <span className="text-xs text-slate-500 font-medium px-2 py-0.5 bg-slate-100 rounded">
              {question.category || question.company}
            </span>
            {question.round_type && (
               <span className="text-xs text-slate-500 font-medium px-2 py-0.5 border border-slate-200 rounded">
                 {question.round_type}
               </span>
            )}
          </div>
        </button>
      ))}
    </div>
  )
}
