'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { sentinelApi } from '@/lib/sentinel-api';
import { DupLink, SentinelIncident, SentinelStats } from '@/types/sentinel';

export function useSentinel(pollMs = 5000) {
  const [incidents, setIncidents] = useState<SentinelIncident[]>([]);
  const [stats, setStats] = useState<SentinelStats | null>(null);
  const [duplicates, setDuplicates] = useState<DupLink[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [incs, st, dups] = await Promise.all([
        sentinelApi.listIncidents(),
        sentinelApi.stats(),
        sentinelApi.listDuplicates(),
      ]);
      setIncidents(incs);
      setStats(st);
      setDuplicates(dups);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to reach Sentinel API');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    timer.current = setInterval(refresh, pollMs);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [refresh, pollMs]);

  const selected = incidents.find((i) => i.id === selectedId) ?? null;

  return { incidents, stats, duplicates, selected, selectedId, setSelectedId, loading, error, refresh };
}
