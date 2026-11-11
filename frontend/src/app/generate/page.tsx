'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import AiAnalysisLoader from '@/components/generate/AiAnalysisLoader';
import { 
  Sparkles, 
  Briefcase, 
  Building2,
  FileText, 
  UploadCloud, 
  Layers, 
  AlertCircle,
  FileCheck2,
  Trash2,
  RefreshCw,
  X,
  Info
} from 'lucide-react';

const EXPERIENCE_OPTIONS = [
  { value: 'FRESHER', label: 'Fresher', desc: 'Prioritizes academic/personal projects and computer science fundamentals.' },
  { value: 'NO_INTERNSHIP', label: 'No Internship Experience', desc: 'Emphasizes practical project engineering and verifiable coursework.' },
  { value: 'INTERNSHIP', label: 'Internship Experience', desc: 'Prioritizes real-world internship contributions, tools, and team deliverables.' },
  { value: 'APPRENTICE', label: 'Apprentice', desc: 'Highlights apprenticeship learning, pair programming, and production tasks.' },
  { value: '1_YEAR', label: '1 Year Experience', desc: 'Focuses on feature delivery, API engineering, and codebase ownership.' },
  { value: '2_YEARS', label: '2 Years Experience', desc: 'Demonstrates end-to-end service ownership and database optimization.' },
  { value: '3_YEARS', label: '3 Years Experience', desc: 'Spotlights microservices, architectural decisions, and performance tuning.' },
  { value: '4_YEARS', label: '4 Years Experience', desc: 'Emphasizes technical leadership, system architecture, and integrations.' },
  { value: '5_PLUS_YEARS', label: '5+ Years Experience', desc: 'Highlights distributed architecture, cross-team technical leadership, and scalability.' },
];

