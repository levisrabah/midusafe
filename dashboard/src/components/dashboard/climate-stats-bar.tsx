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
    <div className="fixed top-0 left-0 right-0 z-10 flex h-16 items-center border-b border-white/10 bg-card/50 px-4 backdrop-blur-sm">
      <div className="flex items-center gap-2">
        <div className="h-3 w-3 animate-pulse rounded-full bg-emergency-red" />
        <p className="font-semibold text-red-500">Live</p>
      </div>
      <div className="flex flex-1 justify-center gap-12">
        {stats.map((stat) => (
          <div key={stat.name} className="flex items-center gap-3">
            {stat.icon}
            <div>
              <p className="text-xs text-muted-foreground">{stat.name}</p>
              <p className="text-sm font-bold">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
