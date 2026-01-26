'use client';

import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import { Alert } from '@/types/alert';
import { useAlerts } from '@/hooks/use-alerts';

export default function MapController({ alerts }: { alerts: Alert[] }) {
  const map = useMap();
  const { selectedAlert } = useAlerts();
  
  // Auto-pan to latest alert
  useEffect(() => {
    if (map && alerts.length > 0) {
      const latestAlert = alerts[0];
      if (latestAlert.location?.lat && latestAlert.location?.lng) {
        map.setView([latestAlert.location.lat, latestAlert.location.lng], 10, {
          animate: true,
          duration: 1.5,
        });
      }
    }
  }, [alerts, map]);
  
  // Fly to selected alert when clicked
  useEffect(() => {
    if (map && selectedAlert && selectedAlert.location?.lat && selectedAlert.location?.lng) {
      map.setView([selectedAlert.location.lat, selectedAlert.location.lng], 12, {
        animate: true,
        duration: 2,
      });
    }
  }, [selectedAlert, map]);
  
  return null;
}
