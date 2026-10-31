import React from 'react';
import { Activity, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';
import type { ConnectionStatus, HealthResponse } from '../types';

interface ConnectionStatusBadgeProps {
  status: ConnectionStatus;
  data: HealthResponse | null;
  errorMessage: string | null;
  lastChecked: Date | null;
  isChecking: boolean;
  onRetry: () => void;
}

export const ConnectionStatusBadge: React.FC<ConnectionStatusBadgeProps> = ({
  status,
  data,
  errorMessage,
  lastChecked,
  isChecking,
  onRetry,
}) => {
  return (
    <div className="w-full max-w-lg rounded-2xl border border-indigo-900/40 bg-slate-900/80 p-5 shadow-xl backdrop-blur-md transition-all">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-950/80 border border-indigo-800/50 text-indigo-400">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Backend API Status</h3>
            <p className="text-xs text-slate-400">FastAPI Service Connection</p>
          </div>
        </div>

        <button
          onClick={onRetry}
          disabled={isChecking}
          className="flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-800/60 px-3 py-1.5 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-800 hover:text-white disabled:opacity-50 cursor-pointer"
          title="Re-check connection"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isChecking ? 'animate-spin text-indigo-400' : ''}`} />
          <span>{isChecking ? 'Checking...' : 'Check'}</span>
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-800/80">
        {status === 'checking' && (
          <div className="flex items-center gap-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 px-3.5 py-2.5 text-xs font-medium text-amber-300">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-amber-500"></span>
            </span>
            <span>Checking connection to backend server...</span>
          </div>
        )}

        {status === 'connected' && (
          <div className="space-y-2">
            <div className="flex items-center gap-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-2.5 text-xs font-medium text-emerald-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              <div className="flex-1">
                <span className="font-semibold">Connected</span>
                <span className="mx-1.5 opacity-50">•</span>
                <span>{data?.message || 'Backend is running smoothly.'}</span>
              </div>
            </div>

            {data?.timestamp && (
              <div className="flex items-center justify-between px-1 text-[11px] text-slate-400">
                <span>Endpoint: <code className="text-indigo-300 font-mono">GET /api/health</code></span>
                <span>Server time (UTC): <time className="font-mono text-slate-300">{new Date(data.timestamp).toLocaleTimeString()}</time></span>
              </div>
            )}
          </div>
        )}

        {status === 'disconnected' && (
          <div className="space-y-2">
            <div className="flex items-start gap-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 px-3.5 py-2.5 text-xs text-rose-300">
              <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="font-semibold text-rose-200">Disconnected</div>
                <div className="mt-0.5 text-slate-300">
                  {errorMessage || 'Cannot reach the backend server.'}
                </div>
              </div>
            </div>

            <p className="px-1 text-[11px] text-slate-400">
              Make sure the FastAPI server is running on <code className="text-indigo-300 font-mono">http://localhost:8000</code>.
            </p>
          </div>
        )}

        {lastChecked && (
          <div className="mt-2.5 text-right text-[10px] text-slate-400">
            Last verified: {lastChecked.toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
};
