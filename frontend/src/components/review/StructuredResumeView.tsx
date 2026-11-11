'use client';

import React, { useState } from 'react';
import { 
  StructuredResumeData, 
  ChangeDetail, 
  ProposedContentItem,
  ResumeWorkExperience,
  ResumeProject
} from '@/lib/types';
import { 
  Sparkles, 
  Award, 
  ExternalLink,
  Lightbulb,
  Check,
  Code,
  Globe,
  Trophy,
  Plus,
  RotateCcw,
  CheckCircle2,
  Target,
  FileText
} from 'lucide-react';

interface ExtendedResumeData extends StructuredResumeData {
  experiences?: ResumeWorkExperience[];
  experience?: ResumeWorkExperience[];
  key_projects?: ResumeProject[];
  achievements_hackathons_coding?: string[];
  coding_and_hackathons?: string[];
  achievements_and_hackathons?: string[];
}

interface StructuredResumeViewProps {
  resume: StructuredResumeData;
  tailoredResume?: StructuredResumeData;
  changes?: ChangeDetail[];
  selectedProposedBullets?: string[];
  onToggleProposedBullet?: (item: ProposedContentItem) => void;
  activeResumeMode?: 'tailored' | 'general';
  onChangeResumeMode?: (mode: 'tailored' | 'general') => void;
}

