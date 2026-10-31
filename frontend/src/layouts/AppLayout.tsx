import React from 'react';
import { Sparkles, BookOpen } from 'lucide-react';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="relative flex min-h-screen flex-col bg-slate-950 text-slate-100 overflow-x-hidden">
      {/* Background ambient gradient glow */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-indigo-600/15 blur-3xl" />
        <div className="absolute top-1/4 right-0 h-96 w-96 rounded-full bg-purple-600/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-indigo-900/10 blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-indigo-950/60 bg-slate-950/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5 sm:px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 shadow-lg shadow-indigo-500/20 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
                StorySpark AI
              </span>
              <span className="ml-2.5 hidden text-xs font-normal text-slate-400 sm:inline-block">
                Where Ideas Become Stories
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-900/50 bg-indigo-950/40 px-3 py-1 text-xs font-medium text-indigo-300">
              <BookOpen className="h-3.5 w-3.5 text-indigo-400" />
              <span>Phase 2 Active</span>
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex flex-col">{children}</main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-900 bg-slate-950/60 py-4 text-center text-xs text-slate-400">
        <p>StorySpark AI • Next-Generation Creative Storytelling Platform</p>
      </footer>
    </div>
  );
};
