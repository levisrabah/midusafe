'use client';

import { useMemo } from 'react';
import Map, { Layer, Source } from 'react-map-gl';
import type { LayerProps } from 'react-map-gl';
import { Alert } from '@/types/alert';

const MAPBOX_TOKEN =
  process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN ||
  'pk.eyJ1IjoiZXhhbXBsZXMiLCJpZCI6ImNqYWx5b3k2MDB4cGUzM215enIzb25qZ3kifQ.uM4f-2qA1dO2a294F4I2fA'; // Add your Mapbox token here

const heatmapLayer: LayerProps = {
  id: 'heatmap',
  maxzoom: 9,
  type: 'heatmap',
  paint: {
    'heatmap-weight': ['interpolate', ['linear'], ['get', 'urgency'], 0, 0, 100, 1],
    'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 9, 3],
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
    'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 9, 20],
    'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 7, 1, 9, 0],
  },
};

export default function InteractiveMap({ alerts }: { alerts: Alert[] }) {
  const geojsonData = useMemo(() => {
    return {
      type: 'FeatureCollection' as const,
      features: alerts.map((alert) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [alert.location.lng, alert.location.lat],
        },
        properties: {
          urgency: alert.urgency,
        },
      })),
    };
  }, [alerts]);

  return (
    <Map
      initialViewState={{
        longitude: -95.7129,
        latitude: 37.0902,
        zoom: 3.5,
      }}
      style={{ width: '100%', height: '100%' }}
      mapStyle="mapbox://styles/mapbox/dark-v11"
      mapboxAccessToken={MAPBOX_TOKEN}
    >
      <Source type="geojson" data={geojsonData}>
        <Layer {...heatmapLayer} />
      </Source>
    </Map>
  );
}
