'use client';

import React, { useState } from 'react';
import { ResumeMatchReport, EvidenceGapItem } from '@/lib/types';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ShieldCheck, 
  Tag, 
  Target, 
  ChevronDown, 
  ChevronUp, 
  HelpCircle, 
  Lightbulb, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

interface ScoreMeterProps {
  report?: ResumeMatchReport;
  compact?: boolean;
}

export default function ScoreMeter({ report, compact = false }: ScoreMeterProps) {
  const [expandedGap, setExpandedGap] = useState<number | null>(null);

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

      {/* Skills Pill Breakdown & Gap Explanations */}
      {!compact && (
        <div className="space-y-5 pt-4 border-t border-slate-800">
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

          {/* Missing Mandatory Skills with Explanations */}
          {report.missing_mandatory_skills && report.missing_mandatory_skills.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Missing JD Mandatory Requirements ({report.missing_mandatory_skills.length})
              </span>
              <div className="space-y-2">
                {report.missing_mandatory_skills.map((skill, idx) => {
                  const explanation = report.missing_mandatory_explanations?.find(e => e.skill.toLowerCase() === skill.toLowerCase());
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-950/70 border border-amber-500/20 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-amber-300 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-amber-400" />
                          {skill}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-medium">
                          Requires Evidence
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        {explanation?.reason || "Not found in candidate profile or reference resume."}
                      </p>
                      <div className="text-[11px] text-indigo-300 bg-indigo-950/30 p-2 rounded border border-indigo-500/20 flex items-start gap-1.5">
                        <Lightbulb className="w-3.5 h-3.5 text-indigo-400 mt-0.5 flex-shrink-0" />
                        <span>
                          {explanation?.suggestion || `If you have worked with ${skill}, provide project details or specify it in a revision comment.`}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Evidence Gap Report (Interactive & Detailed) */}
          {report.evidence_gaps && report.evidence_gaps.length > 0 && (
            <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/25 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  Evidence Gap Report (Protected from Hallucination)
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/30">
                  {report.evidence_gaps.length} Gaps Audited
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                The AI intentionally did not fabricate the following requirements as factual employment because no supporting evidence was verified in your career records:
              </p>
              
              <div className="space-y-2">
                {report.evidence_gaps.map((gapItem, idx) => {
                  const reqName = typeof gapItem === 'string' ? gapItem : gapItem.requirement;
                  const reason = typeof gapItem === 'string' ? 'Evidence not found in candidate career profile.' : gapItem.reason_missing;
                  const transferable = typeof gapItem === 'object' ? gapItem.transferable_evidence : '';
                  const suggestion = typeof gapItem === 'object' ? gapItem.suggested_user_input : `If you have performed ${reqName}, submit details via NO revision.`;
                  const isExpanded = expandedGap === idx;

                  return (
                    <div
                      key={idx}
                      className="rounded-lg bg-slate-900/90 border border-slate-800 p-3 text-xs space-y-2"
                    >
                      <div 
                        className="flex items-center justify-between cursor-pointer select-none"
                        onClick={() => setExpandedGap(isExpanded ? null : idx)}
                      >
                        <div className="flex items-center gap-2">
                          <XCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                          <span className="font-semibold text-white">{reqName}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                            Evidence not found
                          </span>
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-slate-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-slate-400" />
                        )}
                      </div>

                      {isExpanded && (
                        <div className="pt-2 border-t border-slate-800 space-y-2 text-[11px] text-slate-300">
                          <div>
                            <span className="text-slate-400 font-medium">Why it is missing: </span>
                            <span>{reason}</span>
                          </div>
                          {transferable && (
                            <div className="text-teal-300 bg-teal-950/20 p-2 rounded border border-teal-500/20">
                              <span className="font-semibold">Transferable Evidence: </span>
                              {transferable}
                            </div>
                          )}
                          <div className="text-indigo-300 bg-indigo-950/30 p-2 rounded border border-indigo-500/20">
                            <span className="font-semibold">Suggested Action: </span>
                            {suggestion}
                          </div>
                          <div className="text-[10px] text-amber-400/90 flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3 text-amber-400" />
                            Requires candidate confirmation before entering verified resume claims.
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
