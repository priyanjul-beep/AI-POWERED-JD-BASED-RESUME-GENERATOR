import React, { Suspense } from 'react';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/lib/auth';
import Navbar from '@/components/layout/Navbar';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'CareerForge AI | JD-Based Role-Specific Resume Generator',
  description: 'AI-powered resume optimization engine tailoring candidate complete career experience to specific job descriptions with ATS scoring and Human-in-the-Loop validation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200`}>
        <AuthProvider>
          <Suspense fallback={<div className="h-16 bg-slate-950 border-b border-slate-800" />}>
            <Navbar />
          </Suspense>
          <main className="min-h-[calc(100vh-4rem)] flex flex-col">
            <Suspense fallback={<div className="flex-1 flex items-center justify-center"><div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" /></div>}>
              {children}
            </Suspense>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
