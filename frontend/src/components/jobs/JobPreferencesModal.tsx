import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { X, Briefcase, MapPin, Code2, DollarSign, Target, Clock, Loader2 } from 'lucide-react'
import apiClient from '@/lib/api'
import ReactSlider from 'react-slider'

interface JobPreferencesModalProps {
  isOpen: boolean
  onClose: () => void
  onSaved?: () => void
}

export default function JobPreferencesModal({ isOpen, onClose, onSaved }: JobPreferencesModalProps) {
  const [formData, setFormData] = useState({
    desired_roles: [] as string[],
    desired_companies: [] as string[],
    desired_locations: [] as string[],
    skills: [] as string[],
    experience_level: 'entry',
    preferred_job_type: [] as string[],
    salary_expectation_min: 0,
    salary_expectation_max: 0,
    min_match_score: 60,
    notification_frequency: 'daily',
    notification_time: '09:00'
  })

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  // Temporary inputs for arrays
  const [inputs, setInputs] = useState({ role: '', company: '', location: '', skill: '' })

  useEffect(() => {
    if (isOpen) fetchPreferences()
  }, [isOpen])

  async function fetchPreferences() {
    setIsLoading(true)
    try {
      const res = await apiClient.get('/api/v1/jobs/user/job-preferences')
      if (res.data) {
        setFormData({
          ...formData, // Fallbacks
          ...res.data
        })
      }
    } catch (e) {
      console.error('Failed to load preferences:', e)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSaving(true)
    try {
      await apiClient.post('/api/v1/jobs/user/job-preferences', formData)
      alert('Preferences saved successfully!')
      onSaved?.()
      onClose()
    } catch (error) {
      console.error('Failed to save preferences:', error)
      alert('Failed to save preferences.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddArrayItem = (field: keyof typeof formData, value: string) => {
    if (!value.trim()) return
    const current = formData[field] as string[]
    if (!current.includes(value.trim())) {
      setFormData({ ...formData, [field]: [...current, value.trim()] })
    }
  }

  const handleRemoveArrayItem = (field: keyof typeof formData, value: string) => {
    const current = formData[field] as string[]
    setFormData({ ...formData, [field]: current.filter(v => v !== value) })
  }

  const handleKeyDown = (e: React.KeyboardEvent, field: keyof typeof formData, inputKey: keyof typeof inputs) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddArrayItem(field, inputs[inputKey])
      setInputs({ ...inputs, [inputKey]: '' })
    }
  }

  // Prevent background scrolling
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = 'unset'
    return () => { document.body.style.overflow = 'unset' }
  }, [isOpen])

  if (!isOpen) return null

  const modalContent = (
    <div className="fixed inset-0 z-[100] flex flex-col md:items-center md:justify-center animate-fade-in p-0 md:p-6">
      {/* Overlay */}
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative z-10 w-full h-full md:h-auto md:max-w-3xl bg-white md:rounded-3xl shadow-2xl flex flex-col max-h-screen md:max-h-[85vh] animate-slide-up md:animate-scale-in">
        
        {/* Header */}
        <div className="flex-shrink-0 px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-white z-20">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Job Match Preferences</h2>
            <p className="text-sm text-slate-500">Configure what roles & notifications you want.</p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-700 bg-slate-50 hover:bg-slate-100 rounded-full transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-slate-50/50">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-4" />
              <p>Loading your preferences...</p>
            </div>
          ) : (
            <form id="preferences-form" onSubmit={handleSubmit} className="space-y-8 max-w-2xl mx-auto">
              
              {/* Section: Roles & Skills */}
              <div className="space-y-5">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Briefcase className="w-4 h-4" /> Career Goals
                </h3>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Desired Roles</label>
                  <div className="flex gap-2 mb-3">
                    <input type="text" value={inputs.role} onChange={e => setInputs({...inputs, role: e.target.value})} onKeyDown={e => handleKeyDown(e, 'desired_roles', 'role')} placeholder="e.g. Frontend Developer (press Enter to add)" className="input-field" />
                    <button type="button" onClick={() => { handleAddArrayItem('desired_roles', inputs.role); setInputs({...inputs, role: ''}) }} className="btn-secondary px-4 py-2">Add</button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.desired_roles.map(r => (
                      <span key={r} className="px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-full text-sm font-medium flex items-center gap-1.5">
                        {r} <button type="button" onClick={() => handleRemoveArrayItem('desired_roles', r)}><X className="w-3 h-3 hover:text-red-500 cursor-pointer" /></button>
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Your Skills</label>
                  <div className="flex gap-2 mb-3">
                    <input type="text" value={inputs.skill} onChange={e => setInputs({...inputs, skill: e.target.value})} onKeyDown={e => handleKeyDown(e, 'skills', 'skill')} placeholder="e.g. React, Python (press Enter to add)" className="input-field" />
                    <button type="button" onClick={() => { handleAddArrayItem('skills', inputs.skill); setInputs({...inputs, skill: ''}) }} className="btn-secondary px-4 py-2">Add</button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.skills.map(s => (
                      <span key={s} className="px-3 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-full text-sm font-medium flex items-center gap-1.5">
                        {s} <button type="button" onClick={() => handleRemoveArrayItem('skills', s)}><X className="w-3 h-3 hover:text-red-500 cursor-pointer" /></button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Section: Locations & Companies */}
              <div className="space-y-5">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <MapPin className="w-4 h-4" /> Locations & Companies
                </h3>
                 
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Desired Locations <span className="font-normal text-slate-400">(use "Remote" for remote)</span></label>
                  <div className="flex gap-2 mb-3">
                    <input type="text" value={inputs.location} onChange={e => setInputs({...inputs, location: e.target.value})} onKeyDown={e => handleKeyDown(e, 'desired_locations', 'location')} placeholder="e.g. Bangalore, Remote" className="input-field" />
                    <button type="button" onClick={() => { handleAddArrayItem('desired_locations', inputs.location); setInputs({...inputs, location: ''}) }} className="btn-secondary px-4 py-2">Add</button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.desired_locations.map(l => (
                      <span key={l} className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-full text-sm font-medium flex items-center gap-1.5">
                        {l} <button type="button" onClick={() => handleRemoveArrayItem('desired_locations', l)}><X className="w-3 h-3 hover:text-red-500 cursor-pointer" /></button>
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Dream Companies</label>
                  <div className="flex gap-2 mb-3">
                    <input type="text" value={inputs.company} onChange={e => setInputs({...inputs, company: e.target.value})} onKeyDown={e => handleKeyDown(e, 'desired_companies', 'company')} placeholder="e.g. Google, Microsoft" className="input-field" />
                    <button type="button" onClick={() => { handleAddArrayItem('desired_companies', inputs.company); setInputs({...inputs, company: ''}) }} className="btn-secondary px-4 py-2">Add</button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.desired_companies.map(c => (
                      <span key={c} className="px-3 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-full text-sm font-medium flex items-center gap-1.5">
                        {c} <button type="button" onClick={() => handleRemoveArrayItem('desired_companies', c)}><X className="w-3 h-3 hover:text-red-500 cursor-pointer" /></button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Section: Expectations */}
              <div className="space-y-5">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <DollarSign className="w-4 h-4" /> Expectations & Level
                </h3>
  
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Experience Level</label>
                    <select
                      value={formData.experience_level}
                      onChange={e => setFormData({...formData, experience_level: e.target.value})}
                      className="input-field py-[13.5px] bg-white"
                    >
                      <option value="entry">Entry Level (0-2 Yrs)</option>
                      <option value="mid">Mid Level (3-5 Yrs)</option>
                      <option value="senior">Senior Level (5+ Yrs)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Target Salary Min (LPA)</label>
                    <div className="relative">
                      <span className="absolute left-4 top-3 text-slate-400 font-medium">₹</span>
                      <input type="number" min="0" value={formData.salary_expectation_min} onChange={e => setFormData({...formData, salary_expectation_min: Number(e.target.value)})} className="input-field pl-8" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Section: Matching & Notifications */}
              <div className="space-y-6">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Target className="w-4 h-4" /> Matching & Alerts
                </h3>
  
                <div>
                  <div className="flex justify-between items-center mb-4">
                     <label className="block text-sm font-semibold text-slate-700">Minimum Match Score (%)</label>
                     <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-bold">{formData.min_match_score}%</span>
                  </div>
                  <div className="px-2">
                    <ReactSlider
                        className="w-full h-2 bg-slate-200 rounded-full"
                        thumbClassName="w-6 h-6 bg-white border-2 border-indigo-500 rounded-full -mt-2 shadow cursor-grab active:cursor-grabbing focus:outline-none focus:ring-4 ring-indigo-500/20"
                        trackClassName="h-2 bg-indigo-500 rounded-full"
                        value={formData.min_match_score}
                        onChange={val => setFormData({ ...formData, min_match_score: val as number })}
                        min={0}
                        max={100}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-3 font-medium">Only jobs matching at least {formData.min_match_score}% of your preferences will be recommended.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Notification Frequency</label>
                    <select
                      value={formData.notification_frequency}
                      onChange={e => setFormData({...formData, notification_frequency: e.target.value})}
                      className="input-field py-[13.5px] bg-white"
                    >
                      <option value="none">Off (No Alerts)</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                    </select>
                  </div>
                  {formData.notification_frequency !== 'none' && (
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Alert Time</label>
                      <input type="time" value={formData.notification_time} onChange={e => setFormData({...formData, notification_time: e.target.value})} className="input-field bg-white" />
                    </div>
                  )}
                </div>
              </div>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3 bg-white z-20">
          <button type="button" onClick={onClose} className="px-5 py-2.5 font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors">
            Cancel
          </button>
          <button type="submit" form="preferences-form" disabled={isSaving || isLoading} className="btn-primary py-2.5">
            {isSaving ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</>
            ) : (
              'Save Preferences'
            )}
          </button>
        </div>
      </div>
    </div>
  )

  if (typeof document !== 'undefined') {
    return createPortal(modalContent, document.body)
  }
  return null
}
