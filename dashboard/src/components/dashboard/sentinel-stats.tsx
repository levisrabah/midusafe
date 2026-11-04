'use client';

import { AlertTriangle, CheckCircle2, Clock, Copy, Flame } from 'lucide-react';
import { SentinelStats } from '@/types/sentinel';

function Card({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: number | string; accent: string }) {
  return (
    <div className="glass-card rounded-lg px-4 py-3 flex items-center gap-3 min-w-0">
      <div className={`p-2 rounded-lg border ${accent}`}>{icon}</div>
      <div className="min-w-0">
        <div className="text-2xl font-bold text-zinc-100 leading-none">{value}</div>
        <div className="text-xs text-zinc-500 mt-1 truncate">{label}</div>
      </div>
    </div>
  );
}

export default function SentinelStatsBar({ stats }: { stats: SentinelStats | null }) {
  if (!stats) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="glass-card rounded-lg px-4 py-3 animate-pulse">
            <div className="h-7 w-10 bg-zinc-700/50 rounded" />
            <div className="h-3 w-20 bg-zinc-800/60 rounded mt-2" />
          </div>
        ))}
      </div>
    );
  }
  const topCats = Object.entries(stats.by_category).sort((a, b) => b[1] - a[1]).slice(0, 3);
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      <Card icon={<Flame className="h-4 w-4" />} label="Total" value={stats.total} accent="text-sky-400 border-sky-500/50" />
      <Card icon={<Clock className="h-4 w-4" />} label="Awaiting" value={stats.pending_verification} accent="text-yellow-400 border-yellow-500/50" />
      <Card icon={<AlertTriangle className="h-4 w-4" />} label="High prio" value={stats.high_priority} accent="text-rose-400 border-rose-500/50" />
      <Card icon={<Copy className="h-4 w-4" />} label="Duplicates" value={stats.possible_duplicates} accent="text-violet-400 border-violet-500/50" />
      <div className="glass-card rounded-lg px-4 py-3 min-w-0">
        <div className="flex items-center gap-2 text-emerald-400">
          <CheckCircle2 className="h-4 w-4" />
          <span className="text-2xl font-bold text-zinc-100 leading-none">{stats.verified}</span>
        </div>
        <div className="text-xs text-zinc-500 mt-1 truncate">
          Verified{topCats.length > 0 && ` · ${topCats.map(([k, v]) => `${k} ${v}`).join(' · ')}`}
        </div>
      </div>
    </div>
  );
}
