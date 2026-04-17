import { useState } from 'react'
import { MapPin, Briefcase, DollarSign, Target, ExternalLink } from 'lucide-react'

export interface Job {
  id: number
  job_title: string
  company: string
  location: string
  job_type: string
  experience_required: string
  salary_range?: string
  skills_required: string[]
  url: string
  source: string
  match_score: number
  match_breakdown: {
    role: number
    skills: number
    location: number
    company: number
  }
}

interface JobCardProps {
  job: Job
  onViewDetails?: (jobId: number) => void
  onApply?: (jobId: number) => void
}

export default function JobCard({ job, onViewDetails, onApply }: JobCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [hasApplied, setHasApplied] = useState(false)

  // Color based on match score
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500'
    if (score >= 60) return 'bg-amber-500'
    if (score >= 30) return 'bg-orange-500'
    return 'bg-rose-500'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-50 text-emerald-700 border-emerald-100'
    if (score >= 60) return 'bg-amber-50 text-amber-700 border-amber-100'
    if (score >= 30) return 'bg-orange-50 text-orange-700 border-orange-100'
    return 'bg-rose-50 text-rose-700 border-rose-100'
  }

  async function handleViewDetails() {
    // We would fire the view endpoint here to record analytics
    onViewDetails?.(job.id)
  }

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="glass-card p-6 border border-slate-200 rounded-2xl hover:shadow-lg transition-all cursor-pointer relative overflow-hidden group"
      onClick={handleViewDetails}
    >
      {/* Top Gradient Bar */}
      <div className={`absolute top-0 left-0 right-0 h-1 transition-all duration-300 ${isHovered ? getScoreColor(job.match_score) : 'bg-transparent'}`} />

      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div className="flex-1 pr-4">
          <h3 className="text-xl font-bold font-heading text-slate-900 group-hover:text-indigo-600 transition-colors">
            {job.job_title}
          </h3>
          <p className="text-base text-slate-500 font-medium mt-1">{job.company}</p>
        </div>
        
        {/* Match Score Badge */}
        <div className={`flex flex-col items-center justify-center p-2 rounded-xl border ${getScoreBg(job.match_score)} flex-shrink-0 text-center min-w-[70px] shadow-sm`}>
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-70 mb-0.5">Match</span>
          <span className="font-bold text-xl leading-none">{job.match_score}%</span>
        </div>
      </div>

      {/* Job Details Meta */}
      <div className="flex flex-wrap gap-4 text-sm font-medium text-slate-600 mb-5">
        <div className="flex items-center gap-1.5 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
          <MapPin className="w-4 h-4 text-slate-400" /> {job.location || 'Remote'}
        </div>
        <div className="flex items-center gap-1.5 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
          <Briefcase className="w-4 h-4 text-slate-400" /> {job.job_type || 'Full-time'}
        </div>
        {job.salary_range && (
          <div className="flex items-center gap-1.5 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <DollarSign className="w-4 h-4 text-slate-400" /> {job.salary_range}
          </div>
        )}
      </div>

      {/* Skills */}
      <div className="flex items-start gap-2 mb-4">
         <Target className="w-4 h-4 text-slate-400 mt-1 flex-shrink-0" />
         <div className="flex flex-wrap gap-1.5">
            {job.skills_required.slice(0, 5).map((skill, i) => (
              <span key={i} className="px-2.5 py-0.5 text-xs bg-indigo-50 text-indigo-700 border border-indigo-100/50 rounded-md font-medium">
                {skill}
              </span>
            ))}
            {job.skills_required.length > 5 && (
              <span className="px-2 py-0.5 text-xs font-medium text-slate-500 bg-slate-100 rounded-md">
                +{job.skills_required.length - 5} more
              </span>
            )}
         </div>
      </div>

      {/* Match Breakdown (Expanded on hover) */}
      <div className={`grid grid-cols-4 gap-2 text-xs border-y border-slate-100 overflow-hidden transition-all duration-300 ease-in-out ${isHovered ? 'py-4 my-4 max-h-[100px] opacity-100' : 'max-h-0 py-0 my-0 opacity-0 border-transparent'}`}>
        <div className="text-center">
            <p className="font-bold text-slate-800 text-sm">{job.match_breakdown.role}%</p>
            <p className="text-slate-500 uppercase tracking-wider text-[10px] mt-0.5">Role</p>
        </div>
        <div className="text-center border-l border-slate-100">
            <p className="font-bold text-slate-800 text-sm">{job.match_breakdown.skills}%</p>
            <p className="text-slate-500 uppercase tracking-wider text-[10px] mt-0.5">Skills</p>
        </div>
        <div className="text-center border-l border-slate-100">
            <p className="font-bold text-slate-800 text-sm">{job.match_breakdown.location}%</p>
            <p className="text-slate-500 uppercase tracking-wider text-[10px] mt-0.5">Location</p>
        </div>
        <div className="text-center border-l border-slate-100">
            <p className="font-bold text-slate-800 text-sm">{job.match_breakdown.company}%</p>
            <p className="text-slate-500 uppercase tracking-wider text-[10px] mt-0.5">Company</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleViewDetails();
          }}
          className="flex-1 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-sm font-bold shadow-sm transition-colors"
        >
          View Details
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setHasApplied(true);
            window.open(job.url, '_blank', 'noopener,noreferrer');
            onApply?.(job.id);
          }}
          className={`flex-1 px-4 py-2.5 rounded-xl text-sm font-bold shadow-sm transition-colors flex items-center justify-center gap-2 ${
            hasApplied
              ? 'bg-emerald-500 text-white shadow-emerald-500/30'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-200'
          }`}
        >
          {hasApplied ? (
            'Applied ✓'
          ) : (
            <>Apply Now <ExternalLink className="w-4 h-4" /></>
          )}
        </button>
      </div>
    </div>
  )
}
