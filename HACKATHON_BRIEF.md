# MASTER ENGINEERING BRIEF: BUILD MIDUSAFE SENTINEL
## Meta Global AI Developer Hackathon 2026

You are acting as the lead software architect, senior full-stack engineer, AI engineer, UI/UX designer, and QA engineer for this project.

Your mission is to transform my existing MIDUSAFE project into a polished, functional, impressive AI-powered disaster intelligence and emergency response platform called:

# MIDUSAFE SENTINEL
### Turning community reports into actionable disaster intelligence.

This is a serious hackathon project for the Meta Global AI Developer Hackathon 2026.

Do not simply give me a plan, tutorial, mockup, or code snippets. Inspect the existing repository, understand its architecture, and IMPLEMENT the project directly in the codebase.

You must make real code changes, integrate Meta AI models, run the application, test the functionality, and fix errors wherever possible.

---

# 1. HACKATHON REQUIREMENTS — NON-NEGOTIABLE

The project must satisfy the official hackathon problem statements:

**Build for Your World:** Bring Meta's models into a real problem domain and solve a meaningful challenge.

**Push the Frontier:** Use Meta's models to unlock capabilities beyond a basic AI integration.

The project must genuinely incorporate Meta models through the Meta Model API or eligible Meta open-weight models.

The judging rubric is:

- Impact: 30%
- Use of Meta AI Tooling: 25%
- Technical Depth & Execution: 20%
- Demo: 25%

The hackathon requires:
- A public GitHub repository.
- Clear identification of features newly built during the hackathon.
- A working project.
- A three-minute demo video.
- A genuine, meaningful use of Meta models.

IMPORTANT: The existing MIDUSAFE application is our starting codebase. Do not misrepresent existing functionality as new hackathon work. Clearly document what existed before and what you implement now.

---

# 2. THE PROBLEM WE ARE SOLVING

During disasters, critical information arrives from fragmented sources:

- People sending emergency messages.
- Community WhatsApp-style reports.
- Voice recordings.
- Reports in different languages.
- Incomplete descriptions of incidents.
- Conflicting reports about the same incident.
- Unclear locations.
- Duplicate emergency alerts.

Emergency responders need to understand what is happening, where it is happening, how urgent it is, and what information is still uncertain.

MIDUSAFE SENTINEL should turn these fragmented reports into structured, traceable disaster intelligence.

The system must help human responders make better-informed decisions.

It must NOT autonomously dispatch emergency services or invent facts.

---

# 3. EXISTING TECHNOLOGY STACK

First inspect the repository and identify the existing implementation.

The existing project includes:

Frontend:
- Next.js 14+
- React
- Tailwind CSS
- shadcn/ui
- Framer Motion
- Mapbox GL

Backend:
- Python
- FastAPI
- WebSockets

AI:
- Existing Gemini integration.
- Existing simulated incident data.
- Existing multilingual incident triage functionality.

Other existing features include:
- Incident dashboard.
- Map interface.
- Browser-based voice recording.
- Mock emergency reports.

Do not unnecessarily replace working infrastructure.

Reuse existing components and architecture wherever sensible.

If the actual repository differs from this description, trust the repository and adapt accordingly.

---

# 4. THE CORE PRODUCT

Build a real-time disaster intelligence command center.

The central workflow:

1. A community member submits an emergency report.
2. The report may contain text, a voice recording, or an image if supported.
3. Meta AI interprets the available information.
4. The system extracts structured incident information.
5. The backend validates the result.
6. The system resolves the location where possible.
7. Similar reports are identified as potential duplicates.
8. Responders inspect the incident and its original evidence.
9. The system generates a concise response intelligence brief.
10. A human responder reviews and approves any consequential action.

Make the entire workflow visually understandable.

---

# 5. META AI INTEGRATION — THE HEART OF THE PROJECT

This must be a genuine Meta-powered application.

Inspect the official Meta Model API documentation and the actual models enabled for my account before implementing the integration.

Prioritize available models from the Muse Spark series, Muse Wonder, Muse Image, Muse Voice Transcribe, and SAM 3.1 where they genuinely improve the product.

Do not assume every model or capability is available.

Do not invent model identifiers, endpoints, API parameters, or features.

Use the documented API interface and verify that requests work.

Implement a dedicated backend Meta AI service.

All API keys must remain server-side in environment variables. Never expose secrets in frontend code or NEXT_PUBLIC environment variables.

The Meta-powered intelligence should perform the following tasks:

### A. Multilingual incident understanding

Interpret emergency reports written in different languages and informal language styles.

Support examples such as:
- English
- Swahili
- Sheng
- Other languages supported by the selected model

Do not claim universal African language support without testing it.

### B. Structured incident extraction

For every incoming report, extract a validated structured response containing:

