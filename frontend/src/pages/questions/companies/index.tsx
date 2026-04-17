import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import { Building2, Search, ArrowRight, Star, TrendingUp, Users, Briefcase, Loader2, Image as ImageIcon } from 'lucide-react';
import { useImageGeneration } from '@/hooks/useImageGeneration';

const TOP_COMPANIES = [
  { name: 'TCS', type: 'Service Based', roles: ['System Engineer', 'Digital'], difficulty: 'Medium', color: 'from-blue-50 to-indigo-50 border-blue-200 text-blue-700' },
  { name: 'Infosys', type: 'Service Based', roles: ['System Engineer', 'Specialist Programmer'], difficulty: 'Medium', color: 'from-sky-50 to-blue-50 border-sky-200 text-sky-700' },
  { name: 'Wipro', type: 'Service Based', roles: ['Project Engineer', 'Turbo'], difficulty: 'Easy', color: 'from-cyan-50 to-teal-50 border-cyan-200 text-cyan-700' },
  { name: 'Accenture', type: 'Service Based', roles: ['Associate Software Engineer', 'Advanced ASE'], difficulty: 'Medium', color: 'from-purple-50 to-fuchsia-50 border-purple-200 text-purple-700' },
  { name: 'Amazon', type: 'Product Based', roles: ['SDE-1', 'Cloud Support Associate'], difficulty: 'Hard', color: 'from-amber-50 to-orange-50 border-amber-200 text-amber-700' },
  { name: 'Microsoft', type: 'Product Based', roles: ['Software Engineer', 'Support Engineer'], difficulty: 'Hard', color: 'from-emerald-50 to-green-50 border-emerald-200 text-emerald-700' },
  { name: 'Google', type: 'Product Based', roles: ['Software Engineer', 'SWE-III'], difficulty: 'Hard', color: 'from-red-50 to-rose-50 border-red-200 text-red-700' },
  { name: 'Cognizant', type: 'Service Based', roles: ['GenC', 'GenC Elevate', 'GenC Pro'], difficulty: 'Medium', color: 'from-indigo-50 to-blue-50 border-indigo-200 text-indigo-700' },
  { name: 'Capgemini', type: 'Service Based', roles: ['Analyst', 'Senior Analyst'], difficulty: 'Easy', color: 'from-slate-50 to-gray-50 border-slate-200 text-slate-700' },
  { name: 'IBM', type: 'Service Based', roles: ['Associate System Engineer'], difficulty: 'Medium', color: 'from-blue-100 to-indigo-100 border-blue-300 text-blue-800' },
  { name: 'Deloitte', type: 'Consulting', roles: ['Analyst', 'Consultant'], difficulty: 'Medium', color: 'from-green-50 to-emerald-50 border-green-200 text-green-700' },
  { name: 'Oracle', type: 'Product Based', roles: ['MTS', 'Server Technology'], difficulty: 'Hard', color: 'from-red-100 to-rose-100 border-red-300 text-red-800' },
];

const CompanyHeaderImage = ({ companyName, defaultColor }: { companyName: string, defaultColor: string }) => {
  const { generateCompanyProfile, loading, imageUrl } = useImageGeneration();

  useEffect(() => {
    generateCompanyProfile(companyName);
  }, [companyName]);

  if (loading) {
    return (
      <div className={`w-full h-32 rounded-t-3xl bg-gradient-to-br ${defaultColor} flex items-center justify-center opacity-50 animate-pulse`}>
        <Loader2 className="w-6 h-6 animate-spin mix-blend-multiply opacity-50" />
      </div>
    );
  }

  if (imageUrl) {
    return (
      <div className="w-full h-32 rounded-t-3xl overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10" />
        <img src={imageUrl} alt={companyName} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
        <div className="absolute bottom-4 left-6 z-20 flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-white/70" />
          <span className="text-white/70 text-xs font-medium">AI Generated</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`w-full h-32 rounded-t-3xl bg-gradient-to-br ${defaultColor} relative overflow-hidden`}>
      <div className="absolute -bottom-8 -right-8 opacity-10 blur-xl">
        <Building2 className="w-40 h-40 mix-blend-overlay" />
      </div>
    </div>
  );
};


export default function CompaniesDirectory() {
  const [search, setSearch] = useState('');
  const router = useRouter();

  const filteredCompanies = TOP_COMPANIES.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase()) || 
    c.type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Head>
        <title>Company Question Banks — PrepEdge AI</title>
      </Head>

      <div className="min-h-screen bg-slate-50 pt-24 pb-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Header Section */}
          <div className="text-center max-w-2xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider">
              <Building2 className="w-4 h-4" /> Company Insights
            </div>
            <h1 className="text-4xl font-heading font-extrabold text-slate-900 mb-4 tracking-tight">
              Company Question <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Banks</span>
            </h1>
            <p className="text-lg text-slate-600">
              Practice exact interview questions asked at top tech and service companies to maximize your placement chances.
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-10">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-600 transition-colors" />
              <input 
                type="text" 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search for a company (e.g., TCS, Amazon) or type (e.g., Service Based)..."
                className="w-full pl-12 pr-4 py-4 text-base bg-white border-2 border-slate-200 rounded-2xl shadow-sm focus:outline-none focus:ring-0 focus:border-indigo-500 transition-all font-medium text-slate-800 placeholder:font-normal"
              />
            </div>
          </div>

          {/* Company Grid */}
          {filteredCompanies.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border border-slate-200 shadow-sm">
              <Search className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-slate-900 mb-2">No companies found</h3>
              <p className="text-slate-500">Try searching for a different company name.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCompanies.map(company => (
                <Link key={company.name} href={`/questions/company/${encodeURIComponent(company.name)}`}
                      className="group flex flex-col glass-card bg-white rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 relative overflow-hidden">
                  
                  <CompanyHeaderImage companyName={company.name} defaultColor={company.color} />
                  
                  <div className="p-6 flex flex-col flex-grow">
                    <div className="flex items-start justify-between mb-4 -mt-10 relative z-30">
                      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center bg-white shadow-xl border-2 border-white`}>
                        <div className={`flex items-center justify-center w-full h-full rounded-xl bg-gradient-to-br ${company.color}`}>
                          <span className="text-xl font-black">{company.name.charAt(0)}</span>
                        </div>
                      </div>
                      <span className={`px-2.5 py-1 text-xs font-bold rounded-lg border uppercase tracking-wide bg-white shadow-sm
                        ${company.difficulty === 'Hard' ? 'text-red-700 border-red-200' : 
                          company.difficulty === 'Medium' ? 'text-amber-700 border-amber-200' : 
                          'text-emerald-700 border-emerald-200'}`}>
                        {company.difficulty}
                      </span>
                    </div>
                  
                  <h3 className="text-2xl font-bold text-slate-900 mb-1 group-hover:text-indigo-600 transition-colors">{company.name}</h3>
                  <p className="text-sm font-semibold text-slate-500 mb-4">{company.type}</p>
                  
                  <div className="space-y-2 mb-6 flex-grow">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Briefcase className="w-4 h-4 text-indigo-400" /> Hiring for:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {company.roles.map(role => (
                        <span key={role} className="px-2 py-1 bg-slate-100 text-slate-700 rounded-md text-xs font-medium border border-slate-200">
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-auto">
                    <span className="text-sm font-bold text-indigo-600">View Questions</span>
                    <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white text-indigo-500 transition-colors">
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

        </div>
      </div>
    </>
  );
}
