import Link from 'next/link';
import { BookOpen } from 'lucide-react';

const DIFF_BADGE: Record<string, string> = {
  Easy:   'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Hard:   'bg-rose-100 text-rose-700 border-rose-200',
};

interface PracticeSidebarProps {
  timeSpent: number;
  question: any;
  similar: any[];
}

export default function PracticeSidebar({ timeSpent, question, similar }: PracticeSidebarProps) {
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Stats Card */}
      <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition-shadow">
        <h3 className="font-bold text-slate-900 mb-4">Question Info</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-slate-500">Timer</span>
            <span className="font-mono text-indigo-600 font-bold bg-indigo-50 px-2 py-1 rounded-md border border-indigo-100">
              {formatTime(timeSpent)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Company</span>
            <span className="font-semibold text-slate-800">{question?.company_name || question?.company}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Round</span>
            <span className="font-semibold text-slate-800">{question?.round_type}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Difficulty</span>
            <span className={`px-2 py-0.5 rounded-lg text-xs border font-bold ${DIFF_BADGE[question?.difficulty] || 'bg-slate-100 text-slate-600'}`}>
              {question?.difficulty}
            </span>
          </div>
          {question?.frequency_score && (
            <div className="flex justify-between">
              <span className="text-slate-500">Frequency</span>
              <span className="font-semibold text-slate-800">{question?.frequency_score}/10</span>
            </div>
          )}
        </div>
      </div>

      {/* Similar Questions */}
      {similar && similar.length > 0 && (
        <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition-shadow">
          <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-500" />
            Similar Questions
          </h3>
          <div className="space-y-3">
            {similar.slice(0, 4).map(q => (
              <Link key={q.id} href={`/questions/${q.id}/practice`}
                className="block p-3 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-200 border border-slate-100 rounded-xl transition-all">
                <p className="text-sm text-slate-700 font-medium line-clamp-2 mb-1">{q.question}</p>
                <div className="flex gap-1.5">
                  <span className={`px-1.5 py-0.5 text-xs rounded border font-semibold ${DIFF_BADGE[q.difficulty] || 'bg-slate-100 text-slate-600'}`}>
                    {q.difficulty}
                  </span>
                  <span className="text-xs text-slate-400">{q.company}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