- Incident type.
- Incident description.
- Original report.
- Detected language.
- Translated summary where appropriate.
- Location mentioned.
- Geographic coordinates, only when reliably resolved.
- Severity assessment.
- Urgency.
- People potentially affected, if stated.
- Report timestamp.
- Confidence or uncertainty.
- Missing information.
- Recommended follow-up questions.
- Source report identifier.

Use a strict Pydantic schema.

Never fabricate missing coordinates, casualty numbers, or facts.

### C. Incident intelligence

Identify:
- Possible flooding.
- Fires.
- Road blockages.
- Building damage.
- Medical emergencies.
- Displacement.
- Other relevant emergency categories.

Provide an explanation for classifications.

Severity should be treated as an assessment requiring human review, not an unquestionable fact.

### D. Duplicate incident intelligence

Identify reports that might describe the same event.

Compare:
- Location.
- Time.
- Incident type.
- Description.
- Other available evidence.

Show why two reports may be related.

Never automatically merge reports without preserving their original records.

Allow responders to confirm or reject suggested matches.

### E. Response intelligence briefs

Generate concise incident briefs containing:

- What appears to have happened.
- Where it appears to have happened.
- When it was reported.
- What evidence supports the assessment.
- What remains unknown.
- What information responders should verify.
- Suggested next steps for human review.

Every generated claim must be traceable to available source reports.

---

# 6. VOICE AND MULTIMODAL INTELLIGENCE

Improve the existing voice-reporting workflow.

If Meta Voice Transcribe is available, integrate it properly.

The workflow should be:

1. Record an emergency voice report.
2. Send the recording securely to the backend.
3. Transcribe it using the documented Meta capability.
4. Interpret the transcription using the Meta model.
5. Extract structured incident information.
6. Preserve the original recording and transcription where appropriate.

If voice transcription is not available, implement a clearly labelled fallback rather than pretending it works.

If supported Meta image capabilities are available, allow responders to submit disaster images for analysis.

Do not claim an image proves an incident occurred. Present image observations as supporting evidence requiring verification.

---

# 7. COMMAND CENTER INTERFACE

Build an exceptional, professional emergency operations dashboard.

The design should feel like a serious emergency coordination platform, not a generic admin template.

Use:
- Modern dark command-center interface.
- Excellent typography.
- Clean information hierarchy.
- Subtle animations.
- Responsive layouts.
- Clear visual status indicators.
- Interactive maps.
- Carefully designed cards and panels.

The interface should include:

### A. Main dashboard

Display:
- Total reported incidents.
- Incidents awaiting verification.
- High-priority incidents.
- Potential duplicate reports.
- Recently updated incidents.
- Incident distribution by category.

Clearly distinguish simulated data from real submissions.

### B. Interactive incident map

Display incidents geographically.

Include:
- Incident markers.
- Severity indicators.
- Incident category.
- Selected incident details.
- Map filters.
- Location uncertainty indicators.

Never display invented coordinates as confirmed locations.

### C. Incident intelligence panel

When a responder selects an incident, display:
- Incident summary.
- Original reports.
- AI classification.
- Language and translation.
- Location information.
- Confidence and uncertainty.
- Related reports.
- Evidence history.
- Recommended follow-up questions.

### D. Live incident feed

Use the existing WebSocket infrastructure where possible.

New reports should appear without requiring a full page reload.

### E. Human verification workflow

Responders should be able to:
- Mark an incident as verified.
- Request additional information.
- Change its classification.
- Adjust priority.
- Confirm or reject potential duplicates.
- Record response notes.
- Track status changes.

Maintain an audit trail of these actions.

---

# 8. TECHNICAL ARCHITECTURE

Build this using the existing architecture.

Backend responsibilities:
- Report ingestion.
- Meta AI inference.
- Schema validation.
- Geolocation resolution.
- Duplicate candidate detection.
- Incident storage.
- WebSocket broadcasting.
- Audit logging.
- Error handling.

Frontend responsibilities:
- Dashboard.
- Incident submission.
- Incident map.
- Incident intelligence.
- Verification workflow.
- Real-time updates.
- Evidence display.

Use appropriate database persistence if the project does not already have it.

Implement robust error handling for:
- Meta API failures.
- Timeouts.
- Invalid model responses.
- Missing locations.
- Unsupported languages.
- Duplicate detection errors.
- Missing audio or image inputs.

Do not silently swallow errors.

---

# 9. ENGINEERING QUALITY

This is a competitive engineering project.

Implement:

- Typed API contracts.
- Pydantic validation.
- Proper environment configuration.
- Secure server-side API calls.
- Clear separation of services.
- Useful logging.
- Error states.
- Loading states.
- Empty states.
- Responsive design.
- Basic automated tests.

Create tests for:
- Multilingual report extraction.
- Invalid model output.
- Missing location.
- Duplicate candidate detection.
- Incident verification.
- Meta API timeout.
- Evidence traceability.

Create a synthetic evaluation dataset of approximately 30–50 fictional reports.

