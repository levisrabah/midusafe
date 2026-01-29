'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Clock, MapPin } from 'lucide-react';
import { Alert } from '@/types/alert';
import AIAnalysis from './ai-analysis';
import { useAlerts } from '@/hooks/use-alerts';

interface LiveFeedProps {
  alerts: Alert[];
}

export default function LiveFeed({ alerts }: LiveFeedProps) {
  const { selectAlert, selectedAlert } = useAlerts();

  const getUrgencyColor = (urgency: number) => {
    if (urgency >= 8) return 'text-rose-400 border-rose-500/50';
    if (urgency >= 6) return 'text-yellow-400 border-yellow-500/50';
    return 'text-emerald-400 border-emerald-500/50';
  };

  const getDisasterIcon = (type: string) => {
    // Return appropriate icon based on disaster type
    return <AlertTriangle className="h-4 w-4" />;
  };

  const getLanguageBadge = (language: string) => {
    const langMap = {
      'english': '🇰🇪 EN',
      'swahili': '🇰🇪 SW',
      'sheng': '🇰🇪 SH',
      'dholuo': '🇰🇪 LUO'
    };
    return langMap[language as keyof typeof langMap] || '🇰🇪 EN';
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-lg font-semibold text-zinc-200 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-emergency-red" />
          Live Alert Feed
        </h2>
        <p className="text-xs text-zinc-500 mt-1">
          {alerts.length} active {alerts.length === 1 ? 'alert' : 'alerts'}
        </p>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <AnimatePresence mode="popLayout">
          {alerts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-card border border-zinc-800 rounded-lg p-6 text-center"
            >
              <AlertTriangle className="h-12 w-12 text-zinc-600 mx-auto mb-3" />
              <p className="text-zinc-400 text-sm">No active alerts</p>
              <p className="text-zinc-600 text-xs mt-1">Waiting for emergency reports...</p>
            </motion.div>
          ) : (
            alerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -50, scale: 0.9 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 50, scale: 0.9, transition: { duration: 0.2 } }}
                transition={{ 
                  duration: 0.3, 
                  delay: index * 0.1,
                  type: "spring",
                  stiffness: 100
                }}
                whileHover={{ scale: 1.02 }}
                onClick={() => selectAlert(alert)}
                className={`
                  glass-card border rounded-lg p-4 cursor-pointer transition-all
                  ${selectedAlert?.id === alert.id 
                    ? 'border-emerald-500/50 bg-emerald-500/5' 
                    : 'border-zinc-800 hover:border-zinc-700'
                  }
                `}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg border ${getUrgencyColor(alert.urgency)}`}>
                      {getDisasterIcon(alert.disaster_type)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-zinc-200 text-sm">
                          {alert.disaster_type}
                        </h3>
                        <span className="text-xs font-medium text-zinc-400 bg-zinc-800 px-2 py-1 rounded">
                          {getLanguageBadge((alert as any).detected_language || 'english')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-zinc-500">
                        <Clock className="h-3 w-3" />
                        {alert.timestamp}
                      </div>
                    </div>
                  </div>
                  <div className={`text-xs font-medium px-2 py-1 rounded-full border ${getUrgencyColor(alert.urgency)}`}>
                    {alert.urgency}/10
                  </div>
                </div>

                <p className="text-sm text-zinc-300 mb-3 line-clamp-2">
                  {(alert as any).translated_summary || alert.summary}
                </p>

                {(alert as any).original_text && (alert as any).original_text !== (alert as any).translated_summary && (
                  <p className="text-xs text-zinc-400 italic mb-3 line-clamp-2">
                    "Original: {(alert as any).original_text}"
                  </p>
                )}

                {alert.location && (
                  <div className="flex items-center gap-1 text-xs text-zinc-500">
                    <MapPin className="h-3 w-3" />
                    <span>
                      {alert.location.lat.toFixed(4)}, {alert.location.lng.toFixed(4)}
                    </span>
                  </div>
                )}

                {/* Show AI Analysis for selected alert */}
                {selectedAlert?.id === alert.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mt-4 pt-4 border-t border-zinc-800"
                  >
                    <AIAnalysis alert={alert} />
                  </motion.div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
