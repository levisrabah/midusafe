'use client';

import { Alert } from '@/types/alert';
import AiTriageCard from './ai-triage-card';
import { AnimatePresence } from 'framer-motion';

export default function LiveFeed({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="p-4">
      <h2 className="mb-4 text-lg font-semibold">Live Alert Feed</h2>
      <AnimatePresence>
        {alerts.map((alert) => (
          <AiTriageCard key={alert.id} alert={alert} />
        ))}
      </AnimatePresence>
      {alerts.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed border-white/10">
          <p className="text-muted-foreground">Awaiting new alerts...</p>
        </div>
      )}
    </div>
  );
}
