import { Alert, DisasterType } from '@/types/alert';
import { motion } from 'framer-motion';
import { Flame, Waves, Zap, Wind, Mountain } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import AIAnalysis from './ai-analysis';

const disasterIcons: Record<DisasterType, React.ReactElement> = {
  Wildfire: <Flame className="h-5 w-5" />,
  Flood: <Waves className="h-5 w-5" />,
  Earthquake: <Zap className="h-5 w-5" />,
  Tornado: <Wind className="h-5 w-5" />,
  Volcano: <Mountain className="h-5 w-5" />,
};

const UrgencyIndicator = ({ urgency }: { urgency: number }) => {
  const color = urgency > 8 ? 'text-emergency-red' : urgency > 5 ? 'text-alert-amber' : 'text-growth-green';
  const circumference = 2 * Math.PI * 18;
  const strokeDashoffset = circumference - (urgency / 10) * circumference;

  return (
    <div className={`relative h-12 w-12 font-bold ${color}`}>
      <svg className="absolute top-0 left-0 h-full w-full" viewBox="0 0 40 40">
        <circle
          cx="20"
          cy="20"
          r="18"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          className="opacity-20"
        />
        <circle
          cx="20"
          cy="20"
          r="18"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 20 20)"
        />
      </svg>
      <span className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-sm">
        {urgency}
      </span>
    </div>
  );
};

export default function AiTriageCard({ alert }: { alert: Alert }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="mb-4 glass-card rounded-lg p-4 shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <UrgencyIndicator urgency={alert.urgency} />
          <div>
            <Badge variant="destructive" className="flex items-center gap-2 bg-emergency-red hover:bg-emergency-red/90">
              {disasterIcons[alert.disaster_type]}
              <span className="font-semibold">{alert.disaster_type}</span>
            </Badge>
            <p className="mt-1 text-xs text-zinc-400">{new Date(alert.timestamp).toLocaleString()}</p>
          </div>
        </div>
      </div>
      
      <AIAnalysis summary={alert.summary} urgency={alert.urgency} />
    </motion.div>
  );
}
