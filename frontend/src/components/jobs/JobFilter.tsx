import { Filter, DollarSign, Target } from 'lucide-react'

interface JobFilterProps {
  filters: {
    minScore: number
    maxSalary: number | null
    jobTypes: string[]
    locations: string[]
  }
  onChange: (filters: any) => void
}

export default function JobFilter({ filters, onChange }: JobFilterProps) {
  
  const updateFilter = (key: keyof typeof filters, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const toggleArrayItem = (key: 'jobTypes' | 'locations', value: string) => {
    const arr = [...filters[key]]
    const idx = arr.indexOf(value)
    if (idx > -1) arr.splice(idx, 1)
    else arr.push(value)
    updateFilter(key, arr)
  }

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-6">
      
      <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
        <Filter className="w-5 h-5 text-indigo-600" />
        <h3 className="font-bold text-slate-900 font-heading">Refine Matches</h3>
      </div>

      {/* Min Score Filter */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Target className="w-3 h-3" /> Min Match Score
        </h4>
        <div className="flex items-center justify-between gap-4">
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={filters.minScore}
            onChange={(e) => updateFilter('minScore', Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
          <span className="text-sm font-bold bg-indigo-50 text-indigo-700 px-2 py-1 rounded w-12 text-center">
            {filters.minScore}%
          </span>
        </div>
      </div>

      {/* Job Type Filter */}
      <div className="space-y-3 pt-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Job Type</h4>
        <div className="space-y-2">
          {['Full-time', 'Contract', 'Internship', 'Freelance'].map(type => (
            <label key={type} className="flex items-center gap-2 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={filters.jobTypes.includes(type)}
                onChange={() => toggleArrayItem('jobTypes', type)}
                className="w-4 h-4 text-indigo-600 bg-slate-100 border-slate-300 rounded focus:ring-indigo-500 cursor-pointer"
              />
              <span className="text-sm text-slate-600 group-hover:text-slate-900 font-medium transition-colors">{type}</span>
            </label>
          ))}
        </div>
      </div>

      <button 
        onClick={() => onChange({ minScore: 0, maxSalary: null, jobTypes: [], locations: [] })}
        className="w-full py-2.5 mt-2 bg-slate-50 hover:bg-slate-100 text-slate-600 font-bold text-sm rounded-xl border border-slate-200 transition-colors"
      >
        Clear Filters
      </button>

    </div>
  )
}
