'use client';

import { useState, useCallback, useEffect } from 'react';
import { Alert } from '@/types/alert';

interface ToastNotification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [toasts, setToasts] = useState<ToastNotification[]>([]);
  const [systemStatus, setSystemStatus] = useState({
    aiBackend: 'Connected' as 'Connected' | 'Disconnected',
    liveFeed: 'Active' as 'Active' | 'Inactive',
  });

  const addAlert = useCallback((alert: Alert) => {
    setAlerts(prev => [alert, ...prev]);
    
    // Show toast notification for new alert
    const toast: ToastNotification = {
      id: `toast-${alert.id}`,
      message: `🚨 New Alert: ${alert.disaster_type} - ${alert.summary}`,
      type: 'info',
      duration: 5000,
    };
    
    setToasts(prev => [...prev, toast]);
    
    // Auto-remove toast after duration
    if (toast.duration) {
      setTimeout(() => {
        removeToast(toast.id);
      }, toast.duration);
    }
  }, []);

  const removeToast = useCallback((toastId: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== toastId));
  }, []);

  const selectAlert = useCallback((alert: Alert) => {
    setSelectedAlert(alert);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
    setSelectedAlert(null);
  }, []);

  const checkSystemStatus = useCallback(async () => {
    try {
      // Check backend health
      const response = await fetch('http://localhost:8000/alerts');
      if (response.ok) {
        setSystemStatus(prev => ({ ...prev, aiBackend: 'Connected' }));
      } else {
        setSystemStatus(prev => ({ ...prev, aiBackend: 'Disconnected' }));
      }
    } catch (error) {
      setSystemStatus(prev => ({ ...prev, aiBackend: 'Disconnected' }));
    }
  }, []);

  // Check system status on mount and periodically
  useEffect(() => {
    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  // Update live feed status based on alerts
  useEffect(() => {
    setSystemStatus(prev => ({ 
      ...prev, 
      liveFeed: alerts.length > 0 ? 'Active' : 'Inactive' 
    }));
  }, [alerts]);

  return {
    alerts,
    selectedAlert,
    toasts,
    systemStatus,
    addAlert,
    selectAlert,
    clearAlerts,
    removeToast,
    checkSystemStatus,
  };
}
