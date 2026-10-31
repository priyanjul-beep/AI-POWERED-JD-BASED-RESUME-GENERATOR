'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { 
  Sparkles, 
  Briefcase, 
  FileText, 
  UploadCloud, 
  Layers, 
  ArrowRight, 
  ArrowLeft, 
  Loader2, 
  Check, 
  AlertCircle,
  FileCheck2
} from 'lucide-react';

const EXPERIENCE_OPTIONS = [
  { value: 'FRESHER', label: 'Fresher (No professional experience)', desc: 'Prioritizes academic/personal projects and computer science fundamentals.' },
  { value: 'NO_INTERNSHIP', label: 'No Internship Experience', desc: 'Emphasizes practical project engineering and verifiable coursework.' },
  { value: 'INTERNSHIP', label: 'Internship Experience', desc: 'Prioritizes real-world internship contributions, tools, and team deliverables.' },
  { value: 'APPRENTICE', label: 'Apprentice Experience', desc: 'Highlights apprenticeship learning, pair programming, and production tasks.' },
  { value: '1_YEAR', label: '1 Year of Experience', desc: 'Focuses on feature delivery, API engineering, and codebase ownership.' },
  { value: '2_YEARS', label: '2 Years of Experience', desc: 'Demonstrates end-to-end service ownership and database optimization.' },
  { value: '3_YEARS', label: '3 Years of Experience', desc: 'Spotlights microservices, architectural decisions, and performance tuning.' },
  { value: '4_YEARS', label: '4 Years of Experience', desc: 'Emphasizes technical leadership, system architecture, and integrations.' },
  { value: '5_PLUS_YEARS', label: '5+ Years of Experience', desc: 'Highlights distributed architecture, cross-team technical leadership, and scalability.' },
];

