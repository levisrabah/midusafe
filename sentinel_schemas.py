"""Strict Pydantic contracts for MIDUSAFE Sentinel.

Design rule (anti-fabrication): the model NEVER outputs coordinates or
casualty counts. Coordinates are resolved server-side from a known-place
gazetteer; unknown locations stay null and are shown as unresolved.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

IncidentType = Literal[
    "flood", "flash_flood", "fire", "road_blockage", "building_damage",
    "structural_collapse", "medical", "displacement", "landslide", "storm",
    "drought", "disease_outbreak", "gas_leak", "industrial_accident", "other",
]

Severity = Literal["critical", "high", "moderate", "low", "minimal"]


class IncidentExtraction(BaseModel):
    """Validated Meta-model output for one report (no coordinates here)."""

    incident_type: IncidentType
    description: str = Field(min_length=1)
    original_report: str = Field(min_length=1)
    detected_language: str = Field(min_length=2, max_length=16)
    translated_summary: str = Field(min_length=1)
    location_mentioned: Optional[str] = None
    time_mentioned: Optional[str] = None
    severity: Severity
    urgency: int = Field(ge=1, le=10)
    people_affected: Optional[str] = None  # free text, ONLY if stated
    confidence: float = Field(ge=0.0, le=1.0)
    missing_information: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)


EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "incident_type": {
            "type": "string",
            "enum": ["flood", "flash_flood", "fire", "road_blockage",
                     "building_damage", "structural_collapse", "medical",
                     "displacement", "landslide", "storm", "drought",
                     "disease_outbreak", "gas_leak", "industrial_accident",
                     "other"],
        },
        "description": {"type": "string"},
        "original_report": {"type": "string"},
        "detected_language": {
            "type": "string",
            "description": "Language code such as en, sw, sh, luo, fr",
        },
        "translated_summary": {"type": "string"},
        "location_mentioned": {"type": ["string", "null"]},
        "time_mentioned": {"type": ["string", "null"]},
        "severity": {"type": "string",
                     "enum": ["critical", "high", "moderate", "low", "minimal"]},
        "urgency": {"type": "integer", "minimum": 1, "maximum": 10},
        "people_affected": {
            "type": ["string", "null"],
            "description": "ONLY if the report states it, else null. Never guess.",
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "follow_up_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["incident_type", "description", "original_report",
                 "detected_language", "translated_summary", "severity",
                 "urgency", "confidence", "missing_information",
                 "follow_up_questions"],
    "additionalProperties": False,
}

EXTRACTION_SYSTEM_PROMPT = """You extract structured incident data from community emergency reports.

STRICT RULES - violating any of these is a failure:
1. NEVER invent coordinates, casualty numbers, death tolls, or facts not stated in the report.
2. people_affected must be null unless the report explicitly states who/how many are affected.
3. location_mentioned: quote ONLY the place name as written in the report, or null if none is stated. Do not expand or guess locations.
4. detected_language: the language code of the report (en, sw, sh for Sheng, luo, etc.).
5. translated_summary: faithful English summary of what was reported, nothing added.
6. Missing/uncertain details go in missing_information. Questions a responder should ask go in follow_up_questions.
7. urgency is 1-10: 9-10 trapped/dying people or unfolding catastrophe, 7-8 serious threat or damage, 5-6 disruption needing response, 3-4 minor, 1-2 informational.
8. severity: critical/high/moderate/low/minimal - your assessment for HUMAN review, not a final verdict.
9. Do not give medical advice."""


class ReportIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    location_hint: Optional[str] = Field(default=None, max_length=200)
    is_simulated: bool = False
    voice_trace_id: Optional[str] = Field(default=None, max_length=64)


class IncidentOut(BaseModel):
    id: str
    report_id: str
    extraction: IncidentExtraction
    location_resolved: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolved_place: Optional[str] = None
    status: str = "pending"  # pending | verified | needs_info
    priority: Optional[int] = None  # responder override 1-10
    classification: Optional[str] = None  # responder override
    created_at: str
    is_simulated: bool = False


class BriefEvidence(BaseModel):
    claim: str
    source_report_ids: List[str]


class IntelligenceBrief(BaseModel):
    incident_id: str
    what_happened: str
    where: str
    when_reported: str
    evidence: List[BriefEvidence]
    unknowns: List[str]
    to_verify: List[str]
    next_steps: List[str]  # for HUMAN review; never auto-dispatched
    generated_at: str


BRIEF_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "what_happened": {"type": "string"},
        "where": {"type": "string"},
        "when_reported": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "source_report_ids": {"type": "array",
                                           "items": {"type": "string"}},
                },
                "required": ["claim", "source_report_ids"],
                "additionalProperties": False,
            },
        },
        "unknowns": {"type": "array", "items": {"type": "string"}},
        "to_verify": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["what_happened", "where", "when_reported", "evidence",
                 "unknowns", "to_verify", "next_steps"],
    "additionalProperties": False,
}

BRIEF_SYSTEM_PROMPT = """You write evidence-backed intelligence briefs for human emergency responders.

