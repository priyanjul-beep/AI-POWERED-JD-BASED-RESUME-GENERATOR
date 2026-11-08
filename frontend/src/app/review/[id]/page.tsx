'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import confetti from 'canvas-confetti';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { 
  ResumeGeneration, 
  ResumeVersion, 
  ProposedContentItem
} from '@/lib/types';
import StructuredResumeView from '@/components/review/StructuredResumeView';
import ScoreMeter from '@/components/review/ScoreMeter';
import ApprovalModal from '@/components/review/ApprovalModal';
import { 
  CheckCircle2, 
  XCircle, 
  AlertOctagon, 
  Loader2, 
  Sparkles, 
  Download, 
  Eye, 
  FileCheck2,
  Clock,
  History
} from 'lucide-react';

export default function ResumeReviewPage() {
  const routeParams = useParams();
  const generationId = routeParams?.id as string;

  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [generation, setGeneration] = useState<ResumeGeneration | null>(null);
  const [selectedVersionNum, setSelectedVersionNum] = useState<number>(1);
  const [currentVersion, setCurrentVersion] = useState<ResumeVersion | null>(null);
  const [loading, setLoading] = useState(true);

  // NO comment revision state
  const [userComment, setUserComment] = useState('');
  const [isRevising, setIsRevising] = useState(false);
  const [revisionError, setRevisionError] = useState('');
  const [selectedProposedBullets, setSelectedProposedBullets] = useState<string[]>([]);

  // YES approval state
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [isFinalized, setIsFinalized] = useState(false);
  const [finalPdfUrl, setFinalPdfUrl] = useState('');
  const [finalDownloadUrl, setFinalDownloadUrl] = useState('');
  const [finalFilename, setFinalFilename] = useState('');

  // Cancel state
  const [isCancelling, setIsCancelling] = useState(false);

  const loadGeneration = useCallback(async () => {
    try {
      const data = await api.get<ResumeGeneration>(`/api/resume-generations/${generationId}/`);
      setGeneration(data);
      setSelectedVersionNum(data.current_version_number);

      const activeVer = data.versions.find(v => v.version_number === data.current_version_number) || data.versions[data.versions.length - 1];
      setCurrentVersion(activeVer || null);

      if (data.status === 'APPROVED') {
        setIsFinalized(true);
        setFinalPdfUrl(`${api.getBaseUrl()}/api/resume-generations/${data.id}/pdf/`);
        setFinalDownloadUrl(`${api.getBaseUrl()}/api/resume-generations/${data.id}/download/`);
      }
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [generationId]);

  useEffect(() => {
    let ignore = false;
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }
    if (user && generationId) {
      api.get<ResumeGeneration>(`/api/resume-generations/${generationId}/`)
        .then((data) => {
          if (ignore) return;
          setGeneration(data);
          setSelectedVersionNum(data.current_version_number);

          const activeVer = data.versions.find(v => v.version_number === data.current_version_number) || data.versions[data.versions.length - 1];
          setCurrentVersion(activeVer || null);

          if (data.status === 'APPROVED') {
            setIsFinalized(true);
            setFinalPdfUrl(`${api.getBaseUrl()}/api/resume-generations/${data.id}/pdf/`);
            setFinalDownloadUrl(`${api.getBaseUrl()}/api/resume-generations/${data.id}/download/`);
          }
        })
        .catch((err: unknown) => {
          console.error(err);
        })
        .finally(() => {
          if (!ignore) {
            setLoading(false);
          }
        });
    }
    return () => {
      ignore = true;
    };
  }, [user, authLoading, generationId, router]);

  const handleSelectVersion = (versionNum: number) => {
    if (!generation) return;
    setSelectedVersionNum(versionNum);
    const ver = generation.versions.find(v => v.version_number === versionNum);
    if (ver) {
      setCurrentVersion(ver);
      setSelectedProposedBullets([]);
    }
  };

  // Toggle Proposed Bullet Add / Revert into Feedback Box
  const handleToggleProposedBullet = (item: ProposedContentItem) => {
    const bulletKey = item.proposed_text.trim();
    const isAlreadySelected = selectedProposedBullets.includes(bulletKey);
    const formattedLine = `• Confirm & include into ${item.target_section}: "${bulletKey}"`;

    if (isAlreadySelected) {
      setSelectedProposedBullets(prev => prev.filter(k => k !== bulletKey));
      setUserComment(prev => {
        const lines = prev.split('\n');
        const remainingLines = lines.filter(line => !line.includes(bulletKey));
        return remainingLines.join('\n').replace(/\n{3,}/g, '\n\n').trim();
      });
    } else {
      setSelectedProposedBullets(prev => [...prev, bulletKey]);
      setUserComment(prev => {
        const trimmed = prev.trim();
        if (!trimmed) {
          return formattedLine;
        }
        return `${trimmed}\n\n${formattedLine}`;
      });
    }
  };

  // Human-in-the-Loop Step: Click NO
  const handleRevisionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userComment.trim()) {
      setRevisionError('Please enter revision feedback or instructions before clicking Submit Revision.');
      return;
    }

    setIsRevising(true);
    setRevisionError('');

    try {
      const updatedGen = await api.post<ResumeGeneration>(`/api/resume-generations/${generationId}/revise/`, {
        user_comment: userComment.trim(),
      });
      setGeneration(updatedGen);
      setSelectedVersionNum(updatedGen.current_version_number);
      const newActive = updatedGen.versions.find(v => v.version_number === updatedGen.current_version_number);
      setCurrentVersion(newActive || null);
      setUserComment('');
      setSelectedProposedBullets([]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit revision.';
      setRevisionError(msg);
    } finally {
      setIsRevising(false);
    }
  };

  // Human-in-the-Loop Step: Click YES (final approval)
  const handleApprovalConfirm = async (pageFormat: 'ONE_PAGE' | 'TWO_PAGE', customFilename: string, comment: string) => {
    try {
      const res = await api.post<{ filename: string }>(`/api/resume-generations/${generationId}/approve/`, {
        page_format: pageFormat,
        custom_filename: customFilename,
        user_comment: comment,
      });

      setIsFinalized(true);
      setFinalPdfUrl(`${api.getBaseUrl()}/api/resume-generations/${generationId}/pdf/`);
      setFinalDownloadUrl(`${api.getBaseUrl()}/api/resume-generations/${generationId}/download/`);
      setFinalFilename(res.filename);

      // Trigger celebratory confetti effect
      try {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch {
        // ignore in non-browser environments
      }

      await loadGeneration();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to finalize resume.';
      alert(msg);
      throw err;
    }
  };

  // CANCEL workflow
  const handleCancelSession = async () => {
    if (!confirm('Are you sure you want to cancel this resume generation session? The current draft will be preserved in your history, but no PDF will be finalized.')) {
      return;
    }

    setIsCancelling(true);
    try {
      await api.post(`/api/resume-generations/${generationId}/cancel/`);
      router.push('/dashboard');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to cancel session.';
      alert(msg);
      setIsCancelling(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  if (!generation || !currentVersion) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertOctagon className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Generation Session Not Found</h2>
        <p className="text-xs text-slate-400">The requested resume review session does not exist.</p>
        <button
          onClick={() => router.push('/dashboard')}
          className="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const candidateName = currentVersion.structured_resume_data.header.full_name || user?.username || 'candidate';
  const defaultFilename = `${candidateName.toLowerCase().replace(/\s+/g, '_')}_${(generation.target_company || 'company').toLowerCase().replace(/\s+/g, '_')}_${generation.target_role.toLowerCase().replace(/\s+/g, '_')}_v${selectedVersionNum}.pdf`;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
      {/* Top Banner & Control Bar */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-base font-bold text-white">{generation.target_role}</span>
            {generation.target_company && (
              <span className="text-xs text-slate-400">at {generation.target_company}</span>
            )}
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                generation.status === 'APPROVED'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : generation.status === 'CANCELLED'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
              }`}
            >
              {generation.status}
            </span>
          </div>
          <div className="text-xs text-slate-400 flex items-center gap-3">
            <span>Experience: <strong className="text-slate-300">{generation.experience_level}</strong></span>
            <span>&bull;</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              {new Date(generation.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>

        {/* Version History Selector & Cancel Button */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            <span className="text-[11px] font-semibold text-slate-400 px-2 flex items-center gap-1">
              <History className="w-3.5 h-3.5" />
              Versions:
            </span>
            {generation.versions.map((v) => (
              <button
                key={v.version_number}
                onClick={() => handleSelectVersion(v.version_number)}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                  selectedVersionNum === v.version_number
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                v{v.version_number}
              </button>
            ))}
          </div>

          {generation.status !== 'CANCELLED' && !isFinalized && (
            <button
              onClick={handleCancelSession}
              disabled={isCancelling}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 border border-slate-700 hover:border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 transition-all"
            >
              <XCircle className="w-4 h-4" />
              Cancel Workflow
            </button>
          )}
        </div>
      </div>

      {/* FINALIZED SUCCESS BANNER */}
      {isFinalized && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-teal-950/80 border border-emerald-500/30 shadow-2xl space-y-4 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/30">
                <FileCheck2 className="w-3.5 h-3.5" />
                Resume Successfully Finalized
              </div>
              <h3 className="text-xl font-extrabold text-white">Your ATS-Optimized PDF is Ready!</h3>
              <p className="text-xs text-slate-300">
                Saved in your Resume History under: <span className="font-mono text-emerald-300">{finalFilename || defaultFilename}</span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <a
                href={finalPdfUrl}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-2 border border-slate-700 transition-colors"
              >
                <Eye className="w-4 h-4 text-indigo-400" />
                Preview PDF
              </a>
              <a
                href={finalDownloadUrl}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Two-Column Review Layout: Left (Resume & Diffs), Right (Scores & Approvals) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left Column (2 Cols wide on desktop): Structured Resume with Highlight Cues */}
        <div className="lg:col-span-2 space-y-6">
          <StructuredResumeView
            resume={currentVersion.structured_resume_data}
            changes={currentVersion.change_analysis}
            selectedProposedBullets={selectedProposedBullets}
            onToggleProposedBullet={handleToggleProposedBullet}
          />
        </div>

        {/* Right Column (1 Col wide on desktop): Match Score & Approval System */}
        <div className="space-y-6 lg:sticky lg:top-24">
          {/* Match Score Progress Card */}
          <ScoreMeter report={currentVersion.match_report} />

          {/* YES / NO Human-in-the-Loop Decision Card */}
          {!isFinalized && generation.status !== 'CANCELLED' && (
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-5">
              <div className="space-y-1">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  Are you satisfied with this resume?
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Click <strong>YES</strong> to finalize your PDF, or <strong>NO</strong> with feedback instructions to re-optimize.
                </p>
              </div>

              {revisionError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                  {revisionError}
                </div>
              )}

              {/* Instructions / Feedback Box */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-300">
                    Instructions / Modification Notes (Required for NO)
                  </label>
                  {selectedProposedBullets.length > 0 && (
                    <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      {selectedProposedBullets.length} bullet{selectedProposedBullets.length > 1 ? 's' : ''} added
                    </span>
                  )}
                </div>
                <textarea
                  value={userComment}
                  onChange={(e) => setUserComment(e.target.value)}
                  rows={4}
                  disabled={isRevising}
                  placeholder="e.g. 'The technical skills section needs more relevant skills.' or click '+ Add to Feedback' on any proposed bullet to validate it."
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50"
                />
              </div>

              {/* Action Buttons: YES and NO */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                {/* NO Button: triggers revision */}
                <button
                  type="button"
                  onClick={handleRevisionSubmit}
                  disabled={isRevising}
                  className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-amber-500/40 text-slate-200 text-xs font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isRevising ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                      Revising Draft...
                    </>
                  ) : (
                    <>
                      <XCircle className="w-4 h-4 text-amber-400" />
                      NO &bull; Revise with Feedback
                    </>
                  )}
                </button>

                {/* YES Button: opens approval modal */}
                <button
                  type="button"
                  onClick={() => setApprovalModalOpen(true)}
                  disabled={isRevising}
                  className="py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  YES &bull; Approve Resume
                </button>
              </div>

              <div className="pt-2 border-t border-slate-800 text-center">
                <p className="text-[11px] text-slate-500">
                  Current Draft: Version {selectedVersionNum} of {generation.versions.length}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Approval Modal */}
      <ApprovalModal
        isOpen={approvalModalOpen}
        onClose={() => setApprovalModalOpen(false)}
        onConfirm={handleApprovalConfirm}
        defaultFilename={defaultFilename}
      />
    </div>
  );
}
