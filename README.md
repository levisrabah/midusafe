# MIDUSAFE
### Real-time Emergency Synthesis & Coordination Unified Engine

**MIDUSAFE** is a high-performance AI command center designed for disaster response and climate resilience. It transforms the "noise" of a crisis—fragmented social media feeds, sensor data, and satellite imagery—into a single, actionable **Common Operational Picture (COP)**.

---

## Project Vision
In the first hours of a disaster, data is chaotic. MIDUSAFE uses multi-modal AI to fuse crowd-sourced intelligence with official data streams, allowing emergency managers to visualize verified threats and deploy resources with surgical precision.

**🌍 Enhanced with Vernacular-First Support for Kenya & East Africa**

## 🌍 Vernacular-First Features
- **Universal Language Detection**: Auto-detects ANY language including English, Swahili, Sheng, Dholuo, Kalenjin, Gikuyu, Luhya, Somali, French, Arabic
- **Code-Switching Support**: Handles mixed-language sentences (e.g., "Moto umekuwa serious, watu wanarun tao")
- **Cultural Context Awareness**: Extracts meaning from local terms like 'Boma', 'Shamba', 'Stage', 'Mtaa', 'Gichagi'
- **Native Dialect Labeling**: Identifies specific Kenyan dialects (e.g., 'Native: Kalenjin', 'Native: Gikuyu')
- **Ground Truth Display**: Shows original vernacular reports alongside English translations

## 🚀 Production-Grade Command Center Features

### Unified Navigation & Mission Control
- **Consolidated h-16 Navbar**: Glass-morphism design with `bg-zinc-950/90 backdrop-blur-md`
- **Real-Time Clock**: Auto-timezone detection with `font-mono` display updating every 1000ms
- **Climate Metrics Strip**: Live CO2 (422ppm), Temperature (+1.2°C), Active Units (1,240)
- **Language Toggle Dropdown**: 10+ language support with flag indicators

### Advanced AI Triage Pipeline
- **Universal Language Support**: Enhanced Gemini prompt for any language detection
- **Enhanced Disaster Types**: structural_collapse, industrial_accident, gas_leak, landslide, storm, erosion, heatwave, disease_outbreak
- **Geospatial Intelligence**: Precise Kenyan location mapping using place names
- **Confidence Scoring**: 0.0 to 1.0 reliability assessment

### Professional UI/UX
- **Zero-Overlap Layout**: Fixed `pt-20` padding prevents navbar clipping
- **Bottom-Center Toasts**: 8-second duration with `z-[100]` and slide-up animations
- **Language Badges**: 🇬🇧 EN, 🇰🇪 SW, 🇰🇪 SH, 🇰🇪 LUO, 🇰🇪 KAL, 🇸🇴 SOM, etc.
- **Ground Truth Cards**: Original vernacular text with cultural context sections
- **Distinct Map Markers**: Color-coded for specific locations (Thika=Orange, KU=Blue, Wendani=Green)

### Voice Recording System
- **Browser MediaRecorder API**: Native audio capture with WAV output
- **Recording Controls**: Start, Pause/Resume, Stop with real-time timer
- **Visual Feedback**: Pulsing indicators and smooth state transitions
- **Transcription Ready**: Placeholder for speech-to-text integration

## 📍 Hyper-Local Data Integration
- **23 Kenyan Scenarios**: Targeting Thika, Kenyatta University, Kahawa Wendani, Westlands, Dunga (Kisumu), Homa Bay
- **Vernacular Reports**:
  - **Dholuo**: "Pi ochopo e dhoot e Homa Bay" (Water reached doorstep)
  - **Sheng**: "Mvua imepiga Wendani bypass ni river" (Rain hit Wendani, bypass is river)
  - **Code-Switching**: "Moto umekuwa serious, watu wanarun tao"
- **Precise Coordinates**: Map markers fly-to exact locations

## 🏗️ Technical Architecture
- **Frontend**: Next.js 14+, Tailwind CSS, Shadcn/UI, Framer Motion, Leaflet Maps
- **Backend**: FastAPI (Python) with Gemini AI integration
- **Real-time**: WebSocket connections for live alert broadcasting
- **AI Engine**: Google Gemini 2.0 Flash for multilingual triage
- **Voice**: Browser MediaRecorder API for audio capture

