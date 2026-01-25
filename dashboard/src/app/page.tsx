'use client';

import { useWebSocket } from '@/hooks/use-web-socket';
import { Alert } from '@/types/alert';
import ClimateStatsBar from '@/components/dashboard/climate-stats-bar';
import InteractiveMap from '@/components/dashboard/interactive-map';
import LiveFeed from '@/components/dashboard/live-feed';
import SimulateButton from '@/components/dashboard/simulate-button';

const WS_URL = 'ws://localhost:8000/ws/alerts';

export default function DashboardPage() {
  const alerts = useWebSocket<Alert>(WS_URL);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-background font-sans">
      <div
        className="absolute inset-0 bg-grid-zinc-500/10 bg-center"
        style={{
          maskImage: 'linear-gradient(to bottom, white, white, transparent)',
        }}
      />
      <ClimateStatsBar />
      <div className="grid h-full grid-cols-12 gap-4 p-4 pt-20">
        <div className="col-span-4 h-full overflow-y-auto rounded-lg bg-card/50 backdrop-blur-sm">
          <LiveFeed alerts={alerts} />
        </div>
        <div className="col-span-8 h-full rounded-lg bg-card/50 backdrop-blur-sm">
          <InteractiveMap alerts={alerts} />
        </div>
      </div>
      <SimulateButton />
    </main>
  );
}

