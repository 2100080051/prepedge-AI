import { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuthStore } from '@/store/auth';
import { useThemeStore } from '@/store/theme';
import { User, Bell, Lock, Shield, Loader2, Save, ArrowLeft, Paintbrush, Briefcase, Moon, Sun } from 'lucide-react';
import Link from 'next/link';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { isDark, setTheme } = useThemeStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');
  const [mounted, setMounted] = useState(false);

  // Form State
  const [profileForm, setProfileForm] = useState({
    fullName: '',
    email: '',
    github: 'https://github.com/',
  });

  const [personalizationForm, setPersonalizationForm] = useState({
    college: '',
    course: '',
    yearsOfExperience: 0,
  });

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [notificationForm, setNotificationForm] = useState({
    marketing: true,
    security: true,
    studyReminders: true,
    placementAlerts: false
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }
    if (user) {
      setProfileForm({
        fullName: user.full_name || user.username || '',
        email: user.email || '',
        github: 'https://github.com/',
      });
    }
    setMounted(true);
  }, [user, isAuthenticated]);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3500);
  };

  const handleSimulatedSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API delay for a polished UX feeling
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setLoading(false);
    showToast('✅ Preferences updated successfully!');
    
    // Clear password fields if that was the active tab
    if (activeTab === 'security') {
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
    }
  };

  const TABS = [
    { id: 'profile', label: 'Public Profile', icon: <User className="w-4 h-4" /> },
    { id: 'personalization', label: 'Personalization', icon: <Briefcase className="w-4 h-4" /> },
    { id: 'security', label: 'Password & Security', icon: <Lock className="w-4 h-4" /> },
    { id: 'notifications', label: 'Email Notifications', icon: <Bell className="w-4 h-4" /> },
    { id: 'appearance', label: 'Appearance', icon: <Paintbrush className="w-4 h-4" /> },
  ];

  if (!user) return null;

  return (
    <>
      <Head>
        <title>Account Settings — PrepEdge AI</title>
      </Head>

      {toast && (
        <div className="fixed top-6 right-6 z-[200] px-6 py-3 bg-slate-900 text-white rounded-xl shadow-2xl font-medium text-sm animate-fade-in flex items-center gap-2 border top-toast-border">
          {toast}
        </div>
      )}

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <Link href="/profile" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-6">
            <ArrowLeft className="w-4 h-4" /> Back to Profile
          </Link>

          <div className="mb-8">
            <h1 className="text-3xl font-heading font-extrabold text-slate-900 mb-2">Account Settings</h1>
            <p className="text-slate-500">Manage your profile, security, and notification preferences.</p>
          </div>

          <div className="flex flex-col md:flex-row gap-8">
            
            {/* Sidebar Navigation */}
            <div className="w-full md:w-64 flex-shrink-0">
              <div className="bg-white rounded-2xl border border-slate-200 p-2 shadow-sm sticky top-24">
                {TABS.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left mb-1
                      ${activeTab === tab.id 
                        ? 'bg-indigo-50 text-indigo-700 shadow-sm border border-indigo-100' 
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 border border-transparent'}`}
                  >
                    <span className={`${activeTab === tab.id ? 'text-indigo-600' : 'text-slate-400'}`}>
                      {tab.icon}
                    </span>
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1">
              <div className="glass-card bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in">
                
                {/* Profile Settings */}
                {activeTab === 'profile' && (
                  <form onSubmit={handleSimulatedSave} className="p-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                      <User className="w-5 h-5 text-indigo-500" /> Public Profile
                    </h2>
                    
                    <div className="flex items-center gap-6 mb-8 pb-8 border-b border-slate-100">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 border-2 border-indigo-50 flex items-center justify-center shadow-sm">
                        <span className="text-3xl font-black text-indigo-700">{user.username.charAt(0).toUpperCase()}</span>
                      </div>
                      <div>
                        <button type="button" className="px-4 py-2 bg-white border border-slate-200 text-sm font-bold text-slate-700 rounded-xl hover:bg-slate-50 transition-colors shadow-sm mb-2">
                          Change Avatar
                        </button>
                        <p className="text-xs text-slate-500">JPG, GIF or PNG. 1MB max.</p>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-bold text-slate-700 mb-2">Full Name</label>
                          <input type="text" value={profileForm.fullName} onChange={e => setProfileForm({...profileForm, fullName: e.target.value})} 
                            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" />
                        </div>
                        <div>
                          <label className="block text-sm font-bold text-slate-700 mb-2">Email Address</label>
                          <input type="email" value={profileForm.email} disabled
                            className="w-full px-4 py-3 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 cursor-not-allowed text-sm font-medium" />
                          <p className="text-xs text-slate-400 mt-1.5 flex items-center gap-1"><Shield className="w-3 h-3"/> Contact support to change email</p>
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">GitHub Profile URL</label>
                        <input type="url" value={profileForm.github} onChange={e => setProfileForm({...profileForm, github: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" />
                      </div>
                    </div>
                  </form>
                )}

                {/* Security Settings */}
                {activeTab === 'security' && (
                  <form onSubmit={handleSimulatedSave} className="p-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                      <Lock className="w-5 h-5 text-indigo-500" /> Change Password
                    </h2>
                    
                    <div className="space-y-6 max-w-lg">
                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Current Password</label>
                        <input type="password" required value={passwordForm.currentPassword} onChange={e => setPasswordForm({...passwordForm, currentPassword: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" />
                      </div>
                      <div className="pt-4 border-t border-slate-100">
                        <label className="block text-sm font-bold text-slate-700 mb-2">New Password</label>
                        <input type="password" required minLength={8} value={passwordForm.newPassword} onChange={e => setPasswordForm({...passwordForm, newPassword: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium mb-1.5" />
                        <p className="text-xs text-slate-500">Must be at least 8 characters long.</p>
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Confirm New Password</label>
                        <input type="password" required minLength={8} value={passwordForm.confirmPassword} onChange={e => setPasswordForm({...passwordForm, confirmPassword: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" />
                      </div>
                    </div>
                  </form>
                )}

                {/* Notification Settings */}
                {activeTab === 'notifications' && (
                  <form onSubmit={handleSimulatedSave} className="p-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                      <Bell className="w-5 h-5 text-indigo-500" /> Email Notifications
                    </h2>
                    
                    <div className="space-y-6 max-w-2xl">
                      {Object.entries({
                        security: { title: 'Security Alerts', desc: 'Get notified about unrecognized logins or password changes. Cannot be disabled.', disabled: true },
                        studyReminders: { title: 'Daily Study Reminders', desc: 'Receive an email if you are close to losing your gamification streak.', disabled: false },
                        placementAlerts: { title: 'Placement Verification Logs', desc: 'Get updates when an Admin verifies or rejects your logged placement.', disabled: false },
                        marketing: { title: 'Product Updates', desc: 'Occasional emails about new features on PrepEdge AI.', disabled: false }
                      }).map(([key, data]) => (
                        <div key={key} className="flex items-start justify-between py-4 border-b border-slate-100 last:border-0">
                          <div>
                            <h4 className="font-bold text-slate-800 text-sm mb-1">{data.title}</h4>
                            <p className="text-slate-500 text-xs leading-relaxed max-w-sm">{data.desc}</p>
                          </div>
                          <div>
                            <button
                              type="button"
                              onClick={() => !data.disabled && setNotificationForm(prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
                              disabled={data.disabled}
                              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                notificationForm[key as keyof typeof notificationForm] ? 'bg-indigo-600' : 'bg-slate-200'
                              } ${data.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                            >
                              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                notificationForm[key as keyof typeof notificationForm] ? 'translate-x-6' : 'translate-x-1'
                              }`} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </form>
                )}

                {/* Personalization Settings */}
                {activeTab === 'personalization' && (
                  <form onSubmit={handleSimulatedSave} className="p-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-2 flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-indigo-500" /> Job Preferences
                    </h2>
                    <p className="text-slate-600 text-sm mb-6">Help us personalize your job recommendations by telling us about your background.</p>
                    
                    <div className="space-y-6 max-w-lg mb-8">
                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">College/University</label>
                        <input 
                          type="text" 
                          placeholder="e.g., IIT Delhi, Stanford, etc."
                          value={personalizationForm.college} 
                          onChange={e => setPersonalizationForm({...personalizationForm, college: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" 
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Course/Major</label>
                        <input 
                          type="text" 
                          placeholder="e.g., B.Tech Computer Science, B.E. Electronics"
                          value={personalizationForm.course} 
                          onChange={e => setPersonalizationForm({...personalizationForm, course: e.target.value})} 
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium" 
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-bold text-slate-700 mb-2">Years of Professional Experience</label>
                        <div className="flex items-center gap-4">
                          <select 
                            value={personalizationForm.yearsOfExperience} 
                            onChange={e => setPersonalizationForm({...personalizationForm, yearsOfExperience: parseInt(e.target.value)})} 
                            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm font-medium"
                          >
                            <option value={0}>Fresher (0 years)</option>
                            {Array.from({length: 30}, (_, i) => i + 1).map(year => (
                              <option key={year} value={year}>{year} {year === 1 ? 'year' : 'years'}</option>
                            ))}
                          </select>
                          <div className="text-center text-sm font-semibold text-slate-600 bg-slate-100 px-4 py-3 rounded-xl min-w-max">
                            {personalizationForm.yearsOfExperience === 0 ? '👶 Fresher' : 
                             personalizationForm.yearsOfExperience < 3 ? '📚 Junior' : 
                             personalizationForm.yearsOfExperience < 7 ? '⭐ Senior' : '👑 Lead'}
                          </div>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">This helps us recommend the right job match for you</p>
                      </div>
                    </div>

                    <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
                      <p className="text-sm text-indigo-900">
                        <strong>💡 Tip:</strong> The more accurate your information, the better job recommendations you'll receive. We use this data only to personalize your experience.
                      </p>
                    </div>
                  </form>
                )}

                {/* Appearance Settings */}
                {activeTab === 'appearance' && mounted && (
                  <form className="p-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                      <Paintbrush className="w-5 h-5 text-indigo-500" /> Interface Theme
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg">
                      <button
                        type="button"
                        onClick={() => {
                          setTheme(false);
                          showToast('✅ Switched to Light Mode');
                        }}
                        className={`rounded-xl p-4 transition-all border-2 ${
                          !isDark 
                            ? 'border-indigo-600 bg-indigo-50/30' 
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="w-full h-24 bg-slate-50 rounded-lg border border-slate-200 mb-3 overflow-hidden">
                          <div className="h-6 bg-white border-b border-slate-200 flex items-center px-2 gap-1">
                            <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                            <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                            <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                          </div>
                        </div>
                        <div className="flex items-center justify-center gap-2 mb-2">
                          <Sun className="w-5 h-5 text-amber-500" />
                          <span className="font-bold text-slate-900 text-sm">Light Mode</span>
                        </div>
                        {!isDark && <div className="text-xs text-indigo-500 font-medium">✓ Active</div>}
                      </button>
                      
                      <button
                        type="button"
                        onClick={() => {
                          setTheme(true);
                          showToast('✅ Switched to Dark Mode');
                        }}
                        className={`rounded-xl p-4 transition-all border-2 ${
                          isDark 
                            ? 'border-indigo-600 bg-indigo-50/30' 
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="w-full h-24 bg-slate-900 rounded-lg border border-slate-800 mb-3 overflow-hidden">
                          <div className="h-6 bg-slate-950 border-b border-slate-800 flex items-center px-2 gap-1">
                            <div className="w-2 h-2 rounded-full bg-slate-700"></div>
                            <div className="w-2 h-2 rounded-full bg-slate-700"></div>
                            <div className="w-2 h-2 rounded-full bg-slate-700"></div>
                          </div>
                        </div>
                        <div className="flex items-center justify-center gap-2 mb-2">
                          <Moon className="w-5 h-5 text-purple-400" />
                          <span className="font-bold text-slate-700 text-sm">Dark Mode</span>
                        </div>
                        {isDark && <div className="text-xs text-indigo-500 font-medium">✓ Active</div>}
                      </button>
                    </div>
                  </form>
                )}

                {/* Fixed Footer for Save Button */}
                <div className="p-6 bg-slate-50 border-t border-slate-200 flex items-center justify-end">
                  <button
                    onClick={handleSimulatedSave}
                    disabled={loading || (activeTab === 'security' && (!passwordForm.currentPassword || !passwordForm.newPassword || passwordForm.newPassword !== passwordForm.confirmPassword))}
                    className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 text-white font-bold rounded-xl shadow-md hover:bg-indigo-700 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save Changes
                  </button>
                </div>

              </div>
            </div>

          </div>
        </div>
      </div>
    </>
  );
}