## 🛠️ Development Guide

### Key Components
- **Unified Navbar** (`/components/dashboard/unified-navbar.tsx`): Mission control strip with clock and language toggle
- **AI Triage** (`/triage.py`): Universal language detection and cultural context extraction
- **Voice Recording** (`/components/dashboard/community-report-button.tsx`): Full audio capture functionality
- **Live Feed** (`/components/dashboard/live-feed.tsx`): Multilingual alert cards with ground truth
- **Toast System** (`/components/ui/toast.tsx`): Bottom-center notifications with 8s duration

### Data Flow
1. **Report Input**: Text or voice → Community Report Button
2. **AI Processing**: Universal language detection → Cultural context → Translation
3. **Broadcast**: WebSocket → Real-time dashboard updates
4. **Display**: Language badges → Ground truth → Map markers

### Mock Data
- **Location**: `/data/mock-incidents.json` - 23 hyper-local Kenyan scenarios
- **Simulation**: `python3 simulation.py` - Test multilingual reporting

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google Gemini API key

### Installation
```bash
# Backend
cd /home/levis/midusafe
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd dashboard
npm install
```

### Running the Application
```bash
# Start Backend (Terminal 1)
source venv/bin/activate
python3 main.py

# Start Frontend (Terminal 2)
cd dashboard
npm run dev

# Test Simulation (Terminal 3)
python3 simulation.py
```

### Environment Variables
```bash
# Backend
GEMINI_API_KEY=your_gemini_api_key

# Frontend (optional)
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/alerts
```

## 🎯 Usage Instructions

### For Emergency Managers
1. **Monitor Dashboard**: Real-time alerts with language badges and cultural context
2. **View Ground Truth**: Original vernacular reports for authentic community voice
3. **Track Locations**: Color-coded map markers for precise incident locations
4. **Language Toggle**: Switch interface language for multilingual teams

### For Community Reporting
1. **Click Red Button**: Floating "Report Incident" button
2. **Voice or Text**: Record voice or type in any language
3. **Location**: Specify Kenyan location (Thika, KU, Wendani, etc.)
4. **Submit**: Real-time AI triage and dashboard broadcast

### Supported Languages
- **Primary**: English, Swahili, Sheng, Dholuo
- **Extended**: Kalenjin, Gikuyu, Luhya, Somali, French, Arabic
- **Code-Switching**: Mixed language sentences automatically handled

## 🔧 Development Guidelines

### UI/UX Standards
1. **High-Urgency Design**: Dark modes, high-contrast alerts (Reds/Ambers), real-time animations
2. **Vernacular-First**: Always show original text with translation
3. **Cultural Sensitivity**: Respect local terminology and context
4. **Zero Overlap**: Proper z-index hierarchy and padding

### Code Architecture
1. **Modular Components**: Separate AI triage from mapping and UI
2. **TypeScript**: Strict typing for all interfaces
3. **Real-time First**: WebSocket-driven updates
4. **Responsive Design**: Mobile-first approach

### Testing
```bash
# Test multilingual scenarios
python3 simulation.py

# Test voice recording
# Click red button → Start Recording → Speak → Stop → Submit

# Test language detection
# Submit reports in: "Pi ochopo e dhoot", "Mvua imepiga", "Fire serious"
```

## 🌟 Production Features

### Command Center Ready
- **Professional UI**: Unified navbar with mission control strip
- **Real-time Clock**: Auto-timezone detection with live updates
- **Climate Metrics**: Live environmental data display
- **Language Intelligence**: Universal detection with cultural context

### Emergency Response
- **Ground Truth**: Original vernacular reports preserved
- **Cultural Context**: Local terminology explained
- **Geospatial Precision**: Kenyan location intelligence
- **Multilingual Teams**: Interface language switching

### Scalability
- **WebSocket Architecture**: Real-time for thousands of concurrent users
- **AI Triage**: Gemini 2.0 Flash for fast processing
- **Modular Design**: Easy feature addition and maintenance

---

**MIDUSAFE** - Transforming emergency response through vernacular-first AI intelligence and cultural awareness. Built for Kenya, ready for the world.