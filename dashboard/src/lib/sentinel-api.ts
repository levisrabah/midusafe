const API_BASE =
  (typeof process !== 'undefined' && (process.env.NEXT_PUBLIC_API_URL as string)) ||
  'http://localhost:8000';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text.slice(0, 200) || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const sentinelApi = {
  listIncidents: () => req<import('@/types/sentinel').SentinelIncident[]>('/api/sentinel/incidents'),
  getIncident: (id: string) =>
    req<import('@/types/sentinel').SentinelIncident>(`/api/sentinel/incidents/${id}`),
  getBrief: (id: string, refresh = false) =>
    req<{ brief: import('@/types/sentinel').IntelBrief; method: string }>(
      `/api/sentinel/incidents/${id}/brief${refresh ? '?refresh=true' : ''}`
    ),
  getContradictions: (id: string, refresh = false) =>
    req<{ report: import('@/types/sentinel').ContradictionReport; method: string }>(
      `/api/sentinel/incidents/${id}/contradictions${refresh ? '?refresh=true' : ''}`
    ),
  draftFollowup: (id: string) =>
    req<{ draft: import('@/types/sentinel').FollowupDraft | null; method: string; note: string }>(
      `/api/sentinel/incidents/${id}/followups`, { method: 'POST' }
    ),
  listFollowups: (id: string) =>
    req<import('@/types/sentinel').FollowupDraft[]>(`/api/sentinel/incidents/${id}/followups`),
  decideFollowup: (draftId: string, decision: 'approved' | 'discarded', edited_text?: string) =>
    req<{ draft: import('@/types/sentinel').FollowupDraft; status: string }>(
      `/api/sentinel/followups/${draftId}/decision`,
      { method: 'POST', body: JSON.stringify({ decision, edited_text }) }
    ),
  listDuplicates: (status?: string) =>
    req<import('@/types/sentinel').DupLink[]>(
      `/api/sentinel/duplicates${status ? `?status=${status}` : ''}`
    ),
  decideDuplicate: (linkId: string, decision: 'confirmed' | 'rejected') =>
    req<{ status: string; id: string }>(`/api/sentinel/duplicates/${linkId}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision }),
    }),
  verify: (id: string, action: string, value?: string) =>
    req<{ status: string; action: string; incident: import('@/types/sentinel').SentinelIncident }>(
      `/api/sentinel/incidents/${id}/verify`,
      { method: 'POST', body: JSON.stringify({ action, value }) }
    ),
  stats: () => req<import('@/types/sentinel').SentinelStats>('/api/sentinel/stats'),
  audit: () => req<import('@/types/sentinel').AuditEntry[]>('/api/sentinel/audit'),
  submitReport: (message: string, location_hint?: string) =>
    req<{ status: string; incident?: import('@/types/sentinel').SentinelIncident }>(
      '/api/sentinel/reports',
      { method: 'POST', body: JSON.stringify({ message, location_hint, is_simulated: false }) }
    ),
};
