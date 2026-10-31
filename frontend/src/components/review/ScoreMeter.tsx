'use client';

import React from 'react';
import { ResumeMatchReport } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck, Tag, Target } from 'lucide-react';

interface ScoreMeterProps {
  report?: ResumeMatchReport;
  compact?: boolean;
}

export default function ScoreMeter({ report, compact = false }: ScoreMeterProps) {
  if (!report) {
    return (
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm">
        Calculating JD Match Report...
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 60) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  const getProgressGradient = (score: number) => {
    if (score >= 80) return 'from-emerald-500 to-teal-400';
    if (score >= 60) return 'from-amber-500 to-yellow-400';
    return 'from-rose-500 to-red-400';
  };

  return (
    <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 backdrop-blur-md shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-400" />
            JD Match & Evidence Report
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Deterministic coverage calculated from target Job Description & verified candidate evidence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-400">ATS Readiness:</span>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${getScoreColor(report.overall_evidence_score)}`}>
            {report.overall_evidence_score >= 80 ? 'High Match' : report.overall_evidence_score >= 60 ? 'Moderate Match' : 'Needs Evidence'}
          </span>
        </div>
      </div>

      {/* Main Dual Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Evidence Score */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-slate-950 to-slate-900 border border-indigo-500/20 shadow-inner">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              Evidence-Backed Coverage
            </span>
            <span className="text-2xl font-black tracking-tight text-white">
              {report.overall_evidence_score}%
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-full rounded-full bg-gradient-to-r ${getProgressGradient(report.overall_evidence_score)} transition-all duration-700`}
              style={{ width: `${Math.min(100, report.overall_evidence_score)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Weighted on confirmed technical background, projects & skills.
          </p>
        </div>

        {/* Keyword Coverage */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-slate-950 to-slate-900 border border-violet-500/20 shadow-inner">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-violet-300 flex items-center gap-1.5">
              <Tag className="w-4 h-4 text-violet-400" />
              Resume Keyword Coverage
            </span>
            <span className="text-2xl font-black tracking-tight text-white">
              {report.keyword_coverage_score}%
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-full rounded-full bg-gradient-to-r ${getProgressGradient(report.keyword_coverage_score)} transition-all duration-700`}
              style={{ width: `${Math.min(100, report.keyword_coverage_score)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Percentage of ATS industry keywords embedded organically.
          </p>
        </div>
      </div>

      {/* Sub-Metric Bars */}
      <div className="space-y-3 pt-2">
        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Mandatory Skills Coverage</span>
            <span className="text-slate-200 font-semibold">{report.mandatory_skills_score}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, report.mandatory_skills_score)}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Preferred Skills Coverage</span>
            <span className="text-slate-200 font-semibold">{report.preferred_skills_score}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, report.preferred_skills_score)}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Experience & Seniority Alignment</span>
            <span className="text-slate-200 font-semibold">{report.experience_relevance_score}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-indigo-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, report.experience_relevance_score)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Skills Pill Breakdown */}
      {!compact && (
        <div className="space-y-4 pt-4 border-t border-slate-800">
          {/* Matched Mandatory Skills */}
          {report.matched_mandatory_skills && report.matched_mandatory_skills.length > 0 && (
            <div>
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Matched Mandatory Skills ({report.matched_mandatory_skills.length})
              </span>
              <div className="flex flex-wrap gap-1.5">
                {report.matched_mandatory_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Missing / Gap Skills */}
          {report.missing_mandatory_skills && report.missing_mandatory_skills.length > 0 && (
            <div>
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Missing JD Mandatory Skills (Need Confirmation)
              </span>
              <div className="flex flex-wrap gap-1.5">
                {report.missing_mandatory_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Unbacked Evidence Gaps */}
          {report.evidence_gaps && report.evidence_gaps.length > 0 && (
            <div className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/20">
              <span className="text-xs font-semibold text-rose-300 flex items-center gap-1.5 mb-1.5">
                <XCircle className="w-3.5 h-3.5 text-rose-400" />
                Identified Evidence Gaps (Protected from Hallucination)
              </span>
              <p className="text-[11px] text-slate-400 mb-2">
                The AI intentionally did not fabricate the following technologies into your resume because no supporting proof was found in your career profile:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {report.evidence_gaps.map((gap, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30"
                  >
                    {gap}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
