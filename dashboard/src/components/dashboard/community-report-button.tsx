'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Mic, MapPin, X, Send, Pause, Square, MessageCircle } from 'lucide-react';

export default function CommunityReportButton() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reportText, setReportText] = useState('');
  const [location, setLocation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [transcript, setTranscript] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Voice recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        transcribeAudio(audioBlob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check your permissions.');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setIsPaused(false);
      
      // Stop timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };
  
  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };
  
  const resumeRecording = () => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
  };
  
  const transcribeAudio = async (audioBlob: Blob) => {
    // For now, we'll use a placeholder transcription
    // In a real implementation, you'd send this to a speech-to-text service
    setTranscript("Voice transcription would appear here. This is a placeholder for the actual speech-to-text functionality.");
    setReportText("Voice transcription would appear here. This is a placeholder for the actual speech-to-text functionality.");
  };
  
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportText.trim()) return;

    setIsSubmitting(true);
    
    try {
      // Sentinel path: Meta AI extraction, validation, storage, live broadcast.
      const response = await fetch('http://localhost:8000/api/sentinel/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: reportText,
          location_hint: location || null,
          is_simulated: false,
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

                {/* Voice Recording */}
                <div className="bg-zinc-900/30 border border-zinc-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-medium text-zinc-300">
                      Voice Recording 🎤
                    </label>
                    {isRecording && (
                      <span className="text-xs font-mono text-emergency-red">
                        {formatTime(recordingTime)}
                      </span>
                    )}
                  </div>
                  
                  {!isRecording && !audioBlob && (
                    <button
                      type="button"
                      onClick={startRecording}
                      className="w-full py-3 bg-emergency-red hover:bg-red-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <Mic className="h-5 w-5" />
                      <span>Start Recording</span>
                    </button>
                  )}
                  
                  {isRecording && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-center gap-2">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-emergency-red rounded-full animate-pulse" />
                          <span className="text-sm text-zinc-300">
                            {isPaused ? 'Paused' : 'Recording...'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {!isPaused ? (
                          <button
                            type="button"
                            onClick={pauseRecording}
                            className="flex-1 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                          >
                            <Pause className="h-4 w-4" />
                            <span>Pause</span>
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={resumeRecording}
                            className="flex-1 py-2 bg-emergency-red hover:bg-red-600 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                          >
                            <Mic className="h-4 w-4" />
                            <span>Resume</span>
                          </button>
                        )}
                        
                        <button
                          type="button"
                          onClick={stopRecording}
                          className="flex-1 py-2 bg-zinc-600 hover:bg-zinc-700 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                          <Square className="h-4 w-4" />
                          <span>Stop</span>
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {audioBlob && (
                    <div className="space-y-3">
                      <div className="bg-zinc-800/50 rounded-lg p-3">
                        <p className="text-xs text-zinc-400 mb-1">Transcription:</p>
                        <p className="text-sm text-zinc-200">{transcript}</p>
                      </div>
                      
                      <button
                        type="button"
                        onClick={() => {
                          setAudioBlob(null);
                          setTranscript('');
                          setRecordingTime(0);
                        }}
                        className="w-full py-2 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg transition-colors"
                      >
                        Record Again
                      </button>
                    </div>
                  )}
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