Measure and document:
- Structured output validity.
- Incident classification accuracy.
- Location resolution performance.
- Duplicate detection errors.
- Source traceability.
- Model failure handling.

Do not invent performance statistics. Report only results obtained from actual tests.

---

# 10. DEMONSTRATION SCENARIO

Prepare a compelling, reproducible demonstration using fictional data.

Scenario:

Several community members report flooding around the same general area.

Some reports are in English, others in Swahili or Sheng.

The reports contain:
- Different descriptions.
- Incomplete location details.
- Different timestamps.
- Potentially overlapping information.

Show the following:

1. A new report arrives.
2. Meta AI interprets the report.
3. The system extracts structured incident information.
4. The dashboard updates.
5. The map displays the incident when its location is sufficiently established.
6. Another similar report arrives.
7. The system identifies it as a possible duplicate.
8. A responder inspects the original reports.
9. The AI generates an evidence-backed intelligence brief.
10. The responder reviews and approves the next action.

Label fictional and simulated reports clearly.

The demonstration must show actual working features, not fabricated live activity.

---

# 11. HACKATHON SUBMISSION PREPARATION

Create or update the following:

1. README.md
   - Problem.
   - Solution.
   - Architecture.
   - Meta AI integration.
   - Installation.
   - Environment variables.
   - Running instructions.
   - Testing instructions.
   - Screenshots.
   - What was built during the hackathon.

2. HACKATHON_BUILD_LOG.md
   - Existing features.
   - Newly implemented features.
   - Technical decisions.
   - Testing performed.
   - Known limitations.

3. ARCHITECTURE.md
   - System architecture.
   - Data flow.
   - AI integration.
   - Security considerations.

4. DEMO_SCRIPT.md
   - A compelling three-minute demonstration.
   - Exact actions to perform.
   - What to show on screen.
   - Key talking points.

5. .env.example
   - Required environment variables.
   - No actual secrets.

6. Automated test suite.

Prepare the application for a clean, reproducible demonstration.

---

# 12. WORKING METHOD — FOLLOW THIS ORDER

Do not attempt to rewrite the entire project blindly.

PHASE 1 — REPOSITORY AUDIT

Inspect all files.

Identify:
- Existing functionality.
- Broken functionality.
- Existing API endpoints.
- Database setup.
- Existing AI integration.
- Frontend structure.
- Current limitations.

Provide a concise implementation plan.

PHASE 2 — META MODEL VERIFICATION

Inspect the available Meta API documentation.

Confirm the model identifier, endpoint, authentication, supported inputs, response format, and limitations.

Perform a small real API test before building the full integration.

PHASE 3 — IMPLEMENTATION

Build the Meta-powered intelligence workflow first.

Then implement:
- Structured incident extraction.
- Duplicate candidate detection.
- Evidence traceability.
- Incident intelligence briefs.
- Dashboard integration.
- Verification workflow.
- Real-time updates.

PHASE 4 — TESTING

Run the application.

Run backend tests.

Run frontend checks and build.

Test the actual Meta integration.

Fix errors.

PHASE 5 — POLISH

Improve the interface.

Make the main workflow visually impressive and reliable.

Remove broken or misleading demo features.

PHASE 6 — SUBMISSION

Prepare all hackathon documentation.

Make the new work easy for judges to identify.

Prepare the three-minute demo.

---

# 13. IMPORTANT EXECUTION RULES

1. Do not stop after generating a plan. Continue into implementation.
2. Do not replace working functionality without a reason.
3. Do not build a generic chatbot.
4. Do not build a basic RAG application.
5. Do not fabricate AI results or test statistics.
6. Do not pretend simulated data is live emergency data.
7. Do not claim a Meta capability works until it has been tested.
8. Do not expose API keys.
9. Do not automatically execute emergency actions.
10. Do not make unsupported claims about language coverage.
11. Do not create unnecessary complexity that threatens completion before the hackathon deadline.
12. Keep the application runnable throughout development.

If something requires credentials, account access, or a decision from me, explain exactly what is needed and continue with independent work.

Prioritize a complete, working end-to-end experience over a large collection of unfinished features.

---

# 14. DEFINITION OF DONE

The project is not complete merely because the UI looks impressive.

It is complete when:

- The application starts successfully.
- A user can submit an incident report.
- The backend sends the report to an actual available Meta model.
- The Meta model produces structured incident intelligence.
- The backend validates and stores the result.
- The dashboard displays the result.
- A responder can inspect the source evidence.
- Potential duplicates can be reviewed.
- An incident can be verified by a human.
- The tests run successfully.
- The README explains how to reproduce the project.
- The three-minute demo can be performed reliably.

Begin by inspecting the repository and reporting the existing architecture.

Then implement the project in small, working phases.

**Our goal is not to build the biggest disaster dashboard. Our goal is to demonstrate an original, technically credible use of Meta AI that transforms fragmented community emergency reports into trustworthy, actionable intelligence.**
