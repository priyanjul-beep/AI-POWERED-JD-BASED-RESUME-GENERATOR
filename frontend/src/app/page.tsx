import React from 'react';
import Link from 'next/link';
import { 
  Sparkles, 
  ShieldCheck, 
  FileCheck2, 
  ArrowRight, 
  Layers, 
  Database, 
  Cpu, 
  CheckCircle2,
  FileCode2
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col justify-between">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 sm:pt-20 sm:pb-28">
        {/* Glow ambient background */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/20 via-violet-600/20 to-cyan-400/20 blur-[120px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            Next-Generation JD-Targeted Career Architecture
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
            Tailor Your Resume to Any Job Description{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-300 bg-clip-text text-transparent">
              Without Fabricating Lies
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            Harness your complete career database, transferable engineering experience, and reference resume. 
            Review every change with visual diffs, approve with Human-in-the-Loop control, and download ATS-compliant PDFs.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/generate"
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 flex items-center gap-2 group transition-all"
            >
              <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />
              Generate Targeted Resume
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              href="/dashboard"
              className="px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-200 font-semibold text-sm transition-all"
            >
              Open Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-slate-900">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-indigo-500/30 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <Database className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="text-base font-bold text-white">Complete Career Database</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Don't lose past projects or skills just because they didn't fit on your last 1-page resume. We maintain your comprehensive career history and surface relevant evidence for every specific role.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-amber-500/30 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-amber-400" />
            </div>
            <h3 className="text-base font-bold text-white">Human-in-the-Loop Review</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Never accept blind AI outputs. Inspect visual green/yellow/red diffs, provide revision feedback with YES/NO iteration, or safely cancel at any moment without finalizing.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-emerald-500/30 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <FileCheck2 className="w-5 h-5 text-emerald-400" />
            </div>
            <h3 className="text-base font-bold text-white">ATS-Compliant Backend PDF</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generate pixel-perfect 1-page or 2-page PDFs using ReportLab. Clean formatting, standardized fonts, normalized filenames, and zero overflow errors.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-900 text-center text-xs text-slate-500">
        AI-Powered JD-Based Resume Generator &copy; 2026. Built with Next.js, Django & Google Gemini.
      </footer>
    </div>
  );
}
