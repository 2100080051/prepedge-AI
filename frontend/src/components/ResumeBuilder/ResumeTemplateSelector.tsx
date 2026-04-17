'use client';

import React from 'react';

const TEMPLATES = [
  {
    id: 'modern',
    name: 'Modern',
    description: 'Clean and contemporary design with a left sidebar',
    preview: '🎨 Modern minimal style',
    color: 'from-blue-500 to-blue-600',
  },
  {
    id: 'professional',
    name: 'Professional',
    description: 'Traditional, corporate-friendly format',
    preview: '📊 Classic professional layout',
    color: 'from-slate-600 to-slate-700',
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Colorful and visually engaging design',
    preview: '🎭 Creative and bold style',
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Ultra-clean with maximum white space',
    preview: '⚪ Minimalist approach',
    color: 'from-gray-400 to-gray-500',
  },
  {
    id: 'infographic',
    name: 'Infographic',
    description: 'Visual skills and achievements showcase',
    preview: '📈 Data-driven visual format',
    color: 'from-orange-500 to-red-500',
  },
  {
    id: 'academic',
    name: 'Academic',
    description: 'Perfect for research and academic background',
    preview: '🎓 Academic formal style',
    color: 'from-indigo-600 to-indigo-700',
  },
];

interface ResumeTemplateSelectorProps {
  onSelect: (template: string) => void;
}

export default function ResumeTemplateSelector({
  onSelect,
}: ResumeTemplateSelectorProps) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Select a Template</h2>
      <p className="text-slate-600 mb-8">
        Choose a template that best matches your style. You can change it anytime.
      </p>

      <div className="space-y-4">
        {TEMPLATES.map((template) => (
          <button
            key={template.id}
            onClick={() => onSelect(template.id)}
            className="w-full group relative overflow-hidden rounded-lg border-2 border-slate-200 p-4 text-left transition-all hover:border-blue-500 hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 text-lg mb-1">
                  {template.name}
                </h3>
                <p className="text-slate-600 text-sm mb-2">
                  {template.description}
                </p>
              </div>
              <div
                className={`h-12 w-12 rounded-lg bg-gradient-to-br ${template.color} flex items-center justify-center text-white font-bold ml-4 flex-shrink-0`}
              >
                {template.id[0].toUpperCase()}
              </div>
            </div>

            {/* Hover effect */}
            <div className="absolute inset-0 bg-blue-50 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          </button>
        ))}
      </div>

      <div className="mt-8 pt-6 border-t border-slate-200">
        <p className="text-xs text-slate-500">
          💡 All templates are ATS-friendly and designed to highlight your best features
        </p>
      </div>
    </div>
  );
}
