export interface Extraction {
  incident_type: string;
  description: string;
  original_report: string;
  detected_language: string;
  translated_summary: string;
  location_mentioned: string | null;
  time_mentioned: string | null;
  severity: string;
  urgency: number;
  people_affected: string | null;
  confidence: number;
  missing_information: string[];
  follow_up_questions: string[];
}

export interface SentinelIncident {
  id: string;
  report_id: string;
  extraction: Extraction;
  location_resolved: number | boolean;
  latitude: number | null;
  longitude: number | null;
  resolved_place: string | null;
  status: string;
  priority: number | null;
  classification: string | null;
  created_at: string;
  is_simulated: number | boolean;
}

export interface BriefEvidence {
  claim: string;
  source_report_ids: string[];
}

export interface IntelBrief {
  incident_id: string;
  what_happened: string;
  where: string;
  when_reported: string;
  evidence: BriefEvidence[];
  unknowns: string[];
  to_verify: string[];
  next_steps: string[];
  generated_at: string;
}

export interface DupLink {
  id: string;
  incident_a: string;
  incident_b: string;
  score: number;
  reasons: string[];
  status: string;
  created_at: string;
  decided_at: string | null;
}

export interface SentinelStats {
  total: number;
  pending_verification: number;
  verified: number;
  high_priority: number;
  possible_duplicates: number;
  by_category: Record<string, number>;
}

export interface ContradictionClaim {
  topic: string;
  claim_a: string;
  report_id_a: string;
  claim_b: string;
  report_id_b: string;
}

export interface ContradictionReport {
  incident_id: string;
  contradictions: ContradictionClaim[];
  checked_at: string;
  note: string;
}

export interface FollowupDraft {
  id: string;
  incident_id: string;
  language: string;
  draft_text: string;
  status: string;
  created_at: string;
  decided_at: string | null;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: string;
}
