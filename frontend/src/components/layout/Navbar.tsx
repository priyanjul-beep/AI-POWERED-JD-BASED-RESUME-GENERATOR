'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { 
  Sparkles, 
  LayoutDashboard, 
  FileText, 
  UserCircle, 
  History, 
  LogOut, 
  Menu, 
  X,
  FileCheck2
} from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  // Don't show navigation on login/register pages
  if (pathname === '/login' || pathname === '/register') {
    return null;
  }

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/generate', label: 'Generate Resume', icon: Sparkles, highlight: true },
    { href: '/profile', label: 'Career Profile', icon: UserCircle },
    { href: '/history', label: 'Resume History', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-slate-900/80 border-b border-slate-800 text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-cyan-400 p-[1px] shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
                <FileCheck2 className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                CareerForge<span className="text-indigo-400">.AI</span>
              </span>
              <span className="hidden sm:inline-block ml-2 text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                JD Tailored
              </span>
            </div>
          </Link>

          {/* Desktop Nav */}
          {user && (
            <nav className="hidden md:flex items-center gap-1.5">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = pathname === link.href || (link.href !== '/dashboard' && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-inner'
                        : link.highlight
                        ? 'bg-gradient-to-r from-indigo-500 to-violet-600 text-white shadow-md shadow-indigo-500/25 hover:opacity-95'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${link.highlight && !isActive ? 'text-white' : ''}`} />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </nav>
          )}

          {/* User menu / Auth */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
                <div className="flex flex-col text-right">
                  <span className="text-xs font-semibold text-slate-200">
                    {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
                  </span>
                  <span className="text-[11px] text-slate-400">{user.email}</span>
                </div>
                <button
                  onClick={logout}
                  title="Logout"
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-sm transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-950 border-b border-slate-800 px-4 pt-2 pb-6 space-y-2">
          {user ? (
            <>
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                      isActive
                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                        : 'text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
              <div className="pt-4 border-t border-slate-800 flex justify-between items-center">
                <div className="text-xs text-slate-400">
                  Logged in as <span className="font-semibold text-slate-200">{user.username}</span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 text-xs text-rose-400 hover:text-rose-300 font-medium"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Logout
                </button>
              </div>
            </>
          ) : (
            <div className="pt-2 flex flex-col gap-2">
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2 text-sm text-slate-200 font-medium hover:bg-slate-800 rounded-lg"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2 text-sm bg-indigo-600 text-white font-medium rounded-lg"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
