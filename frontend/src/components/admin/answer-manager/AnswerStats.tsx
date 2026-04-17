import { Database, CheckCircle2, Target, AlertCircle } from 'lucide-react'

export default function AnswerStats({ stats }: { stats: any }) {
  const coveragePercentage = stats.total_questions 
    ? Math.round((stats.answered_questions / stats.total_questions) * 100) 
    : 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Questions"
        value={stats.total_questions || 0}
        icon={<Database className="w-6 h-6" />}
        color="slate"
      />
      <StatCard
        title="Answered"
        value={stats.answered_questions || 0}
        icon={<CheckCircle2 className="w-6 h-6" />}
        color="emerald"
      />
      <StatCard
        title="Coverage"
        value={`${coveragePercentage}%`}
        icon={<Target className="w-6 h-6" />}
        color="indigo"
      />
      <StatCard
        title="Remaining"
        value={(stats.total_questions || 0) - (stats.answered_questions || 0)}
        icon={<AlertCircle className="w-6 h-6" />}
        color="amber"
      />
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  icon, 
  color 
}: { 
  title: string, 
  value: string | number, 
  icon: React.ReactNode, 
  color: 'slate' | 'emerald' | 'indigo' | 'amber' 
}) {
  
  const colorStyles = {
    slate: 'bg-slate-50 border-slate-200 text-slate-700 icon-slate-500',
    emerald: 'bg-emerald-50 border-emerald-200 text-emerald-800 icon-emerald-500',
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-800 icon-indigo-500',
    amber: 'bg-amber-50 border-amber-200 text-amber-800 icon-amber-500'
  }

  const activeStyle = colorStyles[color]

  return (
    <div className={`p-5 rounded-2xl border ${activeStyle.split(' ')[0]} ${activeStyle.split(' ')[1]} shadow-sm flex items-center justify-between`}>
      <div>
        <p className={`text-sm font-semibold mb-1 opacity-80 ${activeStyle.split(' ')[2]}`}>{title}</p>
        <p className={`text-3xl font-bold font-heading ${activeStyle.split(' ')[2]}`}>{value}</p>
      </div>
      <div className={`p-3 rounded-xl bg-white/60 shadow-sm ${activeStyle.split(' ')[3].replace('icon-', 'text-')}`}>
        {icon}
      </div>
    </div>
  )
}