export default function GenerateResumePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [targetRole, setTargetRole] = useState('Java Developer');
  const [targetCompany, setTargetCompany] = useState('');
  
  // JD input method: 'paste' or 'upload'
  const [jdMethod, setJdMethod] = useState<'paste' | 'upload'>('paste');
  const [jdText, setJdText] = useState('');
  const [jdFile, setJdFile] = useState<File | null>(null);

  // Reference Resume
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  // Experience level
  const [experienceLevel, setExperienceLevel] = useState('INTERNSHIP');
  const [additionalDetails, setAdditionalDetails] = useState('');

  // Submit status
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading]);

  const handleQuickFillSample = () => {
    setTargetRole('Java Developer');
    setTargetCompany('Mastercard');
    setJdMethod('paste');
    setJdText(`We are looking for a Java Developer to join our core backend engineering team.
Requirements:
- Strong hands-on proficiency in Core Java (Java 11/17) and J2EE.
- Robust experience building enterprise RESTful microservices with Spring Boot and Spring MVC.
- Solid experience with Relational Databases (PostgreSQL / MySQL) and writing performant SQL queries.
- Familiarity with Docker, Git, CI/CD pipelines, and JUnit automated testing.
- Understanding of distributed transaction boundaries, caching (Redis), and clean architecture.`);
    setExperienceLevel('INTERNSHIP');
    setAdditionalDetails('I completed a six-month software development internship where I worked on backend development, REST APIs, and database integration.');
  };

  const handleNext = () => {
    setError('');
    if (step === 1) {
      if (!targetRole.trim()) {
        setError('Please enter your target job designation.');
        return;
      }
    } else if (step === 2) {
      if (jdMethod === 'paste' && !jdText.trim()) {
        setError('Please paste the Job Description text.');
        return;
      }
      if (jdMethod === 'upload' && !jdFile) {
        setError('Please upload a PDF or DOCX file of the Job Description.');
        return;
      }
    }
    setStep(s => Math.min(s + 1, 4));
  };

  const handleBack = () => {
    setError('');
    setStep(s => Math.max(s - 1, 1));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');

    try {
      let jdId: number | undefined;
      let refResumeId: number | undefined;

      // 1. If JD file uploaded, create JobDescription record via FormData first
      if (jdMethod === 'upload' && jdFile) {
        const formData = new FormData();
        formData.append('uploaded_file', jdFile);
        formData.append('target_role', targetRole);
        formData.append('target_company', targetCompany);
        const jdRes = await api.post<{ id: number }>('/api/documents/jds/', formData);
        jdId = jdRes.id;
      }

      // 2. If Reference resume uploaded, upload ReferenceResume record
      if (resumeFile) {
        const formData = new FormData();
        formData.append('uploaded_file', resumeFile);
        formData.append('file_name', resumeFile.name);
        const refRes = await api.post<{ id: number }>('/api/documents/reference-resumes/', formData);
        refResumeId = refRes.id;
      }

      // 3. Trigger analyze and generation endpoint
      const payload: any = {
        target_role: targetRole,
        target_company: targetCompany,
        experience_level: experienceLevel,
        additional_experience_details: additionalDetails,
      };

      if (jdId) {
        payload.job_description_id = jdId;
      } else {
        payload.job_description_text = jdText;
      }

      if (refResumeId) {
        payload.reference_resume_id = refResumeId;
      }

      const generationResult = await api.post<{ id: number }>('/api/resume-generations/analyze/', payload);
      router.push(`/review/${generationResult.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze and generate resume.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 w-full space-y-8">
      {/* Page Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-xs font-semibold border border-indigo-500/20">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          AI Resume Synthesis Wizard
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Targeted Resume Generator
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Provide your target role, job description, reference resume, and current experience level.
        </p>
      </div>

      {/* Quick Fill Sample Button */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleQuickFillSample}
          className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Auto-fill Java Developer sample inputs
        </button>
      </div>

      {/* Step Indicator Bar */}
      <div className="grid grid-cols-4 gap-2 sm:gap-4 pb-2">
        {[
          { num: 1, label: 'Target Role' },
          { num: 2, label: 'Job Description' },
          { num: 3, label: 'Reference Resume' },
          { num: 4, label: 'Experience Level' },
        ].map((item) => (
          <div
            key={item.num}
            className={`p-3 rounded-xl border flex flex-col sm:flex-row items-center gap-2.5 transition-all ${
              step === item.num
                ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md'
                : step > item.num
                ? 'bg-slate-900 border-emerald-500/40 text-emerald-400'
                : 'bg-slate-950 border-slate-800 text-slate-500'
            }`}
          >
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                step > item.num
                  ? 'bg-emerald-500 text-slate-950'
                  : step === item.num
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-400'
              }`}
            >
              {step > item.num ? <Check className="w-3.5 h-3.5" /> : item.num}
            </div>
            <span className="text-xs font-semibold text-center sm:text-left">{item.label}</span>
          </div>
        ))}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Wizard Form Card */}
      <div className="p-6 sm:p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6">
        {/* STEP 1: TARGET ROLE & COMPANY */}
        {step === 1 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-indigo-400" />
                Step 1: Target Job Designation & Company
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Enter the exact position title you are applying for. The LLM will position your experience and summary specifically for this designation.
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  Target Designation <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  required
                  placeholder="e.g. Java Developer, Backend Engineer, AI Engineer, Full Stack Developer"
                  className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  Target Company Name (Optional)
                </label>
                <input
                  type="text"
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  placeholder="e.g. Mastercard, Google, Amazon, Enterprise Tech"
                  className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: JOB DESCRIPTION */}
        {step === 2 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                Step 2: Job Description Input
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Paste the job requirements directly or upload the JD document (PDF/DOCX).
              </p>
            </div>

            <div className="flex gap-2 p-1 rounded-xl bg-slate-950 border border-slate-800 w-fit">
              <button
                type="button"
                onClick={() => setJdMethod('paste')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  jdMethod === 'paste' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Paste Text
              </button>
              <button
                type="button"
                onClick={() => setJdMethod('upload')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  jdMethod === 'upload' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Upload File (PDF/DOCX)
              </button>
            </div>

            {jdMethod === 'paste' ? (
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Job Description Text</label>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  rows={8}
                  placeholder="Paste the full job description here, including responsibilities, required skills, and qualifications..."
                  className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed"
                />
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-8 text-center space-y-3 bg-slate-950/50 transition-colors">
                <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto" />
                <div>
                  <label htmlFor="jd-upload" className="cursor-pointer font-semibold text-sm text-indigo-400 hover:underline">
                    Click to upload Job Description
                  </label>
                  <p className="text-xs text-slate-500 mt-1">Supports PDF, DOCX, or TXT (Max 10MB)</p>
                </div>
                <input
                  id="jd-upload"
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) setJdFile(e.target.files[0]);
                  }}
                />
                {jdFile && (
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-300 text-xs font-semibold">
                    <FileCheck2 className="w-4 h-4" />
                    {jdFile.name} ({(jdFile.size / 1024).toFixed(1)} KB)
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* STEP 3: REFERENCE RESUME */}
        {step === 3 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <UploadCloud className="w-5 h-5 text-indigo-400" />
                Step 3: Reference Resume (Optional)
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Upload your existing resume (PDF or DOCX). We extract your contact details and current baseline, but combine it with your full career profile so technology gaps are bridged.
              </p>
            </div>

            <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-8 text-center space-y-3 bg-slate-950/50 transition-colors">
              <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto" />
              <div>
                <label htmlFor="resume-upload" className="cursor-pointer font-semibold text-sm text-indigo-400 hover:underline">
                  Click to select Reference Resume
                </label>
                <p className="text-xs text-slate-500 mt-1">Supports PDF or DOCX</p>
              </div>
              <input
                id="resume-upload"
                type="file"
                accept=".pdf,.docx,.doc"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) setResumeFile(e.target.files[0]);
                }}
              />
              {resumeFile ? (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-300 text-xs font-semibold">
                  <FileCheck2 className="w-4 h-4" />
                  {resumeFile.name} ({(resumeFile.size / 1024).toFixed(1)} KB)
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">
                  No reference resume selected. Resume will be constructed directly from your Complete Career Profile database.
                </p>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: EXPERIENCE LEVEL & DETAILS */}
        {step === 4 && (
          <div className="space-y-5 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                Step 4: Candidate Experience Level
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Select your current professional standing. Prompts are dynamically customized for Freshers vs Interns vs Senior Engineers.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-72 overflow-y-auto pr-1">
              {EXPERIENCE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setExperienceLevel(opt.value)}
                  className={`p-3.5 rounded-xl border text-left flex flex-col justify-between transition-all ${
                    experienceLevel === opt.value
                      ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                      : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <span className="text-xs font-bold">{opt.label}</span>
                  <span className="text-[11px] text-slate-400 mt-1">{opt.desc}</span>
                </button>
              ))}
            </div>

            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-semibold text-slate-300">
                Additional Experience Context (Optional)
              </label>
              <textarea
                value={additionalDetails}
                onChange={(e) => setAdditionalDetails(e.target.value)}
                rows={3}
                placeholder="e.g. 'I completed a six-month software development internship where I worked on backend development, REST APIs, and database integration.'"
                className="w-full p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          {step > 1 ? (
            <button
              type="button"
              onClick={handleBack}
              disabled={submitting}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Previous Step
            </button>
          ) : (
            <div />
          )}

          {step < 4 ? (
            <button
              type="button"
              onClick={handleNext}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-indigo-500/20"
            >
              Next Step
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Synthesizing Role-Specific Resume...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Analyze & Generate Resume
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
