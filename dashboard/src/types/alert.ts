import { LucideIcon } from 'lucide-react';

export type DisasterType = 'Wildfire' | 'Flood' | 'Earthquake' | 'Tornado' | 'Volcano' | 'fire' | 'flood' | 'medical' | 'other';

export interface Alert {
  id: string;
  urgency: number; // 0-10
  disaster_type: DisasterType;
  location: {
    lat: number;
    lng: number;
  };
  summary: string;
  timestamp: string;
  confidence: number; // 0.0-1.0
  message?: string;
  analysis?: any;
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
