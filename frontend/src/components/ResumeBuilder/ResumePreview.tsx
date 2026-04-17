'use client';

import React from 'react';

interface ResumePreviewProps {
  resumeData: any;
  template: string;
}

export default function ResumePreview({
  resumeData,
  template,
}: ResumePreviewProps) {
  const renderModernTemplate = () => (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8">
        <h1 className="text-4xl font-bold mb-2">{resumeData.header.fullName}</h1>
        <div className="flex flex-wrap gap-4 text-sm">
          {resumeData.header.email && <span>📧 {resumeData.header.email}</span>}
          {resumeData.header.phone && <span>📱 {resumeData.header.phone}</span>}
          {resumeData.header.location && <span>📍 {resumeData.header.location}</span>}
          {resumeData.header.website && <span>🌐 {resumeData.header.website}</span>}
        </div>
      </div>

      {/* Content */}
      <div className="p-8 space-y-6">
        {/* Summary */}
        {resumeData.summary && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-2 border-b-2 border-blue-600 pb-1">
              Professional Summary
            </h2>
            <p className="text-slate-700 text-sm leading-relaxed">
              {resumeData.summary}
            </p>
          </section>
        )}

        {/* Experience */}
        {resumeData.experience?.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1">
              Work Experience
            </h2>
            <div className="space-y-3">
              {resumeData.experience.map((exp: any, idx: number) => (
                <div key={idx} className="text-sm">
                  <div className="flex justify-between items-start mb-1">
                    <div>
                      <p className="font-semibold text-slate-900">{exp.role}</p>
                      <p className="text-slate-600">{exp.company}</p>
                    </div>
                    <span className="text-xs text-slate-500">
                      {exp.startDate} - {exp.currentlyWorking ? 'Present' : exp.endDate}
                    </span>
                  </div>
                  <p className="text-slate-700 ml-4">{exp.description}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Education */}
        {resumeData.education?.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1">
              Education
            </h2>
            <div className="space-y-2">
              {resumeData.education.map((edu: any, idx: number) => (
                <div key={idx} className="text-sm">
                  <div className="flex justify-between items-start mb-1">
                    <div>
                      <p className="font-semibold text-slate-900">
                        {edu.degree} in {edu.field}
                      </p>
                      <p className="text-slate-600">{edu.school}</p>
                    </div>
                    <span className="text-xs text-slate-500">{edu.graduationDate}</span>
                  </div>
                  {edu.gpa && <p className="text-slate-600 text-xs">GPA: {edu.gpa}</p>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Skills */}
        {resumeData.skills?.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1">
              Skills
            </h2>
            <div className="flex flex-wrap gap-2">
              {resumeData.skills.map((skill: string, idx: number) => (
                <span
                  key={idx}
                  className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Certifications */}
        {resumeData.certifications?.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1">
              Certifications
            </h2>
            <div className="space-y-2">
              {resumeData.certifications.map((cert: any, idx: number) => (
                <div key={idx} className="text-sm">
                  <p className="font-semibold text-slate-900">{cert.name}</p>
                  <p className="text-slate-600">{cert.issuer} • {cert.date}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Projects */}
        {resumeData.projects?.length > 0 && (
          <section>
            <h2 className="text-lg font-bold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1">
              Projects
            </h2>
            <div className="space-y-3">
              {resumeData.projects.map((project: any, idx: number) => (
                <div key={idx} className="text-sm">
                  <p className="font-semibold text-slate-900">{project.name}</p>
                  <p className="text-slate-700">{project.description}</p>
                  {project.technologies?.length > 0 && (
                    <p className="text-slate-600 text-xs mt-1">
                      {project.technologies.join(' • ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );

  const renderProfessionalTemplate = () => (
    <div className="bg-white rounded-lg shadow-lg p-8">
      {/* Header */}
      <div className="mb-6 pb-4 border-b-2 border-slate-200">
        <h1 className="text-3xl font-bold text-slate-900 mb-1">
          {resumeData.header.fullName}
        </h1>
        <div className="text-sm text-slate-600 space-y-1">
          {resumeData.header.email && <div>📧 {resumeData.header.email}</div>}
          {resumeData.header.phone && <div>📱 {resumeData.header.phone}</div>}
          {resumeData.header.location && <div>📍 {resumeData.header.location}</div>}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-5">
        {resumeData.summary && (
          <section>
            <h2 className="text-sm font-bold uppercase text-slate-900 mb-2 tracking-wider">
              Professional Summary
            </h2>
            <p className="text-sm text-slate-700">{resumeData.summary}</p>
          </section>
        )}

        {resumeData.experience?.length > 0 && (
          <section>
            <h2 className="text-sm font-bold uppercase text-slate-900 mb-3 tracking-wider">
              Experience
            </h2>
            <div className="space-y-3">
              {resumeData.experience.map((exp: any, idx: number) => (
                <div key={idx} className="text-xs">
                  <div className="flex justify-between">
                    <p className="font-bold text-slate-900">{exp.role}</p>
                    <span className="text-slate-600">
                      {exp.startDate} - {exp.currentlyWorking ? 'Present' : exp.endDate}
                    </span>
                  </div>
                  <p className="text-slate-600">{exp.company}</p>
                  <p className="text-slate-700 mt-1">{exp.description}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {resumeData.education?.length > 0 && (
          <section>
            <h2 className="text-sm font-bold uppercase text-slate-900 mb-3 tracking-wider">
              Education
            </h2>
            <div className="space-y-2">
              {resumeData.education.map((edu: any, idx: number) => (
                <div key={idx} className="text-xs">
                  <div className="flex justify-between">
                    <p className="font-bold text-slate-900">
                      {edu.degree} • {edu.field}
                    </p>
                    <span className="text-slate-600">{edu.graduationDate}</span>
                  </div>
                  <p className="text-slate-600">{edu.school}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {resumeData.skills?.length > 0 && (
          <section>
            <h2 className="text-sm font-bold uppercase text-slate-900 mb-2 tracking-wider">
              Skills
            </h2>
            <p className="text-xs text-slate-700">
              {resumeData.skills.join(' • ')}
            </p>
          </section>
        )}
      </div>
    </div>
  );

  const renderTemplate = () => {
    switch (template) {
      case 'professional':
        return renderProfessionalTemplate();
      case 'modern':
      default:
        return renderModernTemplate();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Preview</h3>
        <p className="text-sm text-slate-600">
          This is how your resume will look. Updates appear in real-time.
        </p>
      </div>

      {/* A4 Page Container for print */}
      <div className="bg-gray-50 p-4 rounded-lg min-h-screen flex items-center justify-center">
        <div className="w-full bg-white" style={{ aspectRatio: '8.5/11' }}>
          {renderTemplate()}
        </div>
      </div>
    </div>
  );
}
