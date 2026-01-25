import { LucideIcon } from 'lucide-react';

export type DisasterType = 'Wildfire' | 'Flood' | 'Earthquake' | 'Tornado' | 'Volcano';

export interface Alert {
  id: string;
  urgency: number; // 0-100
  disaster_type: DisasterType;
  location: {
    lat: number;
    lng: number;
  };
  summary: string;
  timestamp: string;
}
