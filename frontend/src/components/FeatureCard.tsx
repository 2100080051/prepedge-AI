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
  badge?: string;
  stats?: string;
  gradient?: string;
}

const GRADIENTS = [
  'from-indigo-500 to-purple-600',
  'from-emerald-500 to-teal-600',
  'from-rose-500 to-pink-600',
  'from-amber-500 to-orange-500',
  'from-cyan-500 to-sky-600',
  'from-violet-500 to-indigo-600',
];

export default function FeatureCard({
  icon, title, description, href, ctaText,
  delay = 0, badge, stats, gradient
}: FeatureCardProps) {
  return (
    <Link
      href={href}
      className="group relative flex flex-col p-7 rounded-3xl border border-slate-200 bg-white overflow-hidden
                 hover:-translate-y-2 hover:border-transparent hover:shadow-glow
                 transition-all duration-500 ease-spring animate-fade-in-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Animated gradient blob on hover */}
      <div className={`absolute top-0 right-0 -mr-20 -mt-20 w-48 h-48 rounded-full bg-gradient-to-br ${gradient || GRADIENTS[0]} opacity-0 group-hover:opacity-10 blur-2xl transition-all duration-700 group-hover:scale-125`} />

      {/* Top mesh gradient bar */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${gradient || GRADIENTS[0]} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

      {/* Badge */}
      {badge && (
        <span className="absolute top-4 right-4 px-2.5 py-1 text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 rounded-full">
          {badge}
        </span>
      )}

      {/* Icon */}
      <div className="relative mb-5 flex-shrink-0">
        <div className={`inline-flex p-3.5 rounded-2xl bg-gradient-to-br ${gradient || GRADIENTS[0]} text-white shadow-sm group-hover:scale-110 group-hover:shadow-lg transition-all duration-300`}>
          {icon}
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex-1">
        <h3 className="text-xl font-heading font-bold text-slate-900 mb-2.5 group-hover:text-indigo-600 transition-colors duration-300">
          {title}
        </h3>
        <p className="text-slate-500 leading-relaxed text-sm">
          {description}
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="mt-4 pt-4 border-t border-slate-100 text-xs font-semibold text-slate-400 relative z-10">
          {stats}
        </div>
      )}

      {/* CTA */}
      <div className="relative z-10 mt-5 flex items-center justify-between">
        <span className={`inline-flex items-center gap-1.5 text-sm font-semibold bg-gradient-to-r ${gradient || GRADIENTS[0]} bg-clip-text text-transparent group-hover:gap-2.5 transition-all duration-300`}>
          {ctaText}
          <ArrowRight className={`w-4 h-4 text-indigo-600 group-hover:translate-x-1 transition-transform duration-300`} />
        </span>

        {/* Animated dot */}
        <div className="w-2 h-2 rounded-full bg-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-ping-slow" />
      </div>
    </Link>
  );
}
