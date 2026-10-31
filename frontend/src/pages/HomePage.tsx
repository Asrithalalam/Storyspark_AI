import React from 'react';
import { Sparkles, Wand2, Image as ImageIcon, History, Layers } from 'lucide-react';
import { useBackendHealth } from '../hooks/useBackendHealth';
import { ConnectionStatusBadge } from '../components/ConnectionStatusBadge';

export const HomePage: React.FC = () => {
  const { status, data, errorMessage, lastChecked, isChecking, refresh } =
    useBackendHealth();

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col items-center justify-center px-4 py-12 sm:px-6 text-center">
      {/* Sparkle Badge */}
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-4 py-1.5 text-xs font-medium text-indigo-300 backdrop-blur-sm">
        <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
        <span>Welcome to the Creative Canvas</span>
      </div>

      {/* Hero Title */}
      <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl text-white">
        StorySpark{' '}
        <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-indigo-200 bg-clip-text text-transparent">
          AI
        </span>
      </h1>

      {/* Tagline & Subheading */}
      <p className="mt-3 text-lg font-medium text-indigo-200/90 sm:text-xl">
        Where Ideas Become Stories
      </p>
      <p className="mt-3 max-w-2xl text-sm sm:text-base text-slate-300 leading-relaxed">
        Craft compelling narratives from text prompts, uploaded images, or a blend of both.
        Powered by modern intelligence, built with clarity, and saved to your personal library.
      </p>

      {/* Connection Status Card */}
      <div className="mt-10 w-full flex justify-center">
        <ConnectionStatusBadge
          status={status}
          data={data}
          errorMessage={errorMessage}
          lastChecked={lastChecked}
          isChecking={isChecking}
          onRetry={refresh}
        />
      </div>

      {/* Upcoming Capabilities Preview */}
      <div className="mt-14 w-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-left">
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 backdrop-blur-xs">
          <div className="h-8 w-8 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400 mb-2.5">
            <Wand2 className="h-4 w-4" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Text Storytelling</h4>
          <p className="text-[11px] text-slate-400 mt-1">Generate rich narratives tailored by genre, mood, and length.</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 backdrop-blur-xs">
          <div className="h-8 w-8 rounded-lg bg-purple-950 flex items-center justify-center text-purple-400 mb-2.5">
            <ImageIcon className="h-4 w-4" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Visual Inspiration</h4>
          <p className="text-[11px] text-slate-400 mt-1">Transform image uploads into immersive creative worlds.</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 backdrop-blur-xs">
          <div className="h-8 w-8 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400 mb-2.5">
            <History className="h-4 w-4" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Persistent History</h4>
          <p className="text-[11px] text-slate-400 mt-1">Revisit and manage past creations in your persistent shelf.</p>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-4 backdrop-blur-xs">
          <div className="h-8 w-8 rounded-lg bg-purple-950 flex items-center justify-center text-purple-400 mb-2.5">
            <Layers className="h-4 w-4" />
          </div>
          <h4 className="text-xs font-semibold text-slate-200">Reading Comfort</h4>
          <p className="text-[11px] text-slate-400 mt-1">Customize typography and export stories with ease.</p>
        </div>
      </div>
    </div>
  );
};
