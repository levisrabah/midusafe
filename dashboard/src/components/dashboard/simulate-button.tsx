'use client';

import { useMutation } from '@tanstack/react-query';
import { Bot, Loader2 } from 'lucide-react';

const postTestDisaster = async () => {
  const response = await fetch('http://localhost:8000/report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ disaster: 'Test Disaster' }),
  });

  if (!response.ok) {
    throw new Error('Failed to report test disaster');
  }

  return response.json();
};

export default function SimulateButton() {
  const mutation = useMutation({
    mutationFn: postTestDisaster,
    onSuccess: () => {
      console.log('Successfully reported test disaster');
    },
    onError: (error) => {
      console.error('Failed to report test disaster:', error);
    },
  });

  return (
    <button
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
      className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full glass-morphism border border-zinc-700 text-emergency-red shadow-2xl transition-all hover:scale-110 hover:border-emergency-red/50 active:scale-100"
    >
      {mutation.isPending ? (
        <Loader2 className="h-8 w-8 animate-spin" />
      ) : (
        <Bot className="h-8 w-8" />
      )}
    </button>
  );
}
