'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { DashboardStats } from '@/lib/types';
import { 
  Sparkles, 
  FileCheck2, 
  Target, 
  PlusCircle, 
  Download, 
  Eye, 
  Calendar, 
  Briefcase, 
  ArrowUpRight,
  Loader2,
  FileText,
  UserCheck
} from 'lucide-react';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      api.get<DashboardStats>('/api/resume-history/stats/')
        .then((data) => {
          if (!ignore) {
            setStats(data);
          }
        })
        .catch(() => {
          if (!ignore) {
            setStats({
              total_resumes_generated: 0,
              average_jd_match_score: 0,
              recent_resumes: [],
            });
          }
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

  if (authLoading || loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/20 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-xs font-semibold border border-indigo-500/20">
              <Sparkles className="w-3.5 h-3.5" />
              AI Career Control Center
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.first_name || user?.username}!
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
              Ready to tailor a new role-specific resume? Our AI will synthesize your complete career history, reference resume, and JD requirements.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/profile"
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center gap-2 transition-all"
            >
              <UserCheck className="w-4 h-4 text-indigo-400" />
              Career Profile
            </Link>
            <Link
              href="/generate"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 flex items-center gap-2 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              New Resume
            </Link>
          </div>
        </div>
      </div>

      {/* Metric Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Resumes Finalized</p>
            <p className="text-3xl font-black text-white mt-1">{stats?.total_resumes_generated || 0}</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <FileCheck2 className="w-6 h-6" />
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Average JD Match Score</p>
            <p className="text-3xl font-black text-emerald-400 mt-1">{stats?.average_jd_match_score || 0}%</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Target className="w-6 h-6" />
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md shadow-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Career Profile DB</p>
            <p className="text-3xl font-black text-violet-400 mt-1">Active</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
            <Briefcase className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Recent Finalized Resumes */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">Recent Generated Resumes</h2>
          </div>
          <Link
            href="/history"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
          >
            View Complete History
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {stats?.recent_resumes && stats.recent_resumes.length > 0 ? (
          <div className="divide-y divide-slate-800">
            {stats.recent_resumes.map((resume) => (
              <div
                key={resume.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{resume.target_role}</span>
                    {resume.target_company && (
                      <span className="text-xs font-medium text-slate-400">
                        at <span className="text-slate-200">{resume.target_company}</span>
                      </span>
                    )}
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      v{resume.version_number} &bull; {resume.page_format === 'ONE_PAGE' ? '1 Page' : '2 Pages'}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {new Date(resume.created_at).toLocaleDateString()}
                    </span>
                    <span className="font-mono text-slate-500 text-[11px]">{resume.filename}</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Match Score</div>
                    <div className="text-sm font-black text-emerald-400">
                      {resume.overall_evidence_score}%
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <a
                      href={`${api.getBaseUrl()}/api/resume-generations/${resume.generation}/pdf/?token=${api.getAccessToken() || ''}`}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center gap-1.5 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5 text-indigo-400" />
                      View
                    </a>
                    <a
                      href={`${api.getBaseUrl()}/api/resume-generations/${resume.generation}/download/?token=${api.getAccessToken() || ''}`}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs font-medium text-indigo-300 flex items-center gap-1.5 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-white">No Resumes Generated Yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Your finalized, ATS-optimized resumes will appear here once you approve a generated draft.
            </p>
            <div className="pt-2">
              <Link
                href="/generate"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 transition-all"
              >
                <Sparkles className="w-4 h-4" />
                Generate First Resume
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
