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
        // Map the disaster type and ensure proper Alert structure
        const alert: Alert = {
          id: message.id,
          urgency: message.urgency || 5,
          disaster_type: mapDisasterType(message.disaster_type || 'other'),
          location: message.location || { lat: 0, lng: 0 },
          summary: message.summary || 'Emergency report received',
          timestamp: message.timestamp || new Date().toISOString(),
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
