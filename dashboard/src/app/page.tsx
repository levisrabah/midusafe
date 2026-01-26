'use client';

import { useWebSocket } from '@/hooks/use-web-socket';
import { Alert } from '@/types/alert';
import ClimateStatsBar from '@/components/dashboard/climate-stats-bar';
import InteractiveMapLeaflet from '@/components/dashboard/interactive-map-leaflet';
import LiveFeed from '@/components/dashboard/live-feed';
import SimulateButton from '@/components/dashboard/simulate-button';
import LiveHeaderTicker from '@/components/dashboard/live-header-ticker';

const WS_URL = 'ws://localhost:8000/ws/alerts';

export default function DashboardPage() {
  const alerts = useWebSocket<Alert>(WS_URL);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-zinc-950 font-sans">
      {/* Background grid pattern */}
      <div
        className="absolute inset-0 bg-grid-zinc-500/10 bg-center opacity-30"
        style={{
          maskImage: 'linear-gradient(to bottom, white, white, transparent)',
        }}
      />
      
      {/* Live Header Ticker */}
      <LiveHeaderTicker />
      
      {/* Climate Stats Bar */}
      <ClimateStatsBar />
      
      {/* Main Content */}
      <div className="grid h-full grid-cols-12 gap-4 p-4 pt-32">
        {/* Live Feed Sidebar */}
        <div className="col-span-4 h-full overflow-hidden">
          <div className="h-full glass-sidebar rounded-lg">
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
    </main>
  );
}

