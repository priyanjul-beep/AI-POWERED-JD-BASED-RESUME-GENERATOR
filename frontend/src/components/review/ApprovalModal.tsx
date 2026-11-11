'use client';

import React, { useState } from 'react';
import { FileText, CheckCircle2, X, Sparkles, Loader2 } from 'lucide-react';

interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (pageFormat: 'ONE_PAGE' | 'TWO_PAGE', customFilename: string, comment: string) => Promise<void>;
  defaultFilename: string;
}

export default function ApprovalModal({
  isOpen,
  onClose,
  onConfirm,
  defaultFilename,
}: ApprovalModalProps) {
  const [pageFormat, setPageFormat] = useState<'ONE_PAGE' | 'TWO_PAGE'>('ONE_PAGE');
  const [filename, setFilename] = useState(defaultFilename);
  const [prevDefaultFilename, setPrevDefaultFilename] = useState(defaultFilename);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (prevDefaultFilename !== defaultFilename) {
    setPrevDefaultFilename(defaultFilename);
    setFilename(defaultFilename);
  }

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onConfirm(pageFormat, filename, comment);
      onClose();
    } catch {
      // Handled by parent toast/error
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Approve & Generate PDF</h3>
              <p className="text-xs text-slate-400">Configure page budget and download filename</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Page Format Selection */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Resume Page Format</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setPageFormat('ONE_PAGE')}
                className={`p-3.5 rounded-xl border text-left flex flex-col justify-between transition-all ${
                  pageFormat === 'ONE_PAGE'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="text-sm font-bold">One-Page Resume</span>
                  <FileText className="w-4 h-4 text-indigo-400" />
                </div>
                <span className="text-[11px] text-slate-400">
                  Tight ATS spacing. Ideal for 0-3 years experience or standard applications.
                </span>
              </button>

              <button
                type="button"
                onClick={() => setPageFormat('TWO_PAGE')}
                className={`p-3.5 rounded-xl border text-left flex flex-col justify-between transition-all ${
                  pageFormat === 'TWO_PAGE'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="text-sm font-bold">Two-Page Resume</span>
                  <FileText className="w-4 h-4 text-violet-400" />
                </div>
                <span className="text-[11px] text-slate-400">
                  Expanded technical depth, full project highlights, and detailed achievements.
                </span>
              </button>
            </div>
          </div>

          {/* Download Filename */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Download Filename
            </label>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              required
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="candidate_company_role_version.pdf"
            />
            <p className="text-[10px] text-slate-500">
              Normalized format: candidate_name_company_name_target_role_version_number.pdf
            </p>
          </div>

          {/* Optional final comment */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">
              Final Instructions / Comment (Optional)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={2}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="Any last minute tweaks before generating the final PDF? (e.g. 'Make sure phone number is formatted nicely')"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
            >
              Back to Review
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating ATS PDF...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Finalize & Generate PDF
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
