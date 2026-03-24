import Link from 'next/link';
import { Brain, Github, Twitter, Linkedin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 group mb-4">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-1.5 rounded-lg">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-lg tracking-tight text-slate-800">
                PrepEdge AI
              </span>
            </Link>
            <p className="text-slate-500 text-sm mb-6">
              Empowering Indian engineering students to ace their campus placements with AI-driven preparation tools.
            </p>
            <div className="flex space-x-4 text-slate-400">
              <a href="#" className="hover:text-indigo-600 transition-colors"><Twitter className="w-5 h-5" /></a>
              <a href="#" className="hover:text-indigo-600 transition-colors"><Github className="w-5 h-5" /></a>
              <a href="#" className="hover:text-indigo-600 transition-colors"><Linkedin className="w-5 h-5" /></a>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-slate-900 mb-4">Product</h3>
            <ul className="space-y-3 text-sm text-slate-500">
              <li><Link href="/flashlearn" className="hover:text-indigo-600 transition-colors">FlashLearn</Link></li>
              <li><Link href="/resumeai" className="hover:text-indigo-600 transition-colors">ResumeAI</Link></li>
              <li><Link href="/mockmate" className="hover:text-indigo-600 transition-colors">MockMate</Link></li>
              <li><Link href="/pricing" className="hover:text-indigo-600 transition-colors">Pricing</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-slate-900 mb-4">Resources</h3>
            <ul className="space-y-3 text-sm text-slate-500">
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Interview Guides</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Company Profiles</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Help Center</a></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-slate-900 mb-4">Legal</h3>
            <ul className="space-y-3 text-sm text-slate-500">
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-indigo-600 transition-colors">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-100 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-400 text-sm">
            © {new Date().getFullYear()} PrepEdge AI. All rights reserved.
          </p>
          <div className="text-slate-400 text-sm flex gap-4">
            <span>Made with ✨ in India</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
