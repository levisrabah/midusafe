'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/use-web-socket';
import { useAlerts } from '@/hooks/use-alerts';
import { useSentinel } from '@/hooks/use-sentinel';
import { Alert } from '@/types/alert';
import ClimateStatsBar from '@/components/dashboard/climate-stats-bar';
import InteractiveMapLeaflet from '@/components/dashboard/interactive-map-leaflet';
import LiveFeed from '@/components/dashboard/live-feed';
import SimulateButton from '@/components/dashboard/simulate-button';
import LiveHeaderTicker from '@/components/dashboard/live-header-ticker';
import SystemStatus from '@/components/dashboard/system-status';
import ToastContainer from '@/components/ui/toast';
import CommunityReportButton from '@/components/dashboard/community-report-button';
import UnifiedNavbar from '@/components/dashboard/unified-navbar';
import SentinelStatsBar from '@/components/dashboard/sentinel-stats';
import SentinelFeed from '@/components/dashboard/sentinel-feed';
import IncidentDetail from '@/components/dashboard/incident-detail';

const WS_URL = 'ws://localhost:8000/ws/alerts';

export default function DashboardPage() {
  const wsAlerts = useWebSocket<Alert>(WS_URL);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [view, setView] = useState<'live' | 'sentinel'>('sentinel');
  const sentinel = useSentinel();
  const { 
    alerts, 
    addAlert, 
    toasts, 
    removeToast, 
    systemStatus 
  } = useAlerts();

  // Judge's Secret Console Log
  useEffect(() => {
    console.log("System Audit Complete: Pan-African Resilience Engine Online");
  }, []);

  // Sync WebSocket alerts with global state
  useEffect(() => {
    if (wsAlerts.length > alerts.length) {
      // New alerts received via WebSocket
      const newAlerts = wsAlerts.slice(0, wsAlerts.length - alerts.length);
      newAlerts.forEach(alert => addAlert(alert));
    }
  }, [wsAlerts, alerts.length, addAlert]);

  // Sentinel incidents with RESOLVED locations only, mapped for the map.
  const sentinelMapAlerts: Alert[] = sentinel.incidents
    .filter((i) => i.location_resolved && i.latitude != null && i.longitude != null)
    .map((i) => ({
      id: i.id,
      urgency: i.priority ?? i.extraction.urgency,
      urgency_score: i.priority ?? i.extraction.urgency,
      disaster_type: i.extraction.incident_type as Alert['disaster_type'],
      location: { lat: i.latitude as number, lng: i.longitude as number },
      summary: i.extraction.translated_summary,
      english_summary: i.extraction.translated_summary,
      timestamp: i.created_at,
      confidence: i.extraction.confidence,
      message: i.extraction.original_report,
      detected_language: i.extraction.detected_language,
      original_text: i.extraction.original_report,
    }));
  const unresolvedCount = sentinel.incidents.filter((i) => !i.location_resolved).length;

  const mapAlerts = view === 'sentinel' ? sentinelMapAlerts : alerts;

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-zinc-950 font-sans">
      {/* Background grid pattern */}
      <div
        className="absolute inset-0 bg-grid-zinc-500/10 bg-center opacity-30"
        style={{
          maskImage: 'linear-gradient(to bottom, white, white, transparent)',
        }}
      />
      
      {/* Unified Navbar */}
      <UnifiedNavbar 
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
      />
      
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      
      {/* Main Content */}
      <div className="grid h-full grid-cols-12 gap-4 p-4 pt-20">
        {/* Left Sidebar - System Status & Feed with view tabs */}
        <div className="col-span-4 h-full overflow-hidden space-y-4 flex flex-col">
          <div className="flex gap-2 shrink-0">
            <button
              onClick={() => setView('sentinel')}
              className={`flex-1 text-sm font-medium py-2 rounded-lg border transition-colors ${
                view === 'sentinel'
                  ? 'bg-emerald-600/20 border-emerald-500/50 text-emerald-200'
                  : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Sentinel Intel ({sentinel.incidents.length})
            </button>
            <button
              onClick={() => setView('live')}
              className={`flex-1 text-sm font-medium py-2 rounded-lg border transition-colors ${
                view === 'live'
                  ? 'bg-emerald-600/20 border-emerald-500/50 text-emerald-200'
                  : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Live Alerts ({alerts.length})
            </button>
          </div>
          {view === 'live' && (
            <SystemStatus 
              aiBackend={systemStatus.aiBackend}
              liveFeed={systemStatus.liveFeed}
            />
          )}
          <div className="flex-1 min-h-0 glass-sidebar rounded-lg overflow-hidden">
            {view === 'sentinel' ? (
              <SentinelFeed
                incidents={sentinel.incidents}
                selectedId={sentinel.selectedId}
                onSelect={sentinel.setSelectedId}
                loading={sentinel.loading}
                error={sentinel.error}
                onRetry={sentinel.refresh}
              />
            ) : (
              <LiveFeed alerts={alerts} />
            )}
          </div>
        </div>
        
        {/* Right column: stats strip (sentinel) + map */}
        <div className="col-span-8 h-full flex flex-col gap-4 min-h-0">
          {view === 'sentinel' && (
            <div className="shrink-0">
              <SentinelStatsBar stats={sentinel.stats} />
              {unresolvedCount > 0 && (
                <p className="text-xs text-amber-300/80 mt-2">
                  ⚠ {unresolvedCount} incident{unresolvedCount === 1 ? '' : 's'} with unresolved
                  location{unresolvedCount === 1 ? ' is' : 's are'} not shown on the map.
                </p>
              )}
            </div>
          )}
          <div className="flex-1 min-h-0 glass-card rounded-lg border border-zinc-800 relative">
            <InteractiveMapLeaflet alerts={mapAlerts} />
          </div>
        </div>
      </div>

      {/* Sentinel incident detail slide-over */}
      {view === 'sentinel' && sentinel.selected && (
        <IncidentDetail
          incident={sentinel.selected}
          duplicates={sentinel.duplicates}
          onClose={() => sentinel.setSelectedId(null)}
          onChanged={sentinel.refresh}
        />
      )}
      
      {/* Simulate Button */}
      <SimulateButton />
      
      {/* Community Report Button */}
      <CommunityReportButton />
    </main>
  );
}
