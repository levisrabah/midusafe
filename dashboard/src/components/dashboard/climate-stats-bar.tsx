import { ShieldCheck, Thermometer, Users, TrendingUp } from 'lucide-react';

const stats = [
  {
    name: 'CO2 Levels',
    value: '422ppm',
    icon: <Thermometer className="h-5 w-5 text-alert-amber" />,
  },
  {
    name: 'Active Responders',
    value: '1,240',
    icon: <Users className="h-5 w-5 text-growth-green" />,
  },
  {
    name: 'Saved Lives',
    value: '14',
    icon: <ShieldCheck className="h-5 w-5 text-emergency-red" />,
  },
  {
    name: 'Global Temp. Anomaly',
    value: '+1.2°C',
    icon: <TrendingUp className="h-5 w-5 text-alert-amber" />,
  },
];

export default function ClimateStatsBar() {
  return (
    <div className="fixed top-16 left-0 right-0 z-40 glass-morphism border-b border-zinc-800 px-4">
      <div className="flex items-center justify-between py-3">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-emergency-red pulse-dot" />
          <p className="font-semibold text-emergency-red">SYSTEM ACTIVE</p>
        </div>
        
        <div className="flex gap-8">
          {stats.map((stat) => (
            <div key={stat.name} className="flex items-center gap-3">
              {stat.icon}
              <div>
                <p className="text-xs text-zinc-400">{stat.name}</p>
                <p className="text-sm font-bold text-foreground">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-xs text-zinc-500">
          MIDUSAFE v2.0 | UN Disaster Response
        </div>
      </div>
    </div>
  );
}
