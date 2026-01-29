'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { Alert } from '@/types/alert';

// Dynamically import react-leaflet components to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);

const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
);

const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
);

// Create a separate component for the map controller that will be dynamically imported
const MapController: any = dynamic(
  () => import('./map-controller').then((mod: any) => ({ default: mod.default })),
  { ssr: false }
);

export default function InteractiveMapLeaflet({ alerts }: { alerts: Alert[] }) {
  const [isClient, setIsClient] = useState(false);
  const [L, setL] = useState<any>(null);
  const [emergencyIcon, setEmergencyIcon] = useState<any>(null);
  const [locationIcons, setLocationIcons] = useState<any>({});

  const getLocationIcon = (locationName: string, leaflet: any) => {
    const locationKey = locationName.toLowerCase();
    
    // Special icons for specific locations
    if (locationKey.includes('thika')) {
      return leaflet.divIcon({
        html: `<div class="location-marker thika-marker">
          <div class="pulse-ring thika-pulse"></div>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#f97316" stroke="#fff" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" fill="#f97316" stroke="#fff" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" fill="#f97316" stroke="#fff" stroke-width="2"/>
          </svg>
        </div>`,
        className: 'custom-location-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 36],
      });
    }
    
    if (locationKey.includes('kenyatta') || locationKey.includes('ku')) {
      return leaflet.divIcon({
        html: `<div class="location-marker ku-marker">
          <div class="pulse-ring ku-pulse"></div>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" fill="#3b82f6" stroke="#fff" stroke-width="2"/>
          </svg>
        </div>`,
        className: 'custom-location-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 36],
      });
    }
    
    if (locationKey.includes('kahawa') || locationKey.includes('wendani')) {
      return leaflet.divIcon({
        html: `<div class="location-marker kahawa-marker">
          <div class="pulse-ring kahawa-pulse"></div>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#10b981" stroke="#fff" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" fill="#10b981" stroke="#fff" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" fill="#10b981" stroke="#fff" stroke-width="2"/>
          </svg>
        </div>`,
        className: 'custom-location-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 36],
      });
    }
    
    // Default emergency icon
    return emergencyIcon;
  };

  useEffect(() => {
    setIsClient(true);
    
    // Import Leaflet only on client side
    import('leaflet').then((leaflet) => {
      setL(leaflet);
      
      // Fix for default markers in react-leaflet
      delete (leaflet.Icon.Default.prototype as any)._getIconUrl;
      leaflet.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });
      
      // Custom emergency marker icon
      const icon = leaflet.divIcon({
        html: `<div class="emergency-marker">
          <div class="pulse-ring"></div>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#ef4444" stroke="#fff" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" fill="#ef4444" stroke="#fff" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" fill="#ef4444" stroke="#fff" stroke-width="2"/>
          </svg>
        </div>`,
        className: 'custom-emergency-marker',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
      });
      setEmergencyIcon(icon);
    });
  }, []);

  if (!isClient || !L || !emergencyIcon) {
    return (
      <div className="h-full w-full rounded-lg overflow-hidden border border-zinc-800 bg-zinc-950 flex items-center justify-center">
        <div className="text-zinc-400">Loading map...</div>
      </div>
    );
  }

  return (
    <>
      <style jsx global>{`
        .emergency-marker, .location-marker {
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .pulse-ring {
          position: absolute;
          width: 32px;
          height: 32px;
          border: 2px solid #ef4444;
          border-radius: 50%;
          animation: ripple 2s ease-out infinite;
        }
        
        .thika-pulse {
          border-color: #f97316;
        }
        
        .ku-pulse {
          border-color: #3b82f6;
        }
        
        .kahawa-pulse {
          border-color: #10b981;
        }
        
        @keyframes ripple {
          0% {
            transform: scale(0.8);
            opacity: 1;
          }
          100% {
            transform: scale(2);
            opacity: 0;
          }
        }
        
        .leaflet-container {
          background: #09090b;
        }
        
        .leaflet-popup-content-wrapper {
          background: #18181b;
          border: 1px solid #27272a;
          border-radius: 8px;
        }
        
        .leaflet-popup-content {
          color: #fafafa;
          margin: 8px 12px;
        }
        
        .leaflet-popup-tip {
          background: #18181b;
        }
        
        .leaflet-control-attribution {
          display: none !important;
        }
      `}</style>
      
      <div className="h-full w-full rounded-lg overflow-hidden border border-zinc-800">
        <MapContainer
          center={[0, 0]}
          zoom={2}
          style={{ height: '100%', width: '100%' }}
          className="bg-zinc-950"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          <MapController alerts={alerts} />
          
          {alerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ 
                duration: 0.5, 
                delay: index * 0.1,
                type: "spring"
              }}
            >
              {alert.location?.lat && alert.location?.lng && (
                <Marker
                  position={[alert.location.lat, alert.location.lng]}
                  icon={getLocationIcon(alert.message || '', L)}
                >
                  <Popup>
                    <div className="p-2">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="h-4 w-4 text-emergency-red" />
                        <span className="font-semibold">{alert.disaster_type}</span>
                      </div>
                      <p className="text-sm text-zinc-300 mb-2">{alert.summary}</p>
                      <div className="text-xs text-zinc-500">
                        Urgency: {alert.urgency}/10
                      </div>
                    </div>
                  </Popup>
                </Marker>
              )}
            </motion.div>
          ))}
        </MapContainer>
      </div>
    </>
  );
}
