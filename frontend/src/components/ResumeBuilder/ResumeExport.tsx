'use client';

import React, { useState } from 'react';

interface ResumeExportProps {
  resumeData: any;
  onPrevious: () => void;
}

export default function ResumeExport({
  resumeData,
  onPrevious,
}: ResumeExportProps) {
  const [exporting, setExporting] = useState(false);
  const [exportedFormat, setExportedFormat] = useState<string | null>(null);

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      // In a real application, use a library like jsPDF or react-pdf
      // For now, simulate the export
      const element = document.getElementById('resume-preview');
      if (element) {
        // trigger browser's print to PDF
        window.print();
        setExportedFormat('pdf');
      }
    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleExportDOCX = async () => {
    setExporting(true);
    try {
      // In a real application, use a library like docx
      // For now, simulate the export
      const content = generateDocxContent();
      const blob = new Blob([content], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${resumeData.header.fullName}-resume.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setExportedFormat('docx');
    } catch (error) {
      console.error('Error exporting DOCX:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleDownloadJSON = () => {
    const dataStr = JSON.stringify(resumeData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(dataBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${resumeData.header.fullName}-resume.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const generateDocxContent = () => {
    // Simple text representation for DOCX
    return `
${resumeData.header.fullName}

${resumeData.header.email} | ${resumeData.header.phone} | ${resumeData.header.location}

PROFESSIONAL SUMMARY
${resumeData.summary}

WORK EXPERIENCE
${resumeData.experience
  .map(
    (exp: any) => `
${exp.role}
${exp.company} | ${exp.startDate} - ${exp.currentlyWorking ? 'Present' : exp.endDate}
${exp.description}
`
  )
  .join('\n')}

EDUCATION
${resumeData.education
  .map(
    (edu: any) => `
${edu.degree} in ${edu.field}
${edu.school} | ${edu.graduationDate}
${edu.gpa ? `GPA: ${edu.gpa}` : ''}
`
  )
  .join('\n')}

SKILLS
${resumeData.skills.join(' | ')}

CERTIFICATIONS
${resumeData.certifications
  .map((cert: any) => `${cert.name} - ${cert.issuer} (${cert.date})`)
  .join('\n')}

PROJECTS
${resumeData.projects
  .map(
    (project: any) => `
${project.name}
${project.description}
Technologies: ${project.technologies.join(', ')}
${project.link ? `Link: ${project.link}` : ''}
`
  )
  .join('\n')}
    `;
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-slate-900">Export Your Resume</h3>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-900">
          ✅ Your resume is ready! Choose your preferred format below to download.
        </p>
      </div>

      {/* Export Options */}
      <div className="space-y-3">
        {/* PDF Export */}
        <button
          onClick={handleExportPDF}
          disabled={exporting}
          className={`w-full p-4 border-2 rounded-lg transition flex items-center justify-between ${
            exportedFormat === 'pdf'
              ? 'border-green-500 bg-green-50'
              : 'border-slate-200 hover:border-blue-500'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="text-2xl">📄</div>
            <div className="text-left">
              <p className="font-semibold text-slate-900">PDF Format</p>
              <p className="text-sm text-slate-600">Best for most job applications</p>
            </div>
          </div>
          {exportedFormat === 'pdf' && <span className="text-green-600 font-semibold">✓ Done</span>}
        </button>

        {/* DOCX Export */}
        <button
          onClick={handleExportDOCX}
          disabled={exporting}
          className={`w-full p-4 border-2 rounded-lg transition flex items-center justify-between ${
            exportedFormat === 'docx'
              ? 'border-green-500 bg-green-50'
              : 'border-slate-200 hover:border-blue-500'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="text-2xl">📝</div>
            <div className="text-left">
              <p className="font-semibold text-slate-900">Word Document (.docx)</p>
              <p className="text-sm text-slate-600">Editable in Microsoft Word</p>
            </div>
          </div>
          {exportedFormat === 'docx' && <span className="text-green-600 font-semibold">✓ Done</span>}
        </button>

        {/* JSON Export */}
        <button
          onClick={handleDownloadJSON}
          className="w-full p-4 border-2 border-slate-200 rounded-lg transition hover:border-blue-500 flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="text-2xl">💾</div>
            <div className="text-left">
              <p className="font-semibold text-slate-900">JSON Backup</p>
              <p className="text-sm text-slate-600">Save for future editing</p>
            </div>
          </div>
          <span className="text-blue-600">⬇</span>
        </button>
      </div>

      {/* Additional Options */}
      <div className="bg-slate-50 rounded-lg p-4 mt-6">
        <h4 className="font-semibold text-slate-900 mb-3">Next Steps</h4>
        <ul className="space-y-2 text-sm text-slate-700">
          <li>✓ Review your resume for any typos or errors</li>
          <li>✓ Customize for specific job applications using ATS analysis</li>
          <li>✓ Generate cover letters for each position</li>
          <li>✓ Get feedback from our AI resume reviewer</li>
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t border-slate-200">
        <button
          onClick={onPrevious}
          className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition font-medium"
        >
          Back
        </button>
        <button
          onClick={() => window.location.href = '/dashboard'}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
        >
          Go to Dashboard
        </button>
      </div>

      {/* Info Box */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
        <p className="text-xs text-amber-900">
          💡 Tip: Save multiple versions of your resume for different job types or companies. Use different keywords and emphasize different skills based on the job description.
        </p>
      </div>
    </div>
  );
}

function generateDocxContent(): string {
  throw new Error('Function not implemented.');
}
