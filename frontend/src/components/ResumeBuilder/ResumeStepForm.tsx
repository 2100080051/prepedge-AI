'use client';

import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface ResumeStepFormProps {
  step: string;
  data: any;
  onUpdate: (data: any) => void;
  onNext: () => void;
  onPrevious: () => void;
}

export default function ResumeStepForm({
  step,
  data,
  onUpdate,
  onNext,
  onPrevious,
}: ResumeStepFormProps) {
  const [formData, setFormData] = useState(data);

  const handleChange = (field: string, value: any) => {
    const newData = typeof formData === 'object' && !Array.isArray(formData)
      ? { ...formData, [field]: value }
      : value;
    setFormData(newData);
  };

  const handleAddItem = (type: string) => {
    if (Array.isArray(formData)) {
      const newItem = getEmptyItem(type);
      setFormData([...formData, newItem]);
    }
  };

  const handleRemoveItem = (index: number) => {
    if (Array.isArray(formData)) {
      setFormData(formData.filter((_, i) => i !== index));
    }
  };

  const handleUpdateItem = (index: number, field: string, value: any) => {
    if (Array.isArray(formData)) {
      const updated = [...formData];
      updated[index] = { ...updated[index], [field]: value };
      setFormData(updated);
    }
  };

  const handleAddSkill = () => {
    if (Array.isArray(formData)) {
      setFormData([...formData, '']);
    }
  };

  const handleUpdateSkill = (index: number, value: string) => {
    if (Array.isArray(formData)) {
      const updated = [...formData];
      updated[index] = value;
      setFormData(updated);
    }
  };

  const handleRemoveSkill = (index: number) => {
    if (Array.isArray(formData)) {
      setFormData(formData.filter((_, i) => i !== index));
    }
  };

  const handleSave = () => {
    onUpdate(formData);
    onNext();
  };

  const getEmptyItem = (type: string) => {
    const templates: Record<string, any> = {
      experience: {
        id: uuidv4(),
        company: '',
        role: '',
        startDate: '',
        endDate: '',
        currentlyWorking: false,
        description: '',
      },
      education: {
        id: uuidv4(),
        school: '',
        degree: '',
        field: '',
        graduationDate: '',
        gpa: '',
      },
      certification: {
        id: uuidv4(),
        name: '',
        issuer: '',
        date: '',
      },
      project: {
        id: uuidv4(),
        name: '',
        description: '',
        technologies: [],
        link: '',
      },
    };
    return templates[type];
  };

  const renderHeaderForm = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-900">Personal Information</h3>
      
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Full Name
        </label>
        <input
          type="text"
          value={formData.fullName}
          onChange={(e) => handleChange('fullName', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="John Doe"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Email
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="john@example.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Phone
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="+1 (555) 000-0000"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Location
        </label>
        <input
          type="text"
          value={formData.location}
          onChange={(e) => handleChange('location', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="San Francisco, CA"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Website (Optional)
        </label>
        <input
          type="url"
          value={formData.website || ''}
          onChange={(e) => handleChange('website', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://yourwebsite.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          LinkedIn (Optional)
        </label>
        <input
          type="url"
          value={formData.linkedin || ''}
          onChange={(e) => handleChange('linkedin', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://linkedin.com/in/yourprofile"
        />
      </div>
    </div>
  );

  const renderSummaryForm = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-900">Professional Summary</h3>
      <p className="text-sm text-slate-600">Write 2-3 sentences about your professional background and goals.</p>
      
      <textarea
        value={formData}
        onChange={(e) => handleChange('summary', e.target.value)}
        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
        placeholder="e.g., Results-driven Software Engineer with 5+ years of experience..."
      />
    </div>
  );

  const renderExperienceForm = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Work Experience</h3>
        <button
          onClick={() => handleAddItem('experience')}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
        >
          + Add Experience
        </button>
      </div>

      {Array.isArray(formData) && formData.map((exp, index) => (
        <div key={exp.id} className="border border-slate-200 rounded-lg p-4 relative">
          <button
            onClick={() => handleRemoveItem(index)}
            className="absolute top-2 right-2 text-red-500 hover:text-red-700"
          >
            ✕
          </button>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              value={exp.company}
              onChange={(e) => handleUpdateItem(index, 'company', e.target.value)}
              placeholder="Company"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="text"
              value={exp.role}
              onChange={(e) => handleUpdateItem(index, 'role', e.target.value)}
              placeholder="Job Title"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="month"
              value={exp.startDate}
              onChange={(e) => handleUpdateItem(index, 'startDate', e.target.value)}
              placeholder="Start Date"
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="month"
              value={exp.endDate}
              onChange={(e) => handleUpdateItem(index, 'endDate', e.target.value)}
              placeholder="End Date"
              disabled={exp.currentlyWorking}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />

            <label className="col-span-2 flex items-center text-sm">
              <input
                type="checkbox"
                checked={exp.currentlyWorking}
                onChange={(e) => {
                  handleUpdateItem(index, 'currentlyWorking', e.target.checked);
                  if (e.target.checked) {
                    handleUpdateItem(index, 'endDate', '');
                  }
                }}
                className="mr-2"
              />
              Currently working here
            </label>

            <textarea
              value={exp.description}
              onChange={(e) => handleUpdateItem(index, 'description', e.target.value)}
              placeholder="Describe your responsibilities and achievements..."
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
            />
          </div>
        </div>
      ))}
    </div>
  );

  const renderEducationForm = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Education</h3>
        <button
          onClick={() => handleAddItem('education')}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
        >
          + Add Education
        </button>
      </div>

      {Array.isArray(formData) && formData.map((edu, index) => (
        <div key={edu.id} className="border border-slate-200 rounded-lg p-4 relative">
          <button
            onClick={() => handleRemoveItem(index)}
            className="absolute top-2 right-2 text-red-500 hover:text-red-700"
          >
            ✕
          </button>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              value={edu.school}
              onChange={(e) => handleUpdateItem(index, 'school', e.target.value)}
              placeholder="School/University"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="text"
              value={edu.degree}
              onChange={(e) => handleUpdateItem(index, 'degree', e.target.value)}
              placeholder="Degree"
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="text"
              value={edu.field}
              onChange={(e) => handleUpdateItem(index, 'field', e.target.value)}
              placeholder="Field of Study"
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="month"
              value={edu.graduationDate}
              onChange={(e) => handleUpdateItem(index, 'graduationDate', e.target.value)}
              placeholder="Graduation Date"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="text"
              value={edu.gpa || ''}
              onChange={(e) => handleUpdateItem(index, 'gpa', e.target.value)}
              placeholder="GPA (Optional)"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      ))}
    </div>
  );

  const renderSkillsForm = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Skills</h3>
        <button
          onClick={handleAddSkill}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
        >
          + Add Skill
        </button>
      </div>

      <p className="text-sm text-slate-600">List your relevant technical and soft skills.</p>

      <div className="space-y-2">
        {Array.isArray(formData) && formData.map((skill, index) => (
          <div key={index} className="flex gap-2">
            <input
              type="text"
              value={skill}
              onChange={(e) => handleUpdateSkill(index, e.target.value)}
              placeholder="e.g., React, Python, Project Management"
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleRemoveSkill(index)}
              className="px-3 py-2 text-red-500 hover:text-red-700 text-sm"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCertificationsForm = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Certifications</h3>
        <button
          onClick={() => handleAddItem('certification')}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
        >
          + Add Certification
        </button>
      </div>

      {Array.isArray(formData) && formData.map((cert, index) => (
        <div key={cert.id} className="border border-slate-200 rounded-lg p-4 relative">
          <button
            onClick={() => handleRemoveItem(index)}
            className="absolute top-2 right-2 text-red-500 hover:text-red-700"
          >
            ✕
          </button>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              value={cert.name}
              onChange={(e) => handleUpdateItem(index, 'name', e.target.value)}
              placeholder="Certification Name"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="text"
              value={cert.issuer}
              onChange={(e) => handleUpdateItem(index, 'issuer', e.target.value)}
              placeholder="Issuer"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="month"
              value={cert.date}
              onChange={(e) => handleUpdateItem(index, 'date', e.target.value)}
              placeholder="Date Issued"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      ))}
    </div>
  );

  const renderProjectsForm = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Projects</h3>
        <button
          onClick={() => handleAddItem('project')}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition"
        >
          + Add Project
        </button>
      </div>

      {Array.isArray(formData) && formData.map((project, index) => (
        <div key={project.id} className="border border-slate-200 rounded-lg p-4 relative">
          <button
            onClick={() => handleRemoveItem(index)}
            className="absolute top-2 right-2 text-red-500 hover:text-red-700"
          >
            ✕
          </button>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              value={project.name}
              onChange={(e) => handleUpdateItem(index, 'name', e.target.value)}
              placeholder="Project Name"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <textarea
              value={project.description}
              onChange={(e) => handleUpdateItem(index, 'description', e.target.value)}
              placeholder="Project Description"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 h-16"
            />

            <input
              type="text"
              value={project.technologies?.join(', ')}
              onChange={(e) =>
                handleUpdateItem(index, 'technologies', e.target.value.split(',').map(t => t.trim()))
              }
              placeholder="Technologies (comma-separated)"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="url"
              value={project.link || ''}
              onChange={(e) => handleUpdateItem(index, 'link', e.target.value)}
              placeholder="Project Link (Optional)"
              className="col-span-2 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      ))}
    </div>
  );

  const renderForm = () => {
    switch (step) {
      case 'header':
        return renderHeaderForm();
      case 'summary':
        return renderSummaryForm();
      case 'experience':
        return renderExperienceForm();
      case 'education':
        return renderEducationForm();
      case 'skills':
        return renderSkillsForm();
      case 'certifications':
        return renderCertificationsForm();
      case 'projects':
        return renderProjectsForm();
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {renderForm()}

      <div className="flex gap-3 pt-4 border-t border-slate-200">
        <button
          onClick={() => {
            onUpdate(formData);
            onPrevious();
          }}
          className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition font-medium"
        >
          Previous
        </button>
        <button
          onClick={handleSave}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
        >
          Next
        </button>
      </div>
    </div>
  );
}
