'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Thermometer, Users, TrendingUp, ChevronDown, Globe } from 'lucide-react';

interface UnifiedNavbarProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
}

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'sw', name: 'Swahili', flag: '🇰🇪' },
  { code: 'sh', name: 'Sheng', flag: '🇰🇪' },
  { code: 'luo', name: 'Dholuo', flag: '🇰🇪' },
  { code: 'am', name: 'Amharic', flag: '🇪🇹' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
  { code: 'ar', name: 'Arabic', flag: '��' },
  { code: 'ha', name: 'Hausa', flag: '🇳🇬' },
  { code: 'yo', name: 'Yoruba', flag: '🇳�' },
  { code: 'ig', name: 'Igbo', flag: '�🇬' },
  { code: 'zu', name: 'Zulu', flag: '🇿🇦' },
  { code: 'xh', name: 'Xhosa', flag: '🇿🇦' },
  { code: 'af', name: 'Afrikaans', flag: '��' },
  { code: 'so', name: 'Somali', flag: '🇸🇴' },
  { code: 'ti', name: 'Tigrinya', flag: '�🇷' },
  { code: 'om', name: 'Oromo', flag: '🇪🇹' },
  { code: 'wo', name: 'Wolof', flag: '🇸�' },
];

const climateMetrics = [
  { icon: <Thermometer className="h-4 w-4 text-alert-amber" />, label: 'CO2', value: '422ppm' },
  { icon: <TrendingUp className="h-4 w-4 text-alert-amber" />, label: 'Temp', value: '+1.2°C' },
  { icon: <Users className="h-4 w-4 text-growth-green" />, label: 'Units', value: '1,240' },
];

export default function UnifiedNavbar({ selectedLanguage, onLanguageChange }: UnifiedNavbarProps) {
  const [currentTime, setCurrentTime] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const timeString = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
      });
      setCurrentTime(timeString);
    };

    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const currentLanguage = languages.find(lang => lang.code === selectedLanguage) || languages[0];

  return (
    <motion.div
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 h-16 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800"
    >
      <div className="flex items-center justify-between h-full px-6">
        {/* Left: App Title & Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-zinc-200">MIDUSAFE</h1>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-growth-green animate-pulse" />
              <span className="text-xs font-semibold text-growth-green">System Live</span>
            </div>
          </div>
        </div>

        {/* Center: Climate Metrics Strip (hardcoded demo values, not live data) */}
        <div className="flex items-center gap-6">
          <span className="text-[10px] font-medium text-zinc-500 bg-zinc-800/60 border border-zinc-700/60 px-1.5 py-0.5 rounded" title="These figures are static demo placeholders, not live measurements">
            demo values
          </span>
          {climateMetrics.map((metric) => (
            <div key={metric.label} className="flex items-center gap-2">
              {metric.icon}
              <div className="flex items-baseline gap-1">
                <span className="text-xs text-zinc-400">{metric.label}:</span>
                <span className="text-sm font-bold text-zinc-200">{metric.value}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right: Clock & Language Toggle */}
        <div className="flex items-center gap-4">
          {/* Real-Time Clock */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-zinc-300">{currentTime}</span>
          </div>

          {/* Language Toggle Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
            >
              <Globe className="h-4 w-4 text-zinc-400" />
              <span className="text-sm text-zinc-200">
                {currentLanguage.flag} {currentLanguage.name}
              </span>
              <ChevronDown className={`h-3 w-3 text-zinc-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute top-full right-0 mt-2 w-48 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl z-50"
              >
                <div className="py-1 max-h-64 overflow-y-auto">
                  {languages.map((language) => (
                    <button
                      key={language.code}
                      onClick={() => {
                        onLanguageChange(language.code);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2 text-sm hover:bg-zinc-800 transition-colors ${
                        selectedLanguage === language.code ? 'bg-zinc-800 text-zinc-200' : 'text-zinc-400'
                      }`}
                    >
                      <span className="text-lg">{language.flag}</span>
                      <span>{language.name}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