export default function StructuredResumeView({ 
  resume, 
  tailoredResume,
  changes = [],
  selectedProposedBullets = [],
  onToggleProposedBullet,
  activeResumeMode = 'tailored',
  onChangeResumeMode
}: StructuredResumeViewProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'audit' | 'proposed'>('preview');

  const currentResume = (activeResumeMode === 'tailored' && tailoredResume) ? tailoredResume : resume;
  const extResume = currentResume as ExtendedResumeData;
  const proposedItems: ProposedContentItem[] = resume.proposed_content || [];
  const workExperiences = currentResume.work_experience || extResume.experiences || extResume.experience || [];
  const projectsList = currentResume.projects || extResume.key_projects || [];
  const achievementsAndCoding: string[] = 
    currentResume.achievements_and_coding ||
    extResume.achievements_hackathons_coding ||
    extResume.coding_and_hackathons ||
    extResume.achievements_and_hackathons ||
    [
      ...(currentResume.achievements || []),
      ...(currentResume.coding_profiles || []),
      ...(currentResume.hackathons || [])
    ];

  const handleModeChange = (mode: 'tailored' | 'general') => {
    if (onChangeResumeMode) {
      onChangeResumeMode(mode);
    }
  };

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
    if (match.change_type === 'PROPOSED') return 'bg-purple-500/15 border-l-2 border-purple-500 pl-2 text-purple-100';
    return '';
  };

  const renderFormattedText = (text: string | null | undefined): React.ReactNode => {
    if (!text) return null;
    const parts = text.split(/(\*\*[^*]+\*\*|__[^_]+__)/g);
    return parts.map((part, index) => {
      if ((part.startsWith('**') && part.endsWith('**')) || (part.startsWith('__') && part.endsWith('__'))) {
        const boldText = part.slice(2, -2);
        return (
          <strong key={index} className="font-bold text-white tracking-wide">
            {boldText}
          </strong>
        );
      }
      return <React.Fragment key={index}>{part}</React.Fragment>;
    });
  };

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden">
      {/* Top Header / View Toggle */}
      <div className="bg-slate-950/80 px-6 py-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Optimized Resume Snapshot
          </h2>
        </div>
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-medium">
          <button
            onClick={() => {
              handleModeChange('tailored');
              setActiveTab('preview');
            }}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'preview' && activeResumeMode === 'tailored'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-sm font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Target className="w-3.5 h-3.5 text-indigo-300" />
            <span>🎯 JD-Tailored View</span>
          </button>
          <button
            onClick={() => {
              handleModeChange('general');
              setActiveTab('preview');
            }}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'preview' && activeResumeMode === 'general'
                ? 'bg-gradient-to-r from-slate-700 to-slate-800 text-white shadow-sm font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-slate-300" />
            <span>📄 General Profile View</span>
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
            <span>Audit Changes ({changes.length})</span>
          </button>
          {proposedItems.length > 0 && (
            <button
              onClick={() => setActiveTab('proposed')}
              className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
                activeTab === 'proposed'
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'text-amber-400 hover:text-amber-200 bg-amber-500/10 border border-amber-500/30'
              }`}
            >
              <Lightbulb className="w-3.5 h-3.5" />
              <span>Proposed Bullets ({proposedItems.length})</span>
              {selectedProposedBullets.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-400 text-slate-950 font-bold">
                  {selectedProposedBullets.length} added
                </span>
              )}
            </button>
          )}
        </div>
      </div>

      {activeTab === 'preview' ? (
        <div className="p-8 sm:p-12 space-y-8 bg-slate-900/60 max-w-4xl mx-auto">
          {/* Active Mode Explanation Banner */}
          {activeResumeMode === 'tailored' ? (
            <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/25 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-indigo-200">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                <span>
                  <strong>🎯 JD-Tailored 1-Page View:</strong> Technical skills and experience bullet points that do not directly address the target JD requirements have been cleanly omitted for maximum ATS keyword relevance and single-page density.
                </span>
              </div>
              <button
                type="button"
                onClick={() => handleModeChange('general')}
                className="px-2.5 py-1 rounded bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-100 font-medium whitespace-nowrap text-[11px]"
              >
                Switch to General Resume &rarr;
              </button>
            </div>
          ) : (
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                <span>
                  <strong>📄 General Profile 1-Page View:</strong> Displays your full comprehensive career history, including all technical skills and employment bullet points, formatted to fit on one page.
                </span>
              </div>
              <button
                type="button"
                onClick={() => handleModeChange('tailored')}
                className="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium whitespace-nowrap text-[11px]"
              >
                Switch to JD-Tailored View &rarr;
              </button>
            </div>
          )}

          {/* Banner if Proposed Content Exists */}
          {proposedItems.length > 0 && (
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-3 text-xs text-amber-200">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span>
                  <strong>{proposedItems.length} Proposed Industry Bullets</strong> are available for review.
                  {selectedProposedBullets.length > 0 ? (
                    <span className="ml-1 text-emerald-300 font-bold">
                      ({selectedProposedBullets.length} validated &amp; added to revision feedback)
                    </span>
                  ) : (
                    <span> They have not been added to your factual resume history without confirmation.</span>
                  )}
                </span>
              </div>
              <button
                onClick={() => setActiveTab('proposed')}
                className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 font-medium whitespace-nowrap"
              >
                Review Suggestions &rarr;
              </button>
            </div>
          )}

          {/* Resume Header */}
          <div className="text-center pb-6 border-b border-slate-800">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {currentResume.header?.full_name}
            </h1>
            <p className="text-sm sm:text-base font-semibold text-indigo-400 mt-1">
              {currentResume.header?.headline}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs text-slate-400 mt-2">
              {currentResume.header?.email && <span>{currentResume.header.email}</span>}
              {currentResume.header?.phone && <span>&bull; {currentResume.header.phone}</span>}
              {currentResume.header?.location && <span>&bull; {currentResume.header.location}</span>}
              {currentResume.header?.linkedin_url && (
                <span>&bull; <a href={currentResume.header.linkedin_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">LinkedIn</a></span>
              )}
              {currentResume.header?.github_url && (
                <span>&bull; <a href={currentResume.header.github_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">GitHub</a></span>
              )}
            </div>
          </div>

          {/* Professional Summary */}
          {currentResume.summary && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Professional Summary
              </h3>
              <p className={`text-sm text-slate-300 leading-relaxed rounded p-1 ${getHighlightClass(currentResume.summary)}`}>
                {renderFormattedText(currentResume.summary)}
              </p>
            </section>
          )}

          {/* Technical Skills */}
          {currentResume.skills && (
            <section className="space-y-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Technical Skills
              </h3>
              <div className="space-y-1.5 text-xs text-slate-300">
                {currentResume.skills.languages?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Programming Languages:</span>
                    <span>{currentResume.skills.languages.join(', ')}</span>
                  </div>
                )}
                {currentResume.skills.frameworks?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Frameworks & Libraries:</span>
                    <span>{currentResume.skills.frameworks.join(', ')}</span>
                  </div>
                )}
                {currentResume.skills.databases?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Databases & Storage:</span>
                    <span>{currentResume.skills.databases.join(', ')}</span>
                  </div>
                )}
                {currentResume.skills.cloud_and_devops?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Cloud & DevOps:</span>
                    <span>{currentResume.skills.cloud_and_devops.join(', ')}</span>
                  </div>
                )}
                {currentResume.skills.developer_tools?.length > 0 && (
                  <div className="flex flex-wrap items-baseline gap-1.5">
                    <span className="font-semibold text-slate-200">Tools & Architecture:</span>
                    <span>{currentResume.skills.developer_tools.join(', ')}</span>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Work Experience */}
          {workExperiences.length > 0 && (
            <section className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Work Experience
              </h3>
              <div className="space-y-4">
                {workExperiences.map((exp, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <div className="text-sm font-bold text-white">
                        {exp.company} <span className="font-normal text-slate-400">&mdash; {exp.title}</span>
                      </div>
                      <div className="text-xs text-slate-400 font-medium">
                        {exp.location ? `${exp.location} | ` : ''}{exp.start_date} &ndash; {exp.end_date || 'Present'}
                      </div>
                    </div>
                    <ul className="space-y-1 pl-4 list-disc text-xs text-slate-300">
                      {exp.bullet_points.map((b, bIdx) => (
                        <li key={bIdx} className={`leading-relaxed rounded ${getHighlightClass(b)}`}>
                          {renderFormattedText(b)}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Key Projects */}
          {projectsList.length > 0 && (
            <section className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Key Projects
              </h3>
              <div className="space-y-4">
                {projectsList.map((proj, idx) => {
                  const projectLink = proj.github_url || proj.url;
                  const demoLink = proj.demo_url;
                  return (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="text-sm font-bold text-white flex flex-wrap items-center gap-2">
                          <span>{proj.title}</span>
                          {projectLink && (
                            <a
                              href={projectLink}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 border border-indigo-700/60 hover:border-indigo-400 transition-colors"
                              title="Project Repository / Source Link"
                            >
                              <Code className="w-3 h-3 text-indigo-400" />
                              <span>Project Link</span>
                              <ExternalLink className="w-2.5 h-2.5 opacity-70" />
                            </a>
                          )}
                          {demoLink && (
                            <a
                              href={demoLink}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/60 hover:border-emerald-400 transition-colors"
                              title="Live Demo Link"
                            >
                              <Globe className="w-3 h-3 text-emerald-400" />
                              <span>Live Demo</span>
                              <ExternalLink className="w-2.5 h-2.5 opacity-70" />
                            </a>
                          )}
                        </div>
                        {/* <div className="text-xs text-slate-400 font-medium">
                          {proj.role}
                        </div> */}
                      </div>
                      {proj.technologies && proj.technologies.length > 0 && (
                        <p className="text-[11px] text-indigo-300 italic">
                          Technologies: {proj.technologies.join(', ')}
                        </p>
                      )}
                      {proj.description && (
                        <p className="text-xs text-slate-300">{renderFormattedText(proj.description)}</p>
                      )}
                      {proj.highlights && proj.highlights.length > 0 && (
                        <ul className="space-y-1 pl-4 list-disc text-xs text-slate-300">
                          {proj.highlights.map((h, hIdx) => (
                            <li key={hIdx} className={`leading-relaxed rounded ${getHighlightClass(h)}`}>
                              {renderFormattedText(h)}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* Education */}
          {currentResume.education && currentResume.education.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Education
              </h3>
              <div className="space-y-2">
                {currentResume.education.map((edu, idx) => (
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
          {currentResume.certifications && currentResume.certifications.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1">
                Certifications
              </h3>
              <div className="space-y-1.5 text-xs text-slate-300">
                {currentResume.certifications.map((cert, idx) => (
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

          {/* Achievements, Hackathons & Coding Profiles */}
          {achievementsAndCoding.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 border-b border-indigo-500/20 pb-1 flex items-center gap-1.5">
                <Trophy className="w-3.5 h-3.5 text-amber-400" />
                <span>Achievements, Hackathons & Coding Profiles</span>
              </h3>
              <ul className="space-y-1.5 pl-4 list-disc text-xs text-slate-300">
                {achievementsAndCoding.map((item, idx) => (
                  <li key={idx} className={`leading-relaxed rounded ${getHighlightClass(item)}`}>
                    {renderFormattedText(item)}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      ) : activeTab === 'audit' ? (
        /* Audit Trail View */
        <div className="p-6 space-y-4">
          <div className="flex flex-wrap items-center gap-4 text-xs font-semibold px-2 py-1">
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
            <span className="flex items-center gap-1.5 text-purple-400">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
              Purple: Suggested / Pending Confirmation
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
                    : ch.change_type === 'PROPOSED'
                    ? 'bg-purple-950/20 border-purple-500/30'
                    : 'bg-rose-950/20 border-rose-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    {ch.section}
                  </span>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        ch.change_type === 'ADDED'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : ch.change_type === 'MODIFIED'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                          : ch.change_type === 'PROPOSED'
                          ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      }`}
                    >
                      {ch.change_type}
                    </span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        ch.confirmation_status === 'PENDING_CONFIRMATION' || ch.change_type === 'PROPOSED'
                          ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                      }`}
                    >
                      {ch.confirmation_status === 'PENDING_CONFIRMATION' || ch.change_type === 'PROPOSED'
                        ? 'Requires Confirmation'
                        : 'Verified'}
                    </span>
                  </div>
                </div>

                {ch.original_content && (
                  <div className="mb-2 text-xs">
                    <span className="text-slate-400 font-medium">Original: </span>
                    <span className="text-slate-400 line-through bg-slate-800/60 px-1.5 py-0.5 rounded">
                      {renderFormattedText(ch.original_content)}
                    </span>
                  </div>
                )}

                <div className="mb-2 text-xs">
                  <span className="text-slate-300 font-medium">Updated: </span>
                  <span className="text-white font-medium bg-slate-900 px-1.5 py-0.5 rounded">
                    {renderFormattedText(ch.updated_content)}
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
      ) : (
        /* Proposed Content & Suggestions View */
        <div className="p-6 space-y-5">
          <div className="p-4 rounded-xl bg-slate-950/90 border border-amber-500/30 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                Proposed Industry-Standard Bullets &amp; Suggested Experience
              </div>
              {selectedProposedBullets.length > 0 && (
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold flex items-center gap-1.5 shadow-sm">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  {selectedProposedBullets.length} Added to Feedback
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              These role-specific responsibility bullets were formulated to match important JD requirements.
              Because supporting evidence was not verified in your career records, they are held separately and will <strong>never be automatically published as factual employment</strong> without your explicit confirmation.
            </p>
            <div className="text-[11px] text-indigo-300 bg-indigo-950/30 p-2.5 rounded border border-indigo-500/20 flex items-start gap-2 mt-2">
              <Check className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
              <span>
                <strong>One-Click Workflow:</strong> Click <strong>&quot;+ Add to Feedback&quot;</strong> on any bullet below to automatically validate it and queue it into your revision feedback box. Click <strong>&quot;Revert&quot;</strong> to remove it. When you click <strong>NO &bull; Revise with Feedback</strong> in the review sidebar, your resume will be regenerated incorporating these validated bullets.
              </span>
            </div>
          </div>

          {selectedProposedBullets.length > 0 && (
            <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in">
              <div className="flex items-center gap-2.5 text-xs text-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>
                  <strong>{selectedProposedBullets.length} bullet{selectedProposedBullets.length > 1 ? 's' : ''}</strong> validated and queued in your revision feedback box.
                </span>
              </div>
              <div className="text-[11px] text-slate-400">
                Click &quot;NO &bull; Revise with Feedback&quot; to rebuild.
              </div>
            </div>
          )}

          <div className="space-y-3">
            {proposedItems.map((item, idx) => {
              const isSelected = selectedProposedBullets.includes(item.proposed_text.trim());
              return (
                <div
                  key={idx}
                  onClick={() => onToggleProposedBullet?.(item)}
                  className={`p-4 rounded-xl transition-all duration-200 cursor-pointer space-y-3 text-xs border ${
                    isSelected
                      ? 'bg-emerald-950/25 border-emerald-500/60 shadow-lg shadow-emerald-950/30 ring-1 ring-emerald-500/30'
                      : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`px-2 py-0.5 rounded font-semibold text-[10px] border ${
                        isSelected
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                      }`}>
                        Target: {item.target_section}
                      </span>
                      <span className="font-bold text-white text-xs">
                        Requirement: {item.targeted_jd_requirement}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {isSelected ? (
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold flex items-center gap-1">
                          <Check className="w-3 h-3 text-emerald-400" />
                          Validated for Inclusion
                        </span>
                      ) : (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 font-medium">
                          Requires User Confirmation
                        </span>
                      )}

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onToggleProposedBullet?.(item);
                        }}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm ${
                          isSelected
                            ? 'bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 hover:text-rose-200 border border-rose-500/30'
                            : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                        }`}
                      >
                        {isSelected ? (
                          <>
                            <RotateCcw className="w-3.5 h-3.5 text-rose-300" />
                            <span>Revert</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5 text-indigo-200" />
                            <span>+ Add to Feedback</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className={`p-3 rounded-lg border text-xs leading-relaxed transition-colors ${
                    isSelected
                      ? 'bg-slate-900/90 border-emerald-500/30 text-emerald-100 font-medium'
                      : 'bg-slate-900 border-slate-800 text-slate-200 font-medium'
                  }`}>
                    &ldquo;{renderFormattedText(item.proposed_text)}&rdquo;
                  </div>

                  <div className="text-[11px] text-slate-400 flex items-center justify-between">
                    <span><strong>Reason:</strong> {renderFormattedText(item.reason)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
