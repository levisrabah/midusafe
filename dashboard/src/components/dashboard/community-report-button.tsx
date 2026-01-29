'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, MapPin, Mic } from 'lucide-react';

export default function CommunityReportButton() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reportText, setReportText] = useState('');
  const [location, setLocation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportText.trim()) return;

    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:8000/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: reportText,
          location: location || 'Unknown Location',
        }),
      });

      if (response.ok) {
        setReportText('');
        setLocation('');
        setIsModalOpen(false);
      } else {
        console.error('Failed to submit report');
      }
    } catch (error) {
      console.error('Error submitting report:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Floating Report Button */}
      <motion.div
        className="fixed bottom-6 right-6 z-[90]"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-emergency-red hover:bg-red-600 text-white rounded-full p-4 shadow-lg border-2 border-zinc-800 transition-all duration-200 group"
        >
          <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
          <span className="absolute -top-2 -right-2 bg-growth-green text-white text-xs rounded-full px-2 py-1 animate-pulse">
            Report
          </span>
        </button>
      </motion.div>

      {/* Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[110] flex items-center justify-center p-4"
            onClick={() => setIsModalOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="glass-card border border-zinc-800 rounded-xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-zinc-200 flex items-center gap-2">
                    <MessageCircle className="h-5 w-5 text-emergency-red" />
                    Report Emergency
                  </h2>
                  <p className="text-sm text-zinc-400 mt-1">
                    Speak in your language - English, Swahili, Sheng, or Dholuo
                  </p>
                </div>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Report Text */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    What's happening? 🗣️
                  </label>
                  <textarea
                    value={reportText}
                    onChange={(e) => setReportText(e.target.value)}
                    placeholder="Speak in your language... (e.g., 'Moto umeteketeza nyumba', 'Kuna floods', 'Pi oguro dala')"
                    className="w-full h-32 p-3 bg-zinc-900/50 border border-zinc-700 rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-emergency-red focus:border-transparent resize-none"
                    required
                  />
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Where is this happening? 📍
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-zinc-500" />
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g., Thika, KU, Kahawa Wendani, Kisumu..."
                      className="w-full pl-10 pr-3 py-3 bg-zinc-900/50 border border-zinc-700 rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-emergency-red focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Voice Note Placeholder */}
                <div className="bg-zinc-900/30 border border-zinc-700 rounded-lg p-4 text-center">
                  <Mic className="h-8 w-8 text-zinc-500 mx-auto mb-2" />
                  <p className="text-sm text-zinc-400">
                    Voice recording coming soon 🎤
                  </p>
                </div>

                {/* Submit Button */}
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 px-4 py-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || !reportText.trim()}
                    className="flex-1 px-4 py-3 bg-emergency-red hover:bg-red-600 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        Send Report
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Language Support Info */}
              <div className="mt-4 pt-4 border-t border-zinc-800">
                <p className="text-xs text-zinc-500 text-center">
                  🇰🇪 Supported: English | Swahili | Sheng | Dholuo
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
