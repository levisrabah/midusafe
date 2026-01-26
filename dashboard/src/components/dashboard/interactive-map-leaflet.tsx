'use client';

import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import L from 'leaflet';
import { Alert } from '@/types/alert';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom emergency marker icon
const emergencyIcon = L.divIcon({
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

// Component to handle map auto-pan
function MapController({ alerts }: { alerts: Alert[] }) {
  const map = useMap();
  
  useEffect(() => {
    if (alerts.length > 0) {
      const latestAlert = alerts[0];
      if (latestAlert.location?.lat && latestAlert.location?.lng) {
        map.setView([latestAlert.location.lat, latestAlert.location.lng], 10, {
          animate: true,
          duration: 1.5,
        });
      }
    }
  }, [alerts, map]);
  
  return null;
}

export default function InteractiveMapLeaflet({ alerts }: { alerts: Alert[] }) {
  const mapRef = useRef<L.Map>(null);

  return (
    <>
      <style jsx global>{`
        .emergency-marker {
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
      `}</style>
      
      <div className="h-full w-full rounded-lg overflow-hidden border border-zinc-800">
        <MapContainer
          ref={mapRef}
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
                  icon={emergencyIcon}
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
