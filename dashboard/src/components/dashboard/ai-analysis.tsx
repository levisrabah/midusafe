'use client';

import { motion } from 'framer-motion';
import { Brain, Target, CheckCircle, AlertTriangle } from 'lucide-react';
import { Alert } from '@/types/alert';

interface AIAnalysisProps {
  alert: Alert;
}

export default function AIAnalysis({ alert }: AIAnalysisProps) {
  const confidence = alert.confidence || 0.8;
  const confidenceColor = confidence >= 0.9 ? 'text-emerald-400' : confidence >= 0.7 ? 'text-yellow-400' : 'text-rose-400';
  
  // Calculate impact radius based on urgency
  const impactRadius = alert.urgency >= 8 ? '5.0km' : alert.urgency >= 6 ? '3.0km' : '1.5km';
  
  // Generate suggested next steps based on disaster type and urgency
  const getSuggestedSteps = () => {
    const steps = [];
    
    if (alert.urgency >= 8) {
      steps.push('Immediate evacuation recommended');
      steps.push('Deploy emergency response units');
    } else if (alert.urgency >= 6) {
      steps.push('Monitor situation closely');
      steps.push('Prepare contingency plans');
    } else {
      steps.push('Continue monitoring');
      steps.push('Update local authorities');
    }
    
    // Add disaster-specific steps
    switch (alert.disaster_type) {
      case 'Wildfire':
        steps.push('Establish firebreaks');
        break;
      case 'Flood':
        steps.push('Monitor water levels');
        break;
      case 'Earthquake':
        steps.push('Check infrastructure integrity');
        break;
      default:
        steps.push('Assess damage and needs');
    }
    
    return steps.slice(0, 3); // Return only top 3 steps
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card border border-zinc-800 rounded-lg p-6 space-y-4"
    >
      <div className="flex items-center gap-2 mb-4">
        <Brain className="h-5 w-5 text-emerald-400" />
        <h3 className="text-lg font-semibold text-zinc-200">AI Analysis</h3>
      </div>
      
      {/* Confidence Score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-zinc-400" />
          <span className="text-sm text-zinc-400">Confidence Score</span>
        </div>
        <span className={`text-lg font-bold ${confidenceColor}`}>
          {(confidence * 100).toFixed(0)}%
        </span>
      </div>
      
      {/* Impact Radius */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-zinc-400" />
          <span className="text-sm text-zinc-400">Impact Radius</span>
        </div>
        <span className="text-sm font-medium text-rose-400">
          {impactRadius}
        </span>
      </div>
      
      {/* Urgency Level */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${
            alert.urgency >= 8 ? 'bg-rose-500' : 
            alert.urgency >= 6 ? 'bg-yellow-500' : 
            'bg-emerald-500'
          }`} />
          <span className="text-sm text-zinc-400">Urgency Level</span>
        </div>
        <span className={`text-sm font-medium ${
          alert.urgency >= 8 ? 'text-rose-400' : 
          alert.urgency >= 6 ? 'text-yellow-400' : 
          'text-emerald-400'
        }`}>
          {alert.urgency}/10
        </span>
      </div>
      
      {/* Suggested Next Steps */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-zinc-300 flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-emerald-400" />
          Suggested Next Steps
        </h4>
        <div className="space-y-1">
          {getSuggestedSteps().map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-2"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
              <p className="text-xs text-zinc-400 leading-relaxed">{step}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
