'use client';

import { Activity, Thermometer, Users } from 'lucide-react';

export default function LiveHeaderTicker() {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 glass-morphism border-b border-zinc-800">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emergency-red pulse-dot" />
          <span className="text-sm font-semibold text-emergency-red">LIVE</span>
        </div>
        
        <div className="flex items-center gap-8 text-sm">
          <div className="flex items-center gap-2">
            <Thermometer className="h-4 w-4 text-alert-amber" />
            <span className="text-zinc-300">Global Temp: <span className="text-alert-amber font-semibold">+1.2°C</span></span>
          </div>
          
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-growth-green" />
            <span className="text-zinc-300">Active Response Units: <span className="text-growth-green font-semibold">42</span></span>
          </div>
          
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-emergency-red" />
            <span className="text-zinc-300">Live Emergency Feed: <span className="text-emergency-red font-semibold">Active</span></span>
          </div>
        </div>
        
        <div className="text-xs text-zinc-500">
          UN Disaster Response System v2.0
        </div>
      </div>
    </div>
  );
}
