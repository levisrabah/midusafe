'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { ToastNotification } from '@/hooks/use-alerts';

interface ToastProps {
  toast: ToastNotification;
  onRemove: (id: string) => void;
}

function Toast({ toast, onRemove }: ToastProps) {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-emerald-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-rose-400" />;
      default:
        return <Info className="h-5 w-5 text-blue-400" />;
    }
  };

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success':
        return 'border-emerald-500/50';
      case 'error':
        return 'border-rose-500/50';
      default:
        return 'border-blue-500/50';
    }
  };

  const getLanguageBadge = () => {
    const langMap = {
      'english': '�� EN',
      'swahili': '🇰🇪 SW',
      'sheng': '🇰🇪 SH',
      'dholuo': '🇰🇪 LUO',
      'kalenjin': '🇰🇪 KAL',
      'gikuyu': '🇰🇪 KIK',
      'luhya': '🇰🇪 LUH',
      'somali': '🇸🇴 SOM',
      'french': '🇫🇷 FR',
      'arabic': '🇸🇦 AR'
    };
    
    // Handle native dialect labels
    if (toast.detectedLanguageLabel && toast.detectedLanguageLabel.includes('Native:')) {
      const dialectName = toast.detectedLanguageLabel.replace('Native: ', '').substring(0, 3).toUpperCase();
      return `🇰🇪 ${dialectName}`;
    }
    
    return langMap[toast.detectedLanguage as keyof typeof langMap] || `� ${toast.detectedLanguageLabel?.substring(0, 3).toUpperCase() || toast.detectedLanguage?.substring(0, 3).toUpperCase()}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.3 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.5, transition: { duration: 0.2 } }}
      className={`
        glass-card border-l-4 ${getBorderColor()} 
        p-4 mb-2 max-w-lg shadow-lg
      `}
    >
      <div className="flex items-start gap-3">
        {getIcon()}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-zinc-400 bg-zinc-800 px-2 py-1 rounded">
              {getLanguageBadge()}
            </span>
          </div>
          <p className="text-sm text-zinc-200 font-medium mb-1">
            {toast.translatedSummary || toast.message}
          </p>
          {toast.originalText && toast.originalText !== toast.translatedSummary && (
            <p className="text-xs text-zinc-400 italic mt-1">
              "{toast.originalText}"
            </p>
          )}
        </div>
        <button
          onClick={() => onRemove(toast.id)}
          className="text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </motion.div>
  );
}

interface ToastContainerProps {
  toasts: ToastNotification[];
  onRemove: (id: string) => void;
}

export default function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-[100] space-y-2">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </AnimatePresence>
    </div>
  );
}