STRICT RULES:
1. Every claim in evidence MUST cite the source report id(s) it comes from, using ONLY ids from the provided reports. Never cite an id you were not given.
2. State what is unknown and what must be verified before acting. Never fill gaps with guesses.
3. next_steps are suggestions FOR HUMAN REVIEW ONLY. Never instruct autonomous dispatch.
4. No medical advice of any kind.
5. Keep each field concise."""


class DuplicateCandidate(BaseModel):
    incident_id: str
    other_incident_id: str
    score: float
    reasons: List[str]
    status: str = "pending"  # pending | confirmed | rejected


class AuditEntry(BaseModel):
    id: str
    timestamp: str
    actor: str = "responder"
    action: str
    target_type: str
    target_id: str
    detail: str = ""


class ContradictionClaim(BaseModel):
    """Two conflicting claims from two cited source reports."""

    topic: str
    claim_a: str
    report_id_a: str
    claim_b: str
    report_id_b: str


class ContradictionReport(BaseModel):
    incident_id: str
    contradictions: List[ContradictionClaim] = Field(default_factory=list)
    checked_at: str
    note: str = ""


CONTRADICTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "claim_a": {"type": "string"},
                    "report_id_a": {"type": "string"},
                    "claim_b": {"type": "string"},
                    "report_id_b": {"type": "string"},
                },
                "required": ["topic", "claim_a", "report_id_a",
                             "claim_b", "report_id_b"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["contradictions"],
    "additionalProperties": False,
}

CONTRADICTION_SYSTEM_PROMPT = """You compare emergency reports about the same incident cluster and flag CONFLICTING factual claims.

STRICT RULES:
1. Only flag genuine contradictions (e.g. one report says the footbridge is passable, another says it is impassable). Differences in detail or wording are NOT contradictions.
2. Each contradiction must cite the two source report ids it comes from, using ONLY ids from the provided reports. Never cite an id you were not given.
3. Quote each claim faithfully in a few words. If there are no contradictions, return an empty list.
4. Never invent facts, and never resolve the conflict yourself - a human verifies on the ground."""


class FollowupDraftText(BaseModel):
    """Validated Meta-model output: one short question in the given language."""

    draft_text: str = Field(min_length=1, max_length=500)
    language: str = Field(min_length=2, max_length=16)


FOLLOWUP_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "draft_text": {"type": "string"},
        "language": {"type": "string",
                     "description": "Language code of draft_text, e.g. en, sw, sh"},
    },
    "required": ["draft_text", "language"],
    "additionalProperties": False,
}

FOLLOWUP_SYSTEM_PROMPT = """You write ONE short follow-up question for an emergency reporter.

STRICT RULES:
1. Write in the requested language ONLY (same language the reporter used).
2. One question, under 30 words, asking for the single most important missing detail.
3. Be polite and direct. Never invent facts about the incident.
4. Return ONLY the question text and its language code."""
