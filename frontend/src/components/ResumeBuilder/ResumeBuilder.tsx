'use client';

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth';
import ResumeTemplateSelector from './ResumeTemplateSelector';
import ResumeStepForm from './ResumeStepForm';
import ResumePreview from './ResumePreview';
import ResumeExport from './ResumeExport';

interface ResumeData {
  template: string;
  header: {
    fullName: string;
    email: string;
    phone: string;
    location: string;
    website?: string;
    linkedin?: string;
  };
  summary: string;
  experience: {
    id: string;
    company: string;
    role: string;
    startDate: string;
    endDate: string;
    currentlyWorking: boolean;
    description: string;
  }[];
  education: {
    id: string;
    school: string;
    degree: string;
    field: string;
    graduationDate: string;
    gpa?: string;
  }[];
  skills: string[];
  certifications: {
    id: string;
    name: string;
    issuer: string;
    date: string;
  }[];
  projects: {
    id: string;
    name: string;
    description: string;
    technologies: string[];
    link?: string;
  }[];
}

type Step = 'template' | 'header' | 'summary' | 'experience' | 'education' | 'skills' | 'certifications' | 'projects' | 'export';

export default function ResumeBuilder() {
  const { user: currentUser } = useAuthStore();
  const [currentStep, setCurrentStep] = useState<Step>('template');
  const [resumeData, setResumeData] = useState<ResumeData>({
    template: 'modern',
    header: {
      fullName: currentUser?.full_name || '',
      email: currentUser?.email || '',
      phone: '',
      location: '',
    },
    summary: '',
    experience: [],
    education: [],
    skills: [],
    certifications: [],
    projects: [],
  });

  const steps: Step[] = ['template', 'header', 'summary', 'experience', 'education', 'skills', 'certifications', 'projects', 'export'];
  const currentStepIndex = steps.indexOf(currentStep);

  const handleTemplateSelect = (template: string) => {
    setResumeData({ ...resumeData, template });
    goToNextStep();
  };

  const handleDataUpdate = (section: keyof ResumeData, data: any) => {
    setResumeData({
      ...resumeData,
      [section]: data,
    });
  };

  const goToNextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1]);
    }
  };

  const goToPreviousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1]);
    }
  };

  const goToStep = (step: Step) => {
    setCurrentStep(step);
  };

  const getStepTitle = (step: Step): string => {
    const titles: Record<Step, string> = {
      template: 'Choose Template',
      header: 'Personal Information',
      summary: 'Professional Summary',
      experience: 'Work Experience',
      education: 'Education',
      skills: 'Skills',
      certifications: 'Certifications',
      projects: 'Projects',
      export: 'Export Resume',
    };
    return titles[step];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-slate-900">Resume Builder</h1>
          <p className="text-slate-600 mt-1">Create a professional resume in minutes</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <React.Fragment key={step}>
                <button
                  onClick={() => goToStep(step)}
                  className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold transition-all ${
                    currentStepIndex === index
                      ? 'bg-blue-600 text-white shadow-lg'
                      : currentStepIndex > index
                      ? 'bg-green-500 text-white'
                      : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                  }`}
                  title={getStepTitle(step)}
                >
                  {currentStepIndex > index ? '✓' : index + 1}
                </button>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      currentStepIndex > index ? 'bg-green-500' : 'bg-slate-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
          <p className="text-center text-slate-600">
            {getStepTitle(currentStep)} ({currentStepIndex + 1} of {steps.length})
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              {currentStep === 'template' && (
                <ResumeTemplateSelector onSelect={handleTemplateSelect} />
              )}

              {currentStep === 'header' && (
                <ResumeStepForm
                  step="header"
                  data={resumeData.header}
                  onUpdate={(data) => handleDataUpdate('header', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'summary' && (
                <ResumeStepForm
                  step="summary"
                  data={resumeData.summary}
                  onUpdate={(data) => handleDataUpdate('summary', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'experience' && (
                <ResumeStepForm
                  step="experience"
                  data={resumeData.experience}
                  onUpdate={(data) => handleDataUpdate('experience', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'education' && (
                <ResumeStepForm
                  step="education"
                  data={resumeData.education}
                  onUpdate={(data) => handleDataUpdate('education', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'skills' && (
                <ResumeStepForm
                  step="skills"
                  data={resumeData.skills}
                  onUpdate={(data) => handleDataUpdate('skills', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'certifications' && (
                <ResumeStepForm
                  step="certifications"
                  data={resumeData.certifications}
                  onUpdate={(data) => handleDataUpdate('certifications', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'projects' && (
                <ResumeStepForm
                  step="projects"
                  data={resumeData.projects}
                  onUpdate={(data) => handleDataUpdate('projects', data)}
                  onNext={goToNextStep}
                  onPrevious={goToPreviousStep}
                />
              )}

              {currentStep === 'export' && (
                <ResumeExport
                  resumeData={resumeData}
                  onPrevious={goToPreviousStep}
                />
              )}
            </div>
          </div>

          {/* Preview Section */}
          <div className="lg:col-span-2">
            <ResumePreview resumeData={resumeData} template={resumeData.template} />
          </div>
        </div>
      </div>
    </div>
  );
}