export default function GenerateResumePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  // Single-Step Form State: Target Job Details
  const [targetRole, setTargetRole] = useState('Software Developer 1');
  const [targetCompany, setTargetCompany] = useState('');
  
  // Job Description Input: Direct Text or File Upload
  const [jdMethod, setJdMethod] = useState<'paste' | 'upload'>('paste');
  const [jdText, setJdText] = useState('');
  const [jdFile, setJdFile] = useState<File | null>(null);

  // Reference Resume: Optional File Upload
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  // Cached Uploaded Document IDs for Instant Resubmission After Cancel
  const [cachedJdId, setCachedJdId] = useState<number | null>(null);
  const [cachedResumeId, setCachedResumeId] = useState<number | null>(null);

  // Candidate Experience Details
  const [experienceLevel, setExperienceLevel] = useState('INTERNSHIP');
  const [additionalDetails, setAdditionalDetails] = useState('');

  // Status & Feedback States
  const [submitting, setSubmitting] = useState(false);
  const [activeRequestId, setActiveRequestId] = useState<string | null>(null);
  const [isUploadPhase, setIsUploadPhase] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  const [infoNotice, setInfoNotice] = useState<string | null>(null);

  // References for Request Tracking & Robust Cancellation
  const abortControllerRef = useRef<AbortController | null>(null);
  const activeRequestIdRef = useRef<string | null>(null);
  const isCancelledRef = useRef<boolean>(false);

  // File input refs for programmatic trigger
  const jdFileInputRef = useRef<HTMLInputElement | null>(null);
  const resumeFileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const handleQuickFillSample = () => {
    setTargetRole('Java Developer');
    setTargetCompany('Mastercard');
    setJdMethod('paste');
    setCachedJdId(null);
    setCachedResumeId(null);
    setJdText(`We are looking for a Java Developer to join our core backend engineering team.
Requirements:
- Strong hands-on proficiency in Core Java (Java 11/17) and J2EE.
- Robust experience building enterprise RESTful microservices with Spring Boot and Spring MVC.
- Solid experience with Relational Databases (PostgreSQL / MySQL) and writing performant SQL queries.
- Familiarity with Docker, Git, CI/CD pipelines, and JUnit automated testing.
- Understanding of distributed transaction boundaries, caching (Redis), and clean architecture.`);
    setExperienceLevel('INTERNSHIP');
    setAdditionalDetails('I completed a six-month software development internship where I worked on backend development, REST APIs, and database integration.');
    setInfoNotice(null);
    setError('');
  };

  const handleCancel = async () => {
    // 1. Immediately flag cancellation
    isCancelledRef.current = true;
    activeRequestIdRef.current = null;
    setActiveRequestId(null);

    // 2. Abort any in-flight HTTP request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // 3. Clear loading screen immediately
    setSubmitting(false);
    setIsUploadPhase(false);
    setIsSuccess(false);

    // 4. Notify user and preserve inputs
    setInfoNotice('Resume analysis cancelled.');
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setInfoNotice(null);

    // Validate Required Inputs
    if (!targetRole.trim()) {
      setError('Please provide your Target Job Role.');
      return;
    }

    if (jdMethod === 'paste' && !jdText.trim()) {
      setError('Please enter or paste the Job Description text.');
      return;
    }

    if (jdMethod === 'upload' && !jdFile) {
      setError('Please upload a PDF or DOCX file for the Job Description.');
      return;
    }

    // Set up request lifecycle and AbortController
    const requestId = crypto.randomUUID();
    activeRequestIdRef.current = requestId;
    setActiveRequestId(requestId);
    isCancelledRef.current = false;

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setSubmitting(true);
    setIsUploadPhase(true);
    setIsSuccess(false);

    try {
      let jdId: number | undefined;
      let refResumeId: number | undefined;

      // Stage A: If JD is an uploaded file, send document first (or reuse cached upload)
      if (jdMethod === 'upload' && jdFile) {
        if (cachedJdId) {
          jdId = cachedJdId;
        } else {
          if (isCancelledRef.current) return;
          const formData = new FormData();
          formData.append('uploaded_file', jdFile);
          formData.append('target_role', targetRole);
          formData.append('target_company', targetCompany);

          const jdRes = await api.post<{ id: number }>('/api/documents/jds/', formData, {
            signal: controller.signal,
          });

          if (isCancelledRef.current || activeRequestIdRef.current !== requestId) return;
          jdId = jdRes.id;
          setCachedJdId(jdRes.id);
        }
      }

      // Stage B: If Reference Resume is uploaded, send reference resume (or reuse cached upload)
      if (resumeFile) {
        if (cachedResumeId) {
          refResumeId = cachedResumeId;
        } else {
          if (isCancelledRef.current) return;
          const formData = new FormData();
          formData.append('uploaded_file', resumeFile);
          formData.append('file_name', resumeFile.name);

          const refRes = await api.post<{ id: number }>('/api/documents/reference-resumes/', formData, {
            signal: controller.signal,
          });

          if (isCancelledRef.current || activeRequestIdRef.current !== requestId) return;
          refResumeId = refRes.id;
          setCachedResumeId(refRes.id);
        }
      }

      // Documents uploaded; transition to AI multi-stage synthesis
      setIsUploadPhase(false);

      if (isCancelledRef.current || activeRequestIdRef.current !== requestId) return;

      // Stage C: Trigger AI Analyze and Synthesis
      const payload: Record<string, unknown> = {
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

      const generationResult = await api.post<{ id: number }>(
        '/api/resume-generations/analyze/',
        payload,
        { signal: controller.signal }
      );

      // Robust race condition check: Did the user click Cancel right as API responded?
      if (isCancelledRef.current || activeRequestIdRef.current !== requestId) {
        // Prevent late response from continuing to review page
        if (generationResult?.id) {
          try {
            await api.post(`/api/resume-generations/${generationResult.id}/cancel/`);
          } catch (cancelErr) {
            console.warn('Backend session cancellation on race condition:', cancelErr);
          }
        }
        return;
      }

      // Mark success & animate completion
      setIsSuccess(true);

      // Brief transition delay so the user sees the completed state before review page loads
      setTimeout(() => {
        if (!isCancelledRef.current && activeRequestIdRef.current === requestId) {
          setSubmitting(false);
          setIsSuccess(false);
          setIsUploadPhase(false);
          activeRequestIdRef.current = null;
          setActiveRequestId(null);
          router.push(`/review/${generationResult.id}`);
        }
      }, 500);

    } catch (err: unknown) {
      // Check if this error was caused by explicit user cancellation
      const isAbort = 
        isCancelledRef.current || 
        (err instanceof Error && (err.name === 'AbortError' || err.message?.toLowerCase().includes('aborted')));

      if (isAbort) {
        // Handled cleanly by cancel flow
        activeRequestIdRef.current = null;
        setActiveRequestId(null);
        setSubmitting(false);
        setIsUploadPhase(false);
        setIsSuccess(false);
        setInfoNotice('Resume analysis cancelled.');
        return;
      }

      // Real error occurred
      const message = err instanceof Error ? err.message : 'Failed to analyze and generate resume. Please try again.';
      setError(message);
      activeRequestIdRef.current = null;
      setActiveRequestId(null);
      setSubmitting(false);
      setIsUploadPhase(false);
      setIsSuccess(false);
    }
  };

  const selectedExpDesc = EXPERIENCE_OPTIONS.find(o => o.value === experienceLevel)?.desc;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-10 w-full space-y-8 animate-in fade-in duration-200">
      
      {/* Full-screen Modern AI Analysis Loader Overlay - Only active when request is in-flight */}
      {submitting && !!activeRequestId && (
        <AiAnalysisLoader
          isOpen={submitting}
          targetRole={targetRole || 'Target Role'}
          targetCompany={targetCompany}
          hasJdFile={jdMethod === 'upload' && !!jdFile}
          hasResumeFile={!!resumeFile}
          isUploadPhase={isUploadPhase}
          isSuccess={isSuccess}
          onCancel={handleCancel}
        />
      )}

      {/* Page Header */}
      <div className="text-center space-y-2.5">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-xs font-semibold border border-indigo-500/20 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          AI-Powered Role-Specific Synthesis
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Targeted Resume Generator
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto leading-relaxed">
          Provide your target role, job description, reference resume, and current experience level in one simple form.
        </p>
      </div>

      {/* Quick Fill Sample Trigger */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleQuickFillSample}
          disabled={submitting}
          className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Auto-fill Java Developer sample inputs
        </button>
      </div>

      {/* Notifications & Error Alerts */}
      {infoNotice && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-center justify-between gap-3 animate-in fade-in duration-200">
          <div className="flex items-center gap-2.5">
            <Info className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span className="font-medium">{infoNotice}</span>
          </div>
          <button 
            type="button" 
            onClick={() => setInfoNotice(null)}
            className="text-amber-400 hover:text-amber-200 p-1"
            title="Dismiss notice"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start justify-between gap-3 animate-in fade-in duration-200">
          <div className="flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-200">Analysis Request Failed</p>
              <p className="mt-0.5 text-rose-300/90 leading-relaxed">{error}</p>
            </div>
          </div>
          <button 
            type="button" 
            onClick={() => setError('')}
            className="text-rose-400 hover:text-rose-200 p-1"
            title="Dismiss error"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* SINGLE-PAGE FORM */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* SECTION A: TARGET JOB DETAILS */}
        <div className="p-6 sm:p-7 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-indigo-400" />
              Target Job Details
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Specify your target position and job requirements. The AI aligns your profile and optimizes summary & bullets for this role.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Target Job Role (Required) */}
            <div className="space-y-1.5">
              <label htmlFor="target-role-input" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                Target Job Role <span className="text-rose-400">*</span>
              </label>
              <div className="relative">
                <input
                  id="target-role-input"
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  required
                  disabled={submitting}
                  placeholder="e.g. Java Developer, Backend Engineer, Cloud Architect"
                  className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-60"
                />
              </div>
            </div>

            {/* Target Company (Optional) */}
            <div className="space-y-1.5">
              <label htmlFor="target-company-input" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                Target Company (Optional)
              </label>
              <input
                id="target-company-input"
                type="text"
                value={targetCompany}
                onChange={(e) => setTargetCompany(e.target.value)}
                disabled={submitting}
                placeholder="e.g. Mastercard, Google, Amazon, Enterprise Tech"
                className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-60"
              />
            </div>
          </div>

          {/* Job Description (Required) */}
          <div className="space-y-3 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                Job Description <span className="text-rose-400">*</span>
              </label>

              {/* Input Method Toggle */}
              <div className="inline-flex p-1 rounded-xl bg-slate-950 border border-slate-800 w-fit">
                <button
                  type="button"
                  onClick={() => setJdMethod('paste')}
                  disabled={submitting}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    jdMethod === 'paste' 
                      ? 'bg-indigo-600 text-white shadow-sm' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Direct Text Input
                </button>
                <button
                  type="button"
                  onClick={() => setJdMethod('upload')}
                  disabled={submitting}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    jdMethod === 'upload' 
                      ? 'bg-indigo-600 text-white shadow-sm' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Upload JD Document (PDF/DOCX)
                </button>
              </div>
            </div>

            {jdMethod === 'paste' ? (
              <div className="space-y-1.5">
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  disabled={submitting}
                  rows={8}
                  placeholder="Paste the full job description here, including responsibilities, mandatory/preferred skills, qualifications, and required tech stack..."
                  className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed disabled:opacity-60"
                />
              </div>
            ) : (
              <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-6 sm:p-8 text-center space-y-3 bg-slate-950/60 transition-colors">
                <input
                  ref={jdFileInputRef}
                  id="jd-file-upload"
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  disabled={submitting}
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      setJdFile(e.target.files[0]);
                      setCachedJdId(null);
                      setError('');
                    }
                  }}
                />

                {!jdFile ? (
                  <div className="space-y-2">
                    <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto" />
                    <div>
                      <label 
                        htmlFor="jd-file-upload" 
                        className="cursor-pointer font-semibold text-sm text-indigo-400 hover:underline"
                      >
                        Click to upload Job Description
                      </label>
                      <p className="text-xs text-slate-500 mt-1">Supports PDF, DOCX, or TXT (Up to 10MB)</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-200 text-xs">
                    <div className="flex items-center gap-2.5 truncate max-w-full">
                      <FileCheck2 className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                      <div className="text-left truncate">
                        <p className="font-semibold text-white truncate">{jdFile.name}</p>
                        <p className="text-[11px] text-slate-400">
                          {(jdFile.size / 1024).toFixed(1)} KB • Document Ready
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button
                        type="button"
                        onClick={() => jdFileInputRef.current?.click()}
                        disabled={submitting}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1 transition-colors"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Replace
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setJdFile(null);
                          setCachedJdId(null);
                        }}
                        disabled={submitting}
                        className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-medium flex items-center gap-1 transition-colors"
                      >
                        <Trash2 className="w-3 h-3" />
                        Remove
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* SECTION B: REFERENCE RESUME */}
        <div className="p-6 sm:p-7 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-indigo-400" />
              Reference Resume (Optional)
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Upload your existing resume to seed contact details and baseline formatting. If omitted, your resume will be synthesized directly from your career profile database.
            </p>
          </div>

          <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-6 sm:p-7 text-center space-y-3 bg-slate-950/60 transition-colors">
            <input
              ref={resumeFileInputRef}
              id="resume-file-upload"
              type="file"
              accept=".pdf,.docx,.doc"
              disabled={submitting}
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  setResumeFile(e.target.files[0]);
                  setCachedResumeId(null);
                }
              }}
            />

            {!resumeFile ? (
              <div className="space-y-2">
                <UploadCloud className="w-9 h-9 text-indigo-400 mx-auto" />
                <div>
                  <label 
                    htmlFor="resume-file-upload" 
                    className="cursor-pointer font-semibold text-sm text-indigo-400 hover:underline"
                  >
                    Click to upload Reference Resume
                  </label>
                  <p className="text-xs text-slate-500 mt-1">Supports PDF or DOCX</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs">
                <div className="flex items-center gap-2.5 truncate max-w-full">
                  <FileCheck2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                  <div className="text-left truncate">
                    <p className="font-semibold text-white truncate">{resumeFile.name}</p>
                    <p className="text-[11px] text-slate-400">
                      {(resumeFile.size / 1024).toFixed(1)} KB • Reference Resume Attached
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    type="button"
                    onClick={() => resumeFileInputRef.current?.click()}
                    disabled={submitting}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1 transition-colors"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Replace
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setResumeFile(null);
                      setCachedResumeId(null);
                    }}
                    disabled={submitting}
                    className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-xs font-medium flex items-center gap-1 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                    Remove
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* SECTION C: CANDIDATE EXPERIENCE DETAILS */}
        <div className="p-6 sm:p-7 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Candidate Experience Details
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select your experience level and optionally add context or specific engineering achievements.
            </p>
          </div>

          <div className="space-y-4">
            {/* Experience Level Dropdown */}
            <div className="space-y-1.5">
              <label htmlFor="experience-level-select" className="text-xs font-semibold text-slate-300">
                Experience Level <span className="text-rose-400">*</span>
              </label>
              <select
                id="experience-level-select"
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                disabled={submitting}
                className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-60"
              >
                {EXPERIENCE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value} className="bg-slate-950 text-slate-100 py-2">
                    {opt.label}
                  </option>
                ))}
              </select>

              {selectedExpDesc && (
                <p className="text-[11px] text-indigo-300/80 pt-1 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                  {selectedExpDesc}
                </p>
              )}
            </div>

            {/* Optional Additional Experience Details Textarea */}
            <div className="space-y-1.5 pt-1">
              <label htmlFor="additional-experience-input" className="text-xs font-semibold text-slate-300">
                Additional Experience Details (Optional)
              </label>
              <textarea
                id="additional-experience-input"
                value={additionalDetails}
                onChange={(e) => setAdditionalDetails(e.target.value)}
                disabled={submitting}
                rows={3}
                placeholder="e.g. 'I completed a six-month software development internship where I worked on backend development, REST APIs, and database integration.'"
                className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed disabled:opacity-60"
              />
            </div>
          </div>
        </div>

        {/* SECTION D: SUBMIT BUTTON */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-sm shadow-xl shadow-indigo-500/25 flex items-center justify-center gap-2.5 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed group"
          >
            <Sparkles className="w-4 h-4 text-indigo-200 group-hover:rotate-12 transition-transform" />
            <span>Analyze &amp; Generate Resume</span>
          </button>
        </div>

      </form>

    </div>
  );
}
