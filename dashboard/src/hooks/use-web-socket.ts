import { useState, useEffect, useRef } from 'react';
import { Alert, mapDisasterType } from '@/types/alert';

export function useWebSocket<T>(url: string) {
  const [data, setData] = useState<Alert[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        // Sentinel incidents have their own feed (REST polling); skip here
        // to avoid null-coordinate shapes in the legacy feed.
        if (message.sentin || message.type === 'sentinel_incident' || message.type === 'sentinel_error') {
          return;
        }
        // Map the disaster type and ensure proper Alert structure
        const alert: Alert = {
          id: message.id,
          urgency: message.urgency || 5,
          disaster_type: mapDisasterType(message.disaster_type || 'other'),
          location: message.location || { lat: 0, lng: 0 },
          summary: message.summary || 'Emergency report received',
          timestamp: message.timestamp || new Date().toISOString(),
          confidence: message.confidence || 0.8,
          message: message.message,
          analysis: message.analysis,
        };
        setData((prevData) => [alert, ...prevData]);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return data;
}
