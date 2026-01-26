'use client';

import { Alert } from '@/types/alert';
import AiTriageCard from './ai-triage-card';
import { AnimatePresence } from 'framer-motion';

export default function LiveFeed({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="p-4 h-full overflow-y-auto">
      <h2 className="mb-4 text-lg font-semibold text-foreground">Live Alert Feed</h2>
      <AnimatePresence mode="popLayout">
        {alerts.map((alert) => (
          <AiTriageCard key={alert.id} alert={alert} />
        ))}
      </AnimatePresence>
      {alerts.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed border-zinc-700 glass-card">
          <p className="text-zinc-400">Awaiting new alerts...</p>
        </div>
      )}
    </div>
  );
}
