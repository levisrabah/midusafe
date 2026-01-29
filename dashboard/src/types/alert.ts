import { LucideIcon } from 'lucide-react';

export type DisasterType = 'Wildfire' | 'Flood' | 'Earthquake' | 'Tornado' | 'Volcano' | 'fire' | 'flood' | 'medical' | 'other';

export interface Alert {
  id: string;
  urgency: number; // 0-10
  urgency_score?: number; // Alternative field name from backend
  disaster_type: DisasterType;
  location: {
    lat: number;
    lng: number;
  };
  summary: string;
  english_summary?: string; // Alternative field name from backend
  timestamp: string;
  confidence: number; // 0.0-1.0
  message?: string;
  analysis?: any;
  detected_language?: string;
  original_text?: string;
  suggested_actions?: string;
  cultural_context?: string;
}

// Map backend disaster types to frontend display types
export const mapDisasterType = (type: string): DisasterType => {
  const typeMap: Record<string, DisasterType> = {
    'fire': 'Wildfire',
    'flood': 'Flood',
    'medical': 'Earthquake', // Using Earthquake as placeholder for medical emergencies
    'other': 'Tornado',
  };
  return typeMap[type] || 'Tornado';
};
