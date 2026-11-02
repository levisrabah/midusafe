'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, Clock, FlaskConical, HelpCircle, MapPin, RefreshCw } from 'lucide-react';
import { SentinelIncident } from '@/types/sentinel';

const LANG_LABEL: Record<string, string> = {
  en: '🇬🇧 EN', sw: '🇰🇪 SW', sh: '🇰🇪 SH', luo: '🇰🇪 LUO', fr: '🇫🇷 FR', ar: '🇸🇦 AR',
};

function urgencyStyle(u: number) {
  if (u >= 8) return 'text-rose-400 border-rose-500/50';
  if (u >= 6) return 'text-yellow-400 border-yellow-500/50';
  return 'text-emerald-400 border-emerald-500/50';
}

function statusBadge(status: string) {
  if (status === 'verified') return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40';
  if (status === 'needs_info') return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
  return 'bg-zinc-500/15 text-zinc-300 border-zinc-500/40';
}

export default function SentinelFeed({
  incidents, selectedId, onSelect, loading, error, onRetry,
}: {
  incidents: SentinelIncident[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-zinc-200 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-emergency-red" />
            Sentinel Intel Feed
          </h2>
          <p className="text-xs text-zinc-500 mt-1">
            {incidents.length} incident{incidents.length === 1 ? '' : 's'} · Meta AI extracted
          </p>
        </div>
        <button onClick={onRetry} className="text-zinc-500 hover:text-zinc-200 transition-colors" title="Refresh">
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading && incidents.length === 0 && (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="glass-card rounded-lg p-4 animate-pulse">
                <div className="h-4 w-2/3 bg-zinc-700/50 rounded" />
                <div className="h-3 w-full bg-zinc-800/60 rounded mt-3" />
                <div className="h-3 w-1/2 bg-zinc-800/60 rounded mt-2" />
              </div>
            ))}
          </div>
        )}

        {error && incidents.length === 0 && !loading && (
          <div className="glass-card border border-rose-500/40 rounded-lg p-6 text-center">
            <AlertTriangle className="h-8 w-8 text-rose-400 mx-auto mb-2" />
            <p className="text-sm text-zinc-300">Could not load incidents</p>
            <p className="text-xs text-zinc-500 mt-1 break-words">{error}</p>
            <button onClick={onRetry} className="mt-3 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded-lg">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && incidents.length === 0 && (
          <div className="glass-card border border-zinc-800 rounded-lg p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-zinc-400 text-sm">No incidents yet</p>
            <p className="text-zinc-600 text-xs mt-1">Submit a report to see Meta AI extraction here</p>
          </div>
        )}

        {incidents.map((inc, index) => {
          const ex = inc.extraction;
          const resolved = Boolean(inc.location_resolved);
          return (
            <motion.div
              key={inc.id}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: Math.min(index * 0.05, 0.4) }}
              onClick={() => onSelect(inc.id)}
              className={`glass-card border rounded-lg p-4 cursor-pointer transition-all hover:border-zinc-600 ${
                selectedId === inc.id ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-zinc-800'
              }`}
            >
              <div className="flex items-start justify-between mb-2 gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-zinc-200 text-sm capitalize">
                    {inc.classification || ex.incident_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[11px] text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded">
                    {LANG_LABEL[ex.detected_language] || ex.detected_language.toUpperCase()}
                  </span>
                  {Boolean(inc.is_simulated) && (
                    <span className="text-[11px] text-violet-300 bg-violet-500/15 border border-violet-500/40 px-2 py-0.5 rounded flex items-center gap-1">
                      <FlaskConical className="h-3 w-3" /> SIMULATED
                    </span>
                  )}
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded-full border whitespace-nowrap ${urgencyStyle(inc.priority ?? ex.urgency)}`}>
                  {inc.priority ?? ex.urgency}/10
                </span>
              </div>

              <p className="text-sm text-zinc-300 mb-2 line-clamp-2">{ex.translated_summary}</p>

              <div className="flex items-center gap-2 flex-wrap text-xs">
                <span className={`px-2 py-0.5 rounded-full border ${statusBadge(inc.status)}`}>
                  {inc.status === 'needs_info' ? 'needs info' : inc.status}
                </span>
                {resolved ? (
                  <span className="text-zinc-500 flex items-center gap-1">
                    <MapPin className="h-3 w-3" /> {inc.resolved_place}
                  </span>
                ) : (
                  <span className="text-amber-300/90 flex items-center gap-1">
                    <HelpCircle className="h-3 w-3" /> Location unresolved
                    {ex.location_mentioned ? ` (“${ex.location_mentioned}”)` : ''}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1 text-[11px] text-zinc-600 mt-2">
                <Clock className="h-3 w-3" />
                {new Date(inc.created_at).toLocaleString()} · conf {(ex.confidence * 100).toFixed(0)}%
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
