'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/use-web-socket';
import { useAlerts } from '@/hooks/use-alerts';
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

const WS_URL = 'ws://localhost:8000/ws/alerts';

export default function DashboardPage() {
  const wsAlerts = useWebSocket<Alert>(WS_URL);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const { 
    alerts, 
    addAlert, 
    toasts, 
    removeToast, 
    systemStatus 
  } = useAlerts();

  // Sync WebSocket alerts with global state
  useEffect(() => {
    if (wsAlerts.length > alerts.length) {
      // New alerts received via WebSocket
      const newAlerts = wsAlerts.slice(0, wsAlerts.length - alerts.length);
      newAlerts.forEach(alert => addAlert(alert));
    }
  }, [wsAlerts, alerts.length, addAlert]);

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
        {/* Left Sidebar - System Status & Live Feed */}
        <div className="col-span-4 h-full overflow-hidden space-y-4">
          <SystemStatus 
            aiBackend={systemStatus.aiBackend}
            liveFeed={systemStatus.liveFeed}
          />
          <div className="h-full glass-sidebar rounded-lg flex-1">
            <LiveFeed alerts={alerts} />
          </div>
        </div>
        
        {/* Interactive Map */}
        <div className="col-span-8 h-full">
          <div className="h-full glass-card rounded-lg border border-zinc-800">
            <InteractiveMapLeaflet alerts={alerts} />
          </div>
        </div>
      </div>
      
      {/* Simulate Button */}
      <SimulateButton />
      
      {/* Community Report Button */}
      <CommunityReportButton />
    </main>
  );
}

