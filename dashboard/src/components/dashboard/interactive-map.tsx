'use client';

import { useMemo, useRef, useEffect } from 'react';
import { Map, Layer, Source, useMap } from 'react-map-gl/mapbox';
import type { LayerProps } from 'react-map-gl/mapbox';
import { Alert } from '@/types/alert';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

// Auto-pan component for new alerts
function MapAutoPan({ alerts }: { alerts: Alert[] }) {
  const map = useMap();
  const latestAlertRef = useRef<Alert | null>(null);

  useEffect(() => {
    if (alerts.length > 0 && map?.current) {
      const latestAlert = alerts[0]; // Assuming alerts are sorted by timestamp (newest first)
      
      // Only pan if this is a genuinely new alert
      if (!latestAlertRef.current || latestAlertRef.current.id !== latestAlert.id) {
        latestAlertRef.current = latestAlert;
        
        // Smooth flyTo to the new alert location
        map.current.flyTo({
          center: [latestAlert.location.lng, latestAlert.location.lat],
          zoom: 10,
          duration: 2000,
          essential: true
        });
      }
    }
  }, [alerts, map]);

  return null;
}

const heatmapLayer: LayerProps = {
  id: 'heatmap',
  type: 'heatmap',
  maxzoom: 9,
  paint: {
    'heatmap-weight': [
      'interpolate',
      ['linear'],
      ['get', 'urgency'],
      0,
      0,
      100,
      1,
    ],
    'heatmap-intensity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      0,
      1,
      9,
      3,
    ],
    'heatmap-color': [
      'interpolate',
      ['linear'],
      ['heatmap-density'],
      0,
      'rgba(0, 242, 143, 0)',
      0.2,
      'rgb(0, 242, 143)',
      0.4,
      'rgb(255, 193, 7)',
      0.6,
      'rgb(255, 77, 77)',
      1,
      'rgb(255, 77, 77)',
    ],
    'heatmap-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      0,
      2,
      9,
      20,
    ],
    'heatmap-opacity': [
      'interpolate',
      ['linear'],
      ['zoom'],
      7,
      1,
      9,
      0,
    ],
  },
};

export default function InteractiveMap({
  alerts,
}: {
  alerts: Alert[];
}) {
  // ✅ Always call hooks first
  const geojsonData = useMemo(
    () => ({
      type: 'FeatureCollection' as const,
      features: alerts.map((alert) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [
            alert.location.lng,
            alert.location.lat,
          ],
        },
        properties: {
          urgency: alert.urgency,
        },
      })),
    }),
    [alerts]
  );

  // ✅ Conditional rendering AFTER hooks
  if (!MAPBOX_TOKEN) {
    return (
      <div className="flex h-full w-full items-center justify-center text-sm text-red-500">
        Mapbox access token is not configured.
      </div>
    );
  }

  return (
    <Map
      initialViewState={{
        longitude: 37.0, // Center on Africa
        latitude: 0.0,
        zoom: 3.5,
      }}
      style={{ width: '100%', height: '100%' }}
      mapStyle="mapbox://styles/mapbox/dark-v11"
      mapboxAccessToken={MAPBOX_TOKEN}
    >
      <Source type="geojson" data={geojsonData}>
        <Layer {...heatmapLayer} />
      </Source>
      <MapAutoPan alerts={alerts} />
    </Map>
  );
}
