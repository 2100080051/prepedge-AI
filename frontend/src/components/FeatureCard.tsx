import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
  ctaText: string;
  delay?: number;
}

export default function FeatureCard({ icon, title, description, href, ctaText, delay = 0 }: FeatureCardProps) {
  return (
    <div 
      className="glass-card group relative p-8 rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-glow hover:-translate-y-2"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Background Gradient Blob */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
      
      {/* Icon Area */}
      <div className="relative mb-6">
        <div className="inline-flex p-3 rounded-xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
          {icon}
        </div>
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        <h3 className="text-xl font-heading font-bold text-slate-800 mb-3 group-hover:text-indigo-600 transition-colors duration-300">
          {title}
        </h3>
        <p className="text-slate-600 mb-8 leading-relaxed">
          {description}
        </p>
      </div>
      
      {/* CTA */}
      <div className="relative z-10 mt-auto">
        <Link 
          href={href} 
          className="inline-flex items-center gap-2 font-semibold text-indigo-600 group-hover:text-indigo-700 transition-colors"
        >
          {ctaText}
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
        </Link>
      </div>
    </div>
  );
}
