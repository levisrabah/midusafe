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
      className="fixed bottom-4 right-4 z-10 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-110 active:scale-100"
    >
      {mutation.isPending ? (
        <Loader2 className="h-6 w-6 animate-spin" />
      ) : (
        <Bot className="h-6 w-6" />
      )}
    </button>
  );
}
