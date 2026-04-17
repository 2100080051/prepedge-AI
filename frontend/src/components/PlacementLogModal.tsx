import { useState } from 'react';
import { X, Building2, IndianRupee, Link2, Layers, Hash, Loader2, CheckCircle2, Sparkles, AlertCircle } from 'lucide-react';
import { placementsApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function PlacementLogModal({ isOpen, onClose, onSuccess }: Props) {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  const [form, setForm] = useState({
    company_name: '',
    salary_lpa: '',
    offer_letter_url: '',
    round_type: '',
    total_rounds: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState<any>(null);

  if (!isOpen) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) { router.push('/auth/login'); return; }
    if (!form.company_name.trim()) { setError('Company name is required.'); return; }

    setLoading(true);
    setError('');
    try {
      const payload: any = { company_name: form.company_name.trim() };
      if (form.salary_lpa) payload.salary_lpa = parseFloat(form.salary_lpa);
      if (form.offer_letter_url) payload.offer_letter_url = form.offer_letter_url.trim();
      if (form.round_type) payload.round_type = form.round_type;
      if (form.total_rounds) payload.total_rounds = parseInt(form.total_rounds);

      const res = await placementsApi.log(payload);
      setSuccess(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to log placement. Please try again.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setForm({ company_name: '', salary_lpa: '', offer_letter_url: '', round_type: '', total_rounds: '' });
    setError('');
    setSuccess(null);
    if (success && onSuccess) onSuccess();
    onClose();
  };

  const ROUND_TYPES = ['Online Test', 'Technical Round 1', 'Technical Round 2', 'HR Round', 'Managerial Round', 'All Rounds'];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={handleClose} />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden animate-fade-in">
        {/* Gradient header */}
        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-6 text-white relative">
          <button onClick={handleClose} className="absolute top-4 right-4 p-1 text-white/70 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl"><Sparkles className="w-6 h-6" /></div>
            <div>
              <h2 className="text-xl font-bold">Log Your Placement 🎉</h2>
              <p className="text-white/80 text-sm mt-1">Share your success and inspire others!</p>
            </div>
          </div>
        </div>

        {success ? (
          <div className="p-8 text-center">
            <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10 text-emerald-500" />
            </div>
            <h3 className="text-2xl font-extrabold text-slate-900 mb-2">Placement Logged! 🥳</h3>
            <p className="text-slate-600 mb-4">{success.message}</p>
            {success.xp_awarded && (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-50 border border-indigo-200 rounded-full text-indigo-700 font-bold text-lg mb-6">
                <Sparkles className="w-5 h-5 text-indigo-500" />
                +{success.xp_awarded} XP Earned!
              </div>
            )}
            <p className="text-sm text-slate-500 mb-6">Your placement is pending admin verification. It will appear on the leaderboard once verified.</p>
            <button onClick={handleClose}
              className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl transition-all hover:shadow-lg">
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-1">
              <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                <Building2 className="w-4 h-4 text-indigo-500" /> Company Name <span className="text-rose-500">*</span>
              </label>
              <input name="company_name" value={form.company_name} onChange={handleChange} required
                placeholder="e.g. TCS, Infosys, Google..."
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <IndianRupee className="w-4 h-4 text-emerald-500" /> Salary (LPA)
                </label>
                <input name="salary_lpa" type="number" step="0.1" min="0" value={form.salary_lpa} onChange={handleChange}
                  placeholder="e.g. 15.5"
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Hash className="w-4 h-4 text-purple-500" /> Total Rounds
                </label>
                <input name="total_rounds" type="number" min="1" max="10" value={form.total_rounds} onChange={handleChange}
                  placeholder="e.g. 3"
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-500" /> Round Type
              </label>
              <select name="round_type" value={form.round_type} onChange={handleChange}
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-700 bg-white">
                <option value="">Select round (optional)</option>
                {ROUND_TYPES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            <div className="space-y-1">
              <label className="block text-sm font-semibold text-slate-700 flex items-center gap-2">
                <Link2 className="w-4 h-4 text-cyan-500" /> Offer Letter URL
              </label>
              <input name="offer_letter_url" value={form.offer_letter_url} onChange={handleChange}
                placeholder="https://drive.google.com/... (optional)"
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              <p className="text-xs text-slate-400">Optional, but speeds up verification by our team.</p>
            </div>

            <button type="submit" disabled={loading || !form.company_name.trim()}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl disabled:opacity-50 hover:shadow-glow transition-all duration-300 flex items-center justify-center gap-2 text-base">
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" />Submitting...</> : <><Sparkles className="w-5 h-5" />Submit Placement</>}
            </button>

            <p className="text-xs text-center text-slate-400">
              Placements are reviewed by our admin team within 24 hours before appearing on the leaderboard.
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
