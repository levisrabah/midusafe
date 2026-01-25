# MIDUSAFE
### Real-time Emergency Synthesis & Coordination Unified Engine

**MIDUSAFE** is a high-performance AI command center designed for disaster response and climate resilience. It transforms the "noise" of a crisis—fragmented social media feeds, sensor data, and satellite imagery—into a single, actionable **Common Operational Picture (COP)**.

---

## 🛡️ Project Vision
In the first hours of a disaster, data is chaotic. MIDUSAFE uses multi-modal AI to fuse crowd-sourced intelligence with official data streams, allowing emergency managers to visualize verified threats and deploy resources with surgical precision.

## 🚀 Key Features (The Tech Stack)
- **AI Triage Pipeline:** - **NLP (LLMs):** Extracting urgency, location, and needs from unstructured text (WhatsApp, Tweets).
    - **Computer Vision:** Analyzing images/videos for flood levels, fire spread, and structural damage.
- **Fusion Core:** - Cross-validates citizen reports with satellite/sensor data.
    - Calculates a "Confidence Score" for every incident.
- **Dynamic Command Dashboard:**
    - Real-time Mapbox integration with live incident pins.
    - AI-predicted hazard propagation layers.
    - Priority-ranked emergency feed.

## 🏗️ Technical Architecture
- **Frontend:** Next.js 14+, Tailwind CSS, Shadcn/UI, Mapbox GL JS.
- **Backend:** FastAPI (Python) for heavy AI processing.
- **Database:** Supabase (PostgreSQL + Real-time subscriptions).
- **AI Engine:** OpenAI GPT-4o (Multimodal) & LangChain for orchestration.

## 🛠️ Rapid Development Guide (For Cursor AI)
When generating code for this project, always adhere to:
1. **High-Urgency UI:** Use dark modes, high-contrast alerts (Reds/Ambers), and real-time animations.
2. **Modular Logic:** Keep the AI Triage logic separate from the Mapping components.
3. **Mock Data First:** Use the `/data/mock-incidents.json` for initial frontend rendering.