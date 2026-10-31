'use client';

import React, { useState } from 'react';
import { StructuredResumeData, ChangeDetail } from '@/lib/types';
import { 
  Building2, 
  Calendar, 
  MapPin, 
  Sparkles, 
  GraduationCap, 
  Award, 
  CheckCircle, 
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface StructuredResumeViewProps {
  resume: StructuredResumeData;
  changes?: ChangeDetail[];
}

export default function StructuredResumeView({ resume, changes = [] }: StructuredResumeViewProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'audit'>('preview');

  // Map of text snippets to change detail for inline visual cueing
  const changeMap = new Map<string, ChangeDetail>();
  changes.forEach((ch) => {
    if (ch.updated_content) {
      changeMap.set(ch.updated_content.trim().toLowerCase(), ch);
    }
  });

  const getHighlightClass = (text: string) => {
    const clean = text.trim().toLowerCase();
    const match = changeMap.get(clean);
    if (!match) return '';
    if (match.change_type === 'ADDED') return 'bg-emerald-500/15 border-l-2 border-emerald-500 pl-2 text-emerald-100';
    if (match.change_type === 'MODIFIED') return 'bg-amber-500/15 border-l-2 border-amber-500 pl-2 text-amber-100';
    if (match.change_type === 'REMOVED') return 'bg-rose-500/15 border-l-2 border-rose-500 pl-2 text-rose-100 line-through';
    return '';
  };

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden">
      {/* Top Header / View Toggle */}
      <div className="bg-slate-950/80 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Optimized Resume Snapshot
          </h2>
        </div>
        <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'preview'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Formatted Resume View
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'audit'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            Audit Changes ({changes.length})
          </button>
        </div>
      </div>

      {activeTab === 'preview' ? (
        <div className="p-8 sm:p-12 space-y-8 bg-slate-900/60 max-w-4xl mx-auto">
          {/* Resume Header */}
          <div className="text-center pb-6 border-b border-slate-800">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {resume.header.full_name}
            </h1>
            <p className="text-sm sm:text-base font-semibold text-indigo-400 mt-1">
              {resume.header.headline}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs text-slate-400 mt-2">
              {resume.header.email && <span>{resume.header.email}</span>}
              {resume.header.phone && <span>&bull; {resume.header.phone}</span>}
              {resume.header.location && <span>&bull; {resume.header.location}</span>}
              {resume.header.linkedin_url && (
                <span>&bull; <a href={resume.header.linkedin_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">LinkedIn</a></span>
              )}
              {resume.header.github_url && (
                <span>&bull; <a href={resume.header.github_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">GitHub</a></span>
              )}
            </div>
          </div>

          {/* Professional Summary */}
          {resume.summary && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Professional Summary
              </h3>
              <p className={`text-sm text-slate-300 leading-relaxed rounded p-1 ${getHighlightClass(resume.summary)}`}>
                {resume.summary}
              </p>
            </section>
          )}

          {/* Technical Skills */}
          {resume.skills && (
            <section className="space-y-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Technical Skills
              </h3>
              <div className="space-y-1.5 text-xs text-slate-300">
                {resume.skills.languages?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Programming Languages:</span>
                    <span>{resume.skills.languages.join(', ')}</span>
                  </div>
                )}
                {resume.skills.frameworks?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Frameworks & Libraries:</span>
                    <span>{resume.skills.frameworks.join(', ')}</span>
                  </div>
                )}
                {resume.skills.databases?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Databases & Storage:</span>
                    <span>{resume.skills.databases.join(', ')}</span>
                  </div>
                )}
                {resume.skills.cloud_and_devops?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Cloud & DevOps:</span>
                    <span>{resume.skills.cloud_and_devops.join(', ')}</span>
                  </div>
                )}
                {resume.skills.developer_tools?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Tools & Architecture:</span>
                    <span>{resume.skills.developer_tools.join(', ')}</span>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Work Experience */}
          {resume.work_experience && resume.work_experience.length > 0 && (
            <section className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Work Experience
              </h3>
              <div className="space-y-4">
                {resume.work_experience.map((exp, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <div className="text-sm font-bold text-white">
                        {exp.title} <span className="font-normal text-slate-400">&mdash; {exp.company}</span>
                      </div>
                      <div className="text-xs text-slate-400 font-medium">
                        {exp.location ? `${exp.location} | ` : ''}{exp.start_date} &ndash; {exp.end_date || 'Present'}
                      </div>
                    </div>
                    {exp.technologies && exp.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {exp.technologies.map((t, tIdx) => (
                          <span key={tIdx} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                    <ul className="space-y-1 pl-4 list-disc text-xs text-slate-300">
                      {exp.bullet_points.map((b, bIdx) => (
                        <li key={bIdx} className={`leading-relaxed rounded ${getHighlightClass(b)}`}>
                          {b}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Key Projects */}
          {resume.projects && resume.projects.length > 0 && (
            <section className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Key Projects
              </h3>
              <div className="space-y-4">
                {resume.projects.map((proj, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <div className="text-sm font-bold text-white flex items-center gap-1.5">
                        {proj.title}
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300">
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                      <div className="text-xs text-slate-400 font-medium">
                        {proj.role}
                      </div>
                    </div>
                    {proj.technologies && proj.technologies.length > 0 && (
                      <p className="text-[11px] text-indigo-300 italic">
                        Technologies: {proj.technologies.join(', ')}
                      </p>
                    )}
                    {proj.description && (
                      <p className="text-xs text-slate-300">{proj.description}</p>
                    )}
                    {proj.highlights && proj.highlights.length > 0 && (
                      <ul className="space-y-1 pl-4 list-disc text-xs text-slate-300">
                        {proj.highlights.map((h, hIdx) => (
                          <li key={hIdx} className={`leading-relaxed rounded ${getHighlightClass(h)}`}>
                            {h}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Education */}
          {resume.education && resume.education.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Education
              </h3>
              <div className="space-y-2">
                {resume.education.map((edu, idx) => (
                  <div key={idx} className="flex justify-between items-baseline text-xs">
                    <div>
                      <span className="font-bold text-white">{edu.degree}</span>
                      <span className="text-slate-400"> &mdash; {edu.institution}</span>
                      {edu.grade && <span className="text-slate-400"> ({edu.grade})</span>}
                    </div>
                    <span className="text-slate-400">{edu.start_date} - {edu.end_date}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Certifications */}
          {resume.certifications && resume.certifications.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Certifications
              </h3>
              <div className="space-y-1.5 text-xs text-slate-300">
                {resume.certifications.map((cert, idx) => (
                  <div key={idx} className="flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-amber-400" />
                    <span className="font-semibold text-white">{cert.name}</span>
                    <span className="text-slate-400">&mdash; {cert.issuing_organization}</span>
                    {cert.issue_date && <span className="text-slate-500">({cert.issue_date})</span>}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      ) : (
        /* Audit Trail View */
        <div className="p-6 space-y-4">
          <div className="flex items-center gap-4 text-xs font-semibold px-2 py-1">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              Green: Newly Added
            </span>
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              Yellow: Modified / Rephrased
            </span>
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              Red: Omitted / Replaced
            </span>
          </div>

          <div className="space-y-3">
            {changes.map((ch, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border ${
                  ch.change_type === 'ADDED'
                    ? 'bg-emerald-950/20 border-emerald-500/30'
                    : ch.change_type === 'MODIFIED'
                    ? 'bg-amber-950/20 border-amber-500/30'
                    : 'bg-rose-950/20 border-rose-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    {ch.section}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      ch.change_type === 'ADDED'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : ch.change_type === 'MODIFIED'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    }`}
                  >
                    {ch.change_type}
                  </span>
                </div>

                {ch.original_content && (
                  <div className="mb-2 text-xs">
                    <span className="text-slate-400 font-medium">Original: </span>
                    <span className="text-slate-400 line-through bg-slate-800/60 px-1.5 py-0.5 rounded">
                      {ch.original_content}
                    </span>
                  </div>
                )}

                <div className="mb-2 text-xs">
                  <span className="text-slate-300 font-medium">Updated: </span>
                  <span className="text-white font-medium bg-slate-900 px-1.5 py-0.5 rounded">
                    {ch.updated_content}
                  </span>
                </div>

                <div className="pt-2 border-t border-slate-800/80 text-[11px] grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-400">
                  <div>
                    <span className="text-indigo-400 font-medium">Reason: </span>
                    {ch.reason}
                  </div>
                  <div>
                    <span className="text-emerald-400 font-medium">Profile Evidence: </span>
                    {ch.supporting_evidence || 'Career Profile background analysis'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
