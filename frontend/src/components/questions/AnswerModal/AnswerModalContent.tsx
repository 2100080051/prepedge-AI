import CodeBlock from '@/components/shared/CodeBlock'
import { CheckCircle2, Lightbulb, Code2 } from 'lucide-react'

// Defining Answer here as well
interface Answer {
  answer_text: string
  explanation: string
  solution_code?: string
  difficulty: string
}

interface AnswerModalContentProps {
  answer: Answer
}

export default function AnswerModalContent({ answer }: AnswerModalContentProps) {
  return (
    <div className="space-y-8">
      {/* Answer */}
      <section>
        <h3 className="text-lg font-semibold text-emerald-600 flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-5 h-5" /> Correct Answer
        </h3>
        <div className="text-slate-700 leading-relaxed text-lg whitespace-pre-wrap pl-[28px]">
          {answer.answer_text}
        </div>
      </section>

      {/* Explanation */}
      {answer.explanation && (
        <section>
          <h3 className="text-lg font-semibold text-amber-600 flex items-center gap-2 mb-3">
            <Lightbulb className="w-5 h-5" /> Explanation
          </h3>
          <div className="text-slate-700 leading-relaxed whitespace-pre-wrap pl-[28px]">
            {answer.explanation}
          </div>
        </section>
      )}

      {/* Code Solution */}
      {answer.solution_code && (
        <section>
          <h3 className="text-lg font-semibold text-indigo-600 flex items-center gap-2 mb-3">
            <Code2 className="w-5 h-5" /> Code Solution
          </h3>
          <div className="pl-[28px]">
            <CodeBlock code={answer.solution_code} language="javascript" />
          </div>
        </section>
      )}
    </div>
  )
}
