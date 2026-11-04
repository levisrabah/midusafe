'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Brain, Check, Copy, FileText, History, MapPin, ShieldCheck, X } from 'lucide-react';
import { sentinelApi } from '@/lib/sentinel-api';
import { AuditEntry, ContradictionReport, DupLink, IntelBrief, SentinelIncident } from '@/types/sentinel';

export default function IncidentDetail({
  incident, duplicates, onClose, onChanged,
}: {
  incident: SentinelIncident;
  duplicates: DupLink[];
  onClose: () => void;
  onChanged: () => void;
}) {
  const [brief, setBrief] = useState<IntelBrief | null>(null);
  const [briefMethod, setBriefMethod] = useState<string>('');
  const [briefLoading, setBriefLoading] = useState(false);
  const [contra, setContra] = useState<ContradictionReport | null>(null);
  const [contraMethod, setContraMethod] = useState<string>('');
  const [contraLoading, setContraLoading] = useState(false);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [note, setNote] = useState('');
  const [priority, setPriority] = useState('8');
  const [reclass, setReclass] = useState(incident.extraction.incident_type);

  const ex = incident.extraction;
  const myDups = duplicates.filter(
    (d) => d.incident_a === incident.id || d.incident_b === incident.id
  );

  useEffect(() => {
    setBrief(null);
    setBriefMethod('');
    setContra(null);
    setContraMethod('');
    setNote('');
    setReclass(incident.extraction.incident_type);
    sentinelApi.audit().then((a) =>
      setAudit(a.filter((e) => e.target_id === incident.id || e.target_id === incident.report_id))
    ).catch(() => setAudit([]));
  }, [incident.id, incident.report_id, incident.extraction.incident_type]);

  const loadBrief = async (refresh = false) => {
    setBriefLoading(true);
    try {
      const res = await sentinelApi.getBrief(incident.id, refresh);
      setBrief(res.brief);
      setBriefMethod(res.method);
    } catch {
      setBrief(null);
    } finally {
      setBriefLoading(false);
    }
  };

  const loadContra = async (refresh = false) => {
    setContraLoading(true);
    try {
      const res = await sentinelApi.getContradictions(incident.id, refresh);
      setContra(res.report);
      setContraMethod(res.method);
    } catch {
      setContra(null);
    } finally {
      setContraLoading(false);
    }
  };

  const act = async (action: string, value?: string) => {
    setBusy(action);
    try {
      await sentinelApi.verify(incident.id, action, value);
      setNote('');
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const decideDup = async (linkId: string, decision: 'confirmed' | 'rejected') => {
    setBusy(linkId);
    try {
      await sentinelApi.decideDuplicate(linkId, decision);
      onChanged();
    } finally {
      setBusy(null);
    }
  };

  const otherId = (d: DupLink) => (d.incident_a === incident.id ? d.incident_b : d.incident_a);

  return (
    <motion.div
      initial={{ x: 60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="absolute inset-y-0 right-0 w-full md:w-[420px] z-[80] glass-sidebar border-l border-zinc-700 flex flex-col"
    >
      <div className="p-4 border-b border-zinc-800 flex items-start justify-between gap-2">
        <div>
          <h3 className="font-bold text-zinc-100 capitalize flex items-center gap-2">
            {(incident.classification || ex.incident_type).replace(/_/g, ' ')}
            {Boolean(incident.is_simulated) && (
              <span className="text-[10px] text-violet-300 bg-violet-500/15 border border-violet-500/40 px-2 py-0.5 rounded font-medium">
                SIMULATED
              </span>
            )}
          </h3>
          <p className="text-xs text-zinc-500 mt-1 font-mono">{incident.id} · {incident.status}</p>
        </div>
        <button onClick={onClose} className="text-zinc-500 hover:text-zinc-200"><X className="h-5 w-5" /></button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Summary + original */}
        <section className="glass-card rounded-lg p-3">
          <p className="text-sm text-zinc-200">{ex.translated_summary}</p>
          <div className="mt-2 bg-zinc-900/60 rounded p-2">
            <p className="text-[11px] text-zinc-500 mb-1">Original report [{ex.detected_language}]:</p>
            <p className="text-xs text-zinc-400 italic">“{ex.original_report}”</p>
          </div>
          <div className="grid grid-cols-3 gap-2 mt-2 text-center">
            <div className="bg-zinc-900/60 rounded p-2">
              <div className="text-[10px] text-zinc-500">URGENCY</div>
              <div className="font-bold text-zinc-100">{incident.priority ?? ex.urgency}/10</div>
            </div>
            <div className="bg-zinc-900/60 rounded p-2">
              <div className="text-[10px] text-zinc-500">SEVERITY</div>
              <div className="font-bold text-zinc-100 capitalize">{ex.severity}</div>
            </div>
            <div className="bg-zinc-900/60 rounded p-2">
              <div className="text-[10px] text-zinc-500">CONFIDENCE</div>
              <div className="font-bold text-zinc-100">{(ex.confidence * 100).toFixed(0)}%</div>
            </div>
          </div>
        </section>

        {/* Location */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <MapPin className="h-3 w-3" /> LOCATION
          </h4>
          {incident.location_resolved ? (
            <p className="text-sm text-emerald-300">📍 {incident.resolved_place}</p>
          ) : (
            <p className="text-sm text-amber-300">⚠ Unresolved — mentioned: “{ex.location_mentioned || 'none stated'}”. Not shown on map.</p>
          )}
          {ex.people_affected && <p className="text-xs text-zinc-400 mt-1">People affected (as stated): {ex.people_affected}</p>}
          {!ex.people_affected && <p className="text-xs text-zinc-600 mt-1">Casualty count not stated — not estimated.</p>}
        </section>

        {/* Duplicates */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <Copy className="h-3 w-3" /> POSSIBLE DUPLICATES ({myDups.filter((d) => d.status === 'pending').length} pending)
          </h4>
          {myDups.length === 0 && <p className="text-xs text-zinc-600">No related reports detected.</p>}
          {myDups.map((d) => (
            <div key={d.id} className="bg-zinc-900/60 rounded p-2 mb-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-zinc-400">{otherId(d).slice(0, 12)}…</span>
                <span className="text-xs text-violet-300">{(d.score * 100).toFixed(0)}% · {d.status}</span>
              </div>
              <ul className="mt-1 space-y-0.5">
                {d.reasons.map((r, i) => (
                  <li key={i} className="text-xs text-zinc-400">• {r}</li>
                ))}
              </ul>
              {d.status === 'pending' && (
                <div className="flex gap-2 mt-2">
                  <button disabled={busy === d.id} onClick={() => decideDup(d.id, 'confirmed')}
                    className="flex-1 text-xs py-1.5 bg-emerald-600/80 hover:bg-emerald-600 disabled:opacity-50 text-white rounded flex items-center justify-center gap-1">
                    <Check className="h-3 w-3" /> Same incident
                  </button>
                  <button disabled={busy === d.id} onClick={() => decideDup(d.id, 'rejected')}
                    className="flex-1 text-xs py-1.5 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-50 text-white rounded">
                    Not related
                  </button>
                </div>
              )}
            </div>
          ))}
        </section>

        {/* Conflicting reports */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" /> CONFLICTING REPORTS {contraMethod && <span className="text-zinc-600">({contraMethod})</span>}
          </h4>
          {!contra && (
            <button onClick={() => loadContra()} disabled={contraLoading}
              className="w-full text-sm py-2 bg-amber-600/80 hover:bg-amber-600 disabled:opacity-50 text-white rounded-lg flex items-center justify-center gap-2">
              {contraLoading ? 'Checking…' : 'Check for conflicts'}
            </button>
          )}
          {contra && contra.contradictions.length === 0 && (
            <p className="text-xs text-zinc-500">{contra.note || 'No conflicts found between reports.'}</p>
          )}
          {contra && contra.contradictions.map((c, i) => (
            <div key={i} className="bg-zinc-900/60 rounded p-2 mb-2">
              <p className="text-xs font-semibold text-amber-300 capitalize">{c.topic}</p>
              <p className="text-xs text-zinc-300 mt-1">“{c.claim_a}” <span className="text-zinc-500 font-mono">[{c.report_id_a.slice(0, 10)}]</span></p>
              <p className="text-[11px] text-zinc-600 my-0.5">conflicts with</p>
              <p className="text-xs text-zinc-300">“{c.claim_b}” <span className="text-zinc-500 font-mono">[{c.report_id_b.slice(0, 10)}]</span></p>
              <p className="text-[11px] text-amber-300/80 mt-1">⚠ Verify on the ground before acting.</p>
            </div>
          ))}
          {contra && (
            <button onClick={() => loadContra(true)} disabled={contraLoading} className="text-zinc-500 hover:text-zinc-300 text-xs">
              Re-check
            </button>
          )}
        </section>

        {/* Brief */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <Brain className="h-3 w-3" /> INTEL BRIEF {briefMethod && <span className="text-zinc-600">({briefMethod})</span>}
          </h4>
          {!brief && (
            <button onClick={() => loadBrief()} disabled={briefLoading}
              className="w-full text-sm py-2 bg-violet-600/80 hover:bg-violet-600 disabled:opacity-50 text-white rounded-lg flex items-center justify-center gap-2">
              <FileText className="h-4 w-4" /> {briefLoading ? 'Generating…' : 'Generate brief'}
            </button>
          )}
          {brief && (
            <div className="space-y-2 text-xs text-zinc-300">
              <p><span className="text-zinc-500 font-semibold">What: </span>{brief.what_happened}</p>
              <p><span className="text-zinc-500 font-semibold">Where: </span>{brief.where}</p>
              <div>
                <p className="text-zinc-500 font-semibold">Evidence:</p>
                {brief.evidence.map((e, i) => (
                  <p key={i} className="mt-1">• {e.claim} <span className="text-zinc-500">[{e.source_report_ids.map((s) => s.slice(0, 10)).join(', ')}]</span></p>
                ))}
              </div>
              <p><span className="text-zinc-500 font-semibold">Unknown: </span>{brief.unknowns.join('; ')}</p>
              <p><span className="text-zinc-500 font-semibold">Verify: </span>{brief.to_verify.join('; ')}</p>
              <p><span className="text-zinc-500 font-semibold">Next (human review): </span>{brief.next_steps.join('; ')}</p>
              <button onClick={() => loadBrief(true)} disabled={briefLoading} className="text-zinc-500 hover:text-zinc-300 text-xs">
                Regenerate
              </button>
            </div>
          )}
        </section>

        {/* Verification */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <ShieldCheck className="h-3 w-3" /> RESPONDER ACTIONS
          </h4>
          <div className="flex gap-2 mb-2">
            <button disabled={busy !== null} onClick={() => act('verify')}
              className="flex-1 text-xs py-2 bg-growth-green hover:brightness-110 disabled:opacity-50 text-white rounded-lg">Mark verified</button>
            <button disabled={busy !== null} onClick={() => act('request_info')}
              className="flex-1 text-xs py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-lg">Request info</button>
          </div>
          <div className="flex gap-2 mb-2">
            <select value={reclass} onChange={(e) => setReclass(e.target.value)}
              className="flex-1 text-xs bg-zinc-900 border border-zinc-700 rounded-lg px-2 py-2 text-zinc-200">
              {['flood', 'flash_flood', 'fire', 'road_blockage', 'building_damage', 'structural_collapse', 'medical', 'displacement', 'landslide', 'storm', 'other'].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <button disabled={busy !== null} onClick={() => act('reclassify', reclass)}
              className="text-xs px-3 py-2 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-50 text-white rounded-lg">Reclassify</button>
          </div>
          <div className="flex gap-2 mb-2">
            <select value={priority} onChange={(e) => setPriority(e.target.value)}
              className="flex-1 text-xs bg-zinc-900 border border-zinc-700 rounded-lg px-2 py-2 text-zinc-200">
              {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                <option key={n} value={n}>Priority {n}</option>
              ))}
            </select>
            <button disabled={busy !== null} onClick={() => act('priority', priority)}
              className="text-xs px-3 py-2 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-50 text-white rounded-lg">Set priority</button>
          </div>
          <div className="flex gap-2">
            <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Add responder note…"
              className="flex-1 text-xs bg-zinc-900 border border-zinc-700 rounded-lg px-2 py-2 text-zinc-200 placeholder-zinc-600" />
            <button disabled={busy !== null || !note.trim()} onClick={() => act('note', note)}
              className="text-xs px-3 py-2 bg-zinc-700 hover:bg-zinc-600 disabled:opacity-50 text-white rounded-lg">Add</button>
          </div>
          <p className="text-[11px] text-zinc-600 mt-2">All actions are audit-logged. Nothing is auto-dispatched.</p>
        </section>

        {/* Missing info / follow-ups */}
        <section className="glass-card rounded-lg p-3 text-xs text-zinc-400">
          <p className="text-zinc-500 font-semibold mb-1">MISSING INFO</p>
          <p>{ex.missing_information.join('; ') || '—'}</p>
          <p className="text-zinc-500 font-semibold mt-2 mb-1">FOLLOW-UP QUESTIONS</p>
          <p>{ex.follow_up_questions.join(' ') || '—'}</p>
        </section>

        {/* Audit */}
        <section className="glass-card rounded-lg p-3">
          <h4 className="text-xs font-semibold text-zinc-400 mb-2 flex items-center gap-1">
            <History className="h-3 w-3" /> AUDIT TRAIL
          </h4>
          {audit.length === 0 && <p className="text-xs text-zinc-600">No actions recorded yet.</p>}
          {audit.map((a) => (
            <p key={a.id} className="text-xs text-zinc-500 font-mono">
              {a.timestamp.slice(0, 19).replace('T', ' ')} · {a.action} · {a.detail.slice(0, 60)}
            </p>
          ))}
        </section>
      </div>
    </motion.div>
  );
}
