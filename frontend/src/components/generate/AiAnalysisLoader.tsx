'use client';

import React, { useEffect, useState } from 'react';
import { 
  X, 
  Sparkles, 
  Check, 
  Loader2, 
  UploadCloud, 
  FileText, 
  BrainCircuit, 
  ShieldCheck, 
  Target, 
  Layers,
  FileCheck2
} from 'lucide-react';

export interface AiAnalysisLoaderProps {
  isOpen: boolean;
  targetRole: string;
  targetCompany?: string;
  hasJdFile: boolean;
  hasResumeFile: boolean;
  isUploadPhase: boolean;
  isSuccess?: boolean;
  onCancel: () => void;
}

interface StepItem {
  id: number;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const ANALYSIS_PIPELINE: StepItem[] = [
  {
    id: 1,
    label: 'Uploading your resume and job description...',
    description: 'Securely transmitting documents to processing engine',
    icon: UploadCloud,
  },
  {
    id: 2,
    label: 'Extracting information from your resume...',
    description: 'Parsing contact details, work history, and skills baseline',
    icon: FileCheck2,
  },
  {
    id: 3,
    label: 'Analyzing the Job Description...',
    description: 'Evaluating role responsibilities and domain context',
    icon: FileText,
  },
  {
    id: 4,
    label: 'Identifying mandatory and preferred skills...',
    description: 'Extracting key technical requirements and qualification criteria',
    icon: Target,
  },
  {
    id: 5,
    label: 'Analyzing your professional experience...',
    description: 'Cross-referencing your complete career database',
    icon: Layers,
  },
  {
    id: 6,
    label: 'Matching your career profile with job requirements...',
    description: 'Calculating evidence coverage and alignment strength',
    icon: BrainCircuit,
  },
  {
    id: 7,
    label: 'Optimizing resume content for the target role...',
    description: 'Synthesizing role-targeted impact statements & achievements',
    icon: Sparkles,
  },
  {
    id: 8,
    label: 'Generating ATS compatibility report...',
    description: 'Validating keyword coverage, structure, and evidence metrics',
    icon: ShieldCheck,
  },
  {
    id: 9,
    label: 'Preparing your updated resume...',
    description: 'Finalizing review draft with Human-in-the-Loop highlights',
    icon: FileText,
  },
];

export default function AiAnalysisLoader({
  isOpen,
  targetRole,
  targetCompany,
  hasJdFile,
  hasResumeFile,
  isUploadPhase,
  isSuccess = false,
  onCancel,
}: AiAnalysisLoaderProps) {
  const [activeStepIndex, setActiveStepIndex] = useState(isUploadPhase ? 0 : 1);
  const [progress, setProgress] = useState(isUploadPhase ? 15 : 25);

  const effectiveProgress = isSuccess ? 100 : progress;
  const effectiveStepIndex = isSuccess ? ANALYSIS_PIPELINE.length - 1 : activeStepIndex;

  useEffect(() => {
    if (!isOpen || isSuccess) return;

    if (isUploadPhase) {
      const uploadTimer = setTimeout(() => {
        setActiveStepIndex(0);
        setProgress(18);
      }, 50);
      return () => clearTimeout(uploadTimer);
    }

    // Step progression timer during active AI analysis
    const stepIntervals = [
      { step: 1, delay: 500, targetProgress: 32 },
      { step: 2, delay: 3000, targetProgress: 44 },
      { step: 3, delay: 6500, targetProgress: 56 },
      { step: 4, delay: 10000, targetProgress: 67 },
      { step: 5, delay: 14000, targetProgress: 76 },
      { step: 6, delay: 18500, targetProgress: 84 },
      { step: 7, delay: 23000, targetProgress: 89 },
      { step: 8, delay: 27500, targetProgress: 92 },
    ];

    const timeouts: NodeJS.Timeout[] = [];

    stepIntervals.forEach(({ step, delay, targetProgress }) => {
      const t = setTimeout(() => {
        setActiveStepIndex(step);
        setProgress((prev) => (prev < targetProgress ? targetProgress : prev));
      }, delay);
      timeouts.push(t);
    });

    // Gentle progress ticker so the progress bar never freezes during long LLM calls
    const ticker = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 92) return 92;
        return +(prev + 0.4).toFixed(1);
      });
    }, 1500);

    return () => {
      timeouts.forEach(clearTimeout);
      clearInterval(ticker);
    };
  }, [isOpen, isUploadPhase, isSuccess]);

  // Keyboard shortcut: Press Escape to cancel analysis
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  const currentStep = ANALYSIS_PIPELINE[effectiveStepIndex] || ANALYSIS_PIPELINE[0];

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-slate-950/90 backdrop-blur-xl animate-in fade-in duration-300"
      role="dialog"
      aria-modal="true"
      aria-label="AI Resume Analysis in Progress"
    >
      {/* Background glowing ambience */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-indigo-600/15 rounded-full blur-[120px]" />
        <div className="absolute -bottom-40 left-1/3 w-[500px] h-[500px] bg-violet-600/10 rounded-full blur-[140px]" />
        <div className="absolute top-1/3 right-10 w-[350px] h-[350px] bg-cyan-500/10 rounded-full blur-[100px]" />
      </div>

      {/* Prominent Cancel Button in Top-Right Corner */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-20 flex items-center gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="group flex items-center gap-2 px-3.5 py-2 rounded-full bg-slate-900/90 border border-slate-700/80 hover:border-rose-500/60 hover:bg-rose-500/10 text-slate-300 hover:text-rose-300 shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-rose-500/50"
          title="Cancel Analysis and Return to Form"
          aria-label="Cancel Resume Analysis"
        >
          <span className="text-xs font-semibold hidden sm:inline">Cancel Analysis</span>
          <div className="w-5 h-5 rounded-full bg-slate-800 group-hover:bg-rose-500/20 flex items-center justify-center transition-colors">
            <X className="w-3.5 h-3.5 text-slate-300 group-hover:text-rose-400" />
          </div>
        </button>
      </div>

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-xl mx-auto flex flex-col items-center text-center space-y-6 my-auto py-6">
        
        {/* Animated AI Neural Network Core Visual */}
        <div className="relative w-36 h-36 flex items-center justify-center">
          {/* Outer Pulsing Glow */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-indigo-500/30 via-violet-500/20 to-cyan-400/30 blur-2xl animate-pulse" />

          {/* SVG Neural Orbital Rings & Synaptic Beams */}
          <svg className="w-full h-full absolute inset-0 animate-[spin_18s_linear_infinite]" viewBox="0 0 144 144">
            <circle
              cx="72"
              cy="72"
              r="66"
              fill="none"
              stroke="rgba(99, 102, 241, 0.25)"
              strokeWidth="1.5"
              strokeDasharray="6 8"
            />
            {/* Synaptic nodes */}
            <circle cx="72" cy="6" r="3.5" fill="#818cf8" className="animate-ping" style={{ animationDuration: '3s' }} />
            <circle cx="138" cy="72" r="3" fill="#38bdf8" />
            <circle cx="72" cy="138" r="3" fill="#a855f7" />
            <circle cx="6" cy="72" r="3" fill="#6366f1" />
          </svg>

          {/* Counter-rotating inner ring */}
          <svg className="w-28 h-28 absolute inset-3 animate-[spin_12s_linear_infinite_reverse]" viewBox="0 0 112 112">
            <circle
              cx="56"
              cy="56"
              r="48"
              fill="none"
              stroke="rgba(56, 189, 248, 0.3)"
              strokeWidth="1.5"
              strokeDasharray="4 6"
            />
            <circle cx="56" cy="8" r="2.5" fill="#38bdf8" />
            <circle cx="104" cy="56" r="2.5" fill="#c084fc" />
            <circle cx="56" cy="104" r="2.5" fill="#818cf8" />
            <circle cx="8" cy="56" r="2.5" fill="#38bdf8" />
          </svg>

          {/* Central AI Brain Node */}
          <div className="relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 p-0.5 shadow-2xl shadow-indigo-500/40 border border-indigo-400/30 flex items-center justify-center group">
            <div className="w-full h-full rounded-2xl bg-slate-950/80 flex items-center justify-center backdrop-blur-sm relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-indigo-500/20 to-transparent animate-pulse" />
              <BrainCircuit className="w-9 h-9 text-indigo-300 animate-pulse relative z-10" />
            </div>
          </div>
        </div>

        {/* Header Text */}
        <div className="space-y-1.5 max-w-md">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" style={{ animationDuration: '4s' }} />
            <span>AI Neural Synthesis Engine Active</span>
          </div>

          <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
            Synthesizing Role-Targeted Resume
          </h2>

          <p className="text-xs sm:text-sm text-slate-400">
            Targeting <span className="text-indigo-300 font-semibold">{targetRole}</span>
            {targetCompany && (
              <> at <span className="text-slate-200 font-semibold">{targetCompany}</span></>
            )}
          </p>

          {(hasResumeFile || hasJdFile) && (
            <div className="flex items-center justify-center gap-2 pt-1 text-[11px] text-slate-400">
              {hasResumeFile && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                  <Check className="w-3 h-3 text-emerald-400" /> Reference Resume
                </span>
              )}
              {hasJdFile && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                  <Check className="w-3 h-3 text-emerald-400" /> JD Document
                </span>
              )}
            </div>
          )}
        </div>

        {/* Progress Bar & Percentage */}
        <div className="w-full max-w-md space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              {isSuccess ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Ready
                </span>
              ) : (
                <span className="text-indigo-400 flex items-center gap-1.5">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> In Progress
                </span>
              )}
            </span>
            <span className="text-xs font-mono font-bold text-slate-400">
              {Math.round(effectiveProgress)}%
            </span>
          </div>

          <div className="w-full h-2 rounded-full bg-slate-900 border border-slate-800/90 overflow-hidden relative shadow-inner">
            <div
              className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-violet-500 to-cyan-400 transition-all duration-500 ease-out relative"
              style={{ width: `${effectiveProgress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse" />
            </div>
          </div>
        </div>

        {/* Real-time Dynamic Stage Pipeline Display */}
        <div className="w-full max-w-md rounded-2xl bg-slate-900/70 border border-slate-800/80 p-4 sm:p-5 shadow-2xl backdrop-blur-md text-left space-y-3">
          
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/70">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
              Processing Pipeline
            </div>
            <div className="text-[11px] text-slate-400 font-medium">
              Stage {Math.min(effectiveStepIndex + 1, ANALYSIS_PIPELINE.length)} of {ANALYSIS_PIPELINE.length}
            </div>
          </div>

          {/* Current Active Highlight Box */}
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-start gap-3">
            <div className="mt-0.5 p-1.5 rounded-lg bg-indigo-600/20 text-indigo-300">
              {isSuccess ? (
                <Check className="w-4 h-4 text-emerald-400" />
              ) : (
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold text-white flex items-center gap-2">
                <span>{currentStep.label}</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                {currentStep.description}
              </p>
            </div>
          </div>

          {/* Compact Pipeline Stages Summary */}
          <div className="space-y-1.5 pt-1 max-h-44 overflow-y-auto pr-1">
            {ANALYSIS_PIPELINE.map((step, idx) => {
              const isPast = effectiveStepIndex > idx || isSuccess;
              const isCurrent = effectiveStepIndex === idx && !isSuccess;

              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                    isCurrent
                      ? 'bg-slate-800/90 text-slate-100 font-medium border border-slate-700/60'
                      : isPast
                      ? 'text-slate-400'
                      : 'text-slate-600'
                  }`}
                >
                  <div className="w-4 h-4 flex-shrink-0 flex items-center justify-center">
                    {isPast ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : isCurrent ? (
                      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    ) : (
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-700" />
                    )}
                  </div>
                  <span className="truncate">{step.label}</span>
                </div>
              );
            })}
          </div>

          {/* Transparent Status Note */}
          <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5 text-slate-400">
              <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
              Deep synthesis with Gemini AI (~15-30s)
            </span>
            <button
              type="button"
              onClick={onCancel}
              className="text-slate-400 hover:text-rose-400 underline font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>

        {/* Safety & Cancellation Note */}
        <p className="text-[11px] text-slate-400 max-w-sm leading-relaxed">
          You can cancel anytime. Your inputs and uploaded files will remain intact in the form.
        </p>

      </div>
    </div>
  );
}
