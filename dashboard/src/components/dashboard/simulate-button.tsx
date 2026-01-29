'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Bot, Loader2, Play } from 'lucide-react';

const postDemoAlert = async (alertData: { message: string; location: string; lat: number; lng: number }) => {
  const response = await fetch('http://localhost:8000/report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(alertData),
  });

  if (!response.ok) {
    throw new Error('Failed to send demo alert');
  }

  return response.json();
};

const demoAlerts = [
  {
    message: "Pi ochopo e dhoot e Homa Bay, nyumba dhi mar chike, wathe dhi ng'ato",
    location: "Homa Bay, Kenya",
    lat: -0.5167,
    lng: 34.4833,
    delay: 0
  },
  {
    message: "Mvua imepiga Wendani bypass ni river, magari hayawezikupita, tunahitaji rescue",
    location: "Kahawa Wendani, Kenya", 
    lat: -1.2167,
    lng: 36.9333,
    delay: 3000
  },
  {
    message: "Industrial fire at Thika Super Highway, factory workers trapped, smoke covering entire area",
    location: "Thika, Kenya",
    lat: -1.0393,
    lng: 37.0715,
    delay: 6000
  }
];

export default function SimulateButton() {
  const [isDemoMode, setIsDemoMode] = useState(false);
  
  const mutation = useMutation({
    mutationFn: postDemoAlert,
    onSuccess: () => {
      console.log('Demo alert sent successfully');
    },
    onError: (error) => {
      console.error('Failed to send demo alert:', error);
    },
  });

  const handleDemoMode = async () => {
    if (isDemoMode) return;
    
    setIsDemoMode(true);
    
    // Send each demo alert with specified delays
    for (const alert of demoAlerts) {
      setTimeout(() => {
        mutation.mutate(alert);
      }, alert.delay);
    }
    
    // Reset demo mode after all alerts are sent
    setTimeout(() => {
      setIsDemoMode(false);
    }, 10000);
  };

  return (
    <button
      onClick={handleDemoMode}
      disabled={isDemoMode || mutation.isPending}
      className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full glass-morphism border border-zinc-700 text-growth-green shadow-2xl transition-all hover:scale-110 hover:border-growth-green/50 active:scale-100"
      title="Demo Mode: 3-Alert Sequence"
    >
      {isDemoMode || mutation.isPending ? (
        <Loader2 className="h-8 w-8 animate-spin" />
      ) : (
        <Play className="h-8 w-8" />
      )}
    </button>
  );
}
