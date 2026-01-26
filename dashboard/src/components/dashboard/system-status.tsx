'use client';

import { motion } from 'framer-motion';
import { Wifi, WifiOff, Activity, Power } from 'lucide-react';

interface SystemStatusProps {
  aiBackend: 'Connected' | 'Disconnected';
  liveFeed: 'Active' | 'Inactive';
}

export default function SystemStatus({ aiBackend, liveFeed }: SystemStatusProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-card border border-zinc-800 rounded-lg p-4 mb-4"
    >
      <h3 className="text-sm font-semibold text-zinc-300 mb-3">
        System Status
      </h3>

      <div className="space-y-2">
        {/* AI Backend */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {aiBackend === 'Connected' ? (
              <Wifi className="h-4 w-4 text-emerald-400" />
            ) : (
              <WifiOff className="h-4 w-4 text-rose-400" />
            )}
            <span className="text-xs text-zinc-400">AI Backend</span>
          </div>
          <span
            className={`text-xs font-medium ${
              aiBackend === 'Connected'
                ? 'text-emerald-400'
                : 'text-rose-400'
            }`}
          >
            {aiBackend}
          </span>
        </div>

        {/* Live Feed */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {liveFeed === 'Active' ? (
              <Activity className="h-4 w-4 text-emerald-400" />
            ) : (
              <Power className="h-4 w-4 text-zinc-500" />
            )}
            <span className="text-xs text-zinc-400">Live Feed</span>
          </div>
          <span
            className={`text-xs font-medium ${
              liveFeed === 'Active'
                ? 'text-emerald-400'
                : 'text-zinc-500'
            }`}
          >
            {liveFeed}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
