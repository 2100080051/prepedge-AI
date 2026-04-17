import { CheckCircle2, Target, MapPin, Briefcase } from 'lucide-react'

interface MatchBreakdownProps {
  breakdown: {
    role: number
    skills: number
    location: number
    company: number
  }
}

export default function MatchBreakdown({ breakdown }: MatchBreakdownProps) {
  const categories = [
    { 
      label: 'Role Match', 
      value: breakdown.role, 
      color: 'bg-indigo-500', 
      bg: 'bg-indigo-100', 
      icon: <Briefcase className="w-4 h-4 text-indigo-500" />
    },
    { 
      label: 'Skills Match', 
      value: breakdown.skills, 
      color: 'bg-purple-500', 
      bg: 'bg-purple-100',
      icon: <Target className="w-4 h-4 text-purple-500" />
    },
    { 
      label: 'Location Match', 
      value: breakdown.location, 
      color: 'bg-emerald-500', 
      bg: 'bg-emerald-100',
      icon: <MapPin className="w-4 h-4 text-emerald-500" />
    },
    { 
      label: 'Company Match', 
      value: breakdown.company, 
      color: 'bg-amber-500', 
      bg: 'bg-amber-100',
      icon: <CheckCircle2 className="w-4 h-4 text-amber-500" />
    },
  ]

  return (
    <div className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm animate-scale-in">
      <h2 className="text-xl font-bold font-heading text-slate-900 mb-6 flex items-center gap-2">
        Profile Match Breakdown
      </h2>
      <div className="space-y-6">
        {categories.map(({ label, value, color, bg, icon }) => (
          <div key={label} className="group">
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-slate-700 flex items-center gap-2">
                <div className={`p-1.5 rounded-lg ${bg}`}>
                   {icon}
                </div>
                {label}
              </span>
              <span className={`text-lg font-bold font-heading ${value >= 70 ? 'text-emerald-600' : value >= 40 ? 'text-amber-600' : 'text-slate-500'}`}>
                {value}%
              </span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden ring-1 ring-inset ring-slate-200 shadow-inner">
              <div
                className={`${color} h-full transition-all duration-1000 ease-out rounded-full shadow-sm`}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
