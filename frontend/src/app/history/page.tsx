'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { FinalizedResumeHistory, ResumeMatchReport } from '@/lib/types';
import ScoreMeter from '@/components/review/ScoreMeter';
import StructuredResumeView from '@/components/review/StructuredResumeView';
import { 
  History, 
  Calendar, 
  Eye, 
  Download, 
  Target, 
  X, 
  Loader2, 
  Sparkles
} from 'lucide-react';

export default function ResumeHistoryPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [historyList, setHistoryList] = useState<FinalizedResumeHistory[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal states
  const [viewResume, setViewResume] = useState<FinalizedResumeHistory | null>(null);
  const [matchReportItem, setMatchReportItem] = useState<{
    resume: FinalizedResumeHistory;
    report: ResumeMatchReport | null;
  } | null>(null);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  const handleDownloadPdf = async (genId: number, filename: string) => {
    setDownloadingId(genId);
    try {
      const blob = await api.get<Blob>(`/api/resume-generations/${genId}/download/`);
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename || 'resume.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err: unknown) {
      console.warn('Blob download failed, trying tokenized URL fallback...', err);
      const token = api.getAccessToken();
      const directUrl = `${api.getBaseUrl()}/api/resume-generations/${genId}/download/${token ? `?token=${token}` : ''}`;
      const fallbackLink = document.createElement('a');
      fallbackLink.href = directUrl;
      fallbackLink.download = filename || 'resume.pdf';
      document.body.appendChild(fallbackLink);
      fallbackLink.click();
      document.body.removeChild(fallbackLink);
    } finally {
      setDownloadingId(null);
    }
  };

  useEffect(() => {
    let ignore = false;
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      api.get<FinalizedResumeHistory[]>('/api/resume-history/')
        .then((data) => {
          if (!ignore) {
            setHistoryList(data);
          }
        })
        .catch((err) => {
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
  }, [user, authLoading, router]);

  const handleOpenMatchReport = async (item: FinalizedResumeHistory) => {
    try {
      const report = await api.get<ResumeMatchReport>(`/api/resume-history/${item.id}/match-report/`);
      setMatchReportItem({ resume: item, report });
    } catch {
      setMatchReportItem({ resume: item, report: item.match_report || null });
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <History className="w-7 h-7 text-indigo-400" />
            Resume Generation History
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Access every previously approved final resume, download PDFs, and inspect JD matching reports.
          </p>
        </div>

        <Link
          href="/generate"
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <Sparkles className="w-4 h-4" />
          Generate New Resume
        </Link>
      </div>

      {/* History Records Table/Cards */}
      {historyList.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {historyList.map((item) => (
            <div
              key={item.id}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-slate-700 transition-colors"
            >
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2.5">
                  <span className="text-base font-bold text-white">{item.target_role}</span>
                  {item.target_company && (
                    <span className="text-xs text-slate-400 font-medium">
                      at <strong className="text-slate-200">{item.target_company}</strong>
                    </span>
                  )}
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    Version {item.version_number} &bull; {item.page_format === 'ONE_PAGE' ? '1 Page' : '2 Pages'}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    {new Date(item.created_at).toLocaleDateString()} at {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span>&bull;</span>
                  <span>Experience: <strong className="text-slate-300">{item.experience_level}</strong></span>
                  <span>&bull;</span>
                  <span className="font-mono text-slate-400 text-[11px]">{item.filename}</span>
                </div>
              </div>

              {/* Metrics & Actions */}
              <div className="flex flex-wrap items-center gap-4 sm:gap-6">
                <div className="text-left md:text-right">
                  <div className="text-[11px] font-semibold uppercase text-slate-400">JD Coverage</div>
                  <div className="text-xl font-black text-emerald-400">{item.overall_evidence_score}%</div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewResume(item)}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5 text-indigo-400" />
                    View
                  </button>

                  <button
                    onClick={() => handleOpenMatchReport(item)}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
                  >
                    <Target className="w-3.5 h-3.5 text-cyan-400" />
                    Match Report
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDownloadPdf(item.generation, item.filename)}
                    disabled={downloadingId === item.generation}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 flex items-center gap-1.5 transition-all disabled:opacity-50"
                  >
                    {downloadingId === item.generation ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Download className="w-3.5 h-3.5" />
                    )}
                    Download PDF
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-16 text-center rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
            <History className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white">No Finalized Resumes in History</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Once you approve an optimized resume in the review workflow, the final PDF and JD match report will be archived here permanently.
          </p>
          <Link
            href="/generate"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/25 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            Generate Resume Now
          </Link>
        </div>
      )}

      {/* VIEW MODAL */}
      {viewResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">
                  {viewResume.target_role} &mdash; Final Approved Snapshot
                </h3>
                <p className="text-xs text-slate-400">{viewResume.filename}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleDownloadPdf(viewResume.generation, viewResume.filename)}
                  disabled={downloadingId === viewResume.generation}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 disabled:opacity-50"
                >
                  {downloadingId === viewResume.generation ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Download className="w-3.5 h-3.5" />
                  )}
                  Download
                </button>
                <button onClick={() => setViewResume(null)} className="text-slate-400 hover:text-white p-1">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <StructuredResumeView resume={viewResume.final_resume_data} />
          </div>
        </div>
      )}

      {/* MATCH REPORT MODAL */}
      {matchReportItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">
                  JD Match Report &bull; {matchReportItem.resume.target_role}
                </h3>
                <p className="text-xs text-slate-400">{matchReportItem.resume.target_company || 'Target Job'}</p>
              </div>
              <button onClick={() => setMatchReportItem(null)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <ScoreMeter report={matchReportItem.report || undefined} />
          </div>
        </div>
      )}
    </div>
  );
}
