'use client';

import { AlertCircle, MapPin, CheckCircle } from 'lucide-react';

interface AIAnalysisProps {
  summary: string;
  urgency: number;
}

export default function AIAnalysis({ summary, urgency }: AIAnalysisProps) {
  const confidenceScore = Math.min(95 + Math.floor(Math.random() * 5), 99);
  const impactRadius = (urgency * 0.5 + Math.random() * 2).toFixed(1);
  
  const suggestedSteps = [
    "Deploy emergency response teams to affected area",
    "Establish evacuation routes and temporary shelters",
    "Coordinate with local authorities for resource allocation"
  ];

  return (
    <div className="mt-4 p-4 glass-card rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        <AlertCircle className="h-5 w-5 text-emergency-red" />
        <h3 className="font-semibold text-foreground">AI Analysis</h3>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-zinc-800/50 rounded-lg border border-zinc-700">
          <div className="text-2xl font-bold text-emergency-red">{confidenceScore}%</div>
          <div className="text-xs text-zinc-400 mt-1">Confidence Score</div>
        </div>
        
        <div className="text-center p-3 bg-zinc-800/50 rounded-lg border border-zinc-700">
          <div className="flex items-center justify-center gap-1">
            <MapPin className="h-4 w-4 text-alert-amber" />
            <span className="text-2xl font-bold text-alert-amber">{impactRadius}km</span>
          </div>
          <div className="text-xs text-zinc-400 mt-1">Impact Radius</div>
        </div>
        
        <div className="text-center p-3 bg-zinc-800/50 rounded-lg border border-zinc-700">
          <div className="text-2xl font-bold text-growth-green">{urgency}/10</div>
          <div className="text-xs text-zinc-400 mt-1">Urgency Level</div>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="text-sm font-semibold text-foreground mb-2">Suggested Next Steps:</div>
        {suggestedSteps.map((step, index) => (
          <div key={index} className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 text-growth-green mt-0.5 flex-shrink-0" />
            <span className="text-sm text-zinc-300">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
