import { useEffect, useRef, useState, useCallback } from 'react';
import { AlertTriangle, Video, AlertCircle, CheckCircle, StopCircle } from 'lucide-react';
import apiClient from '@/lib/api';

interface ProctoringMonitorProps {
  sessionId: number;
  onFlagSession: (reason: string) => void;
  isActive: boolean;
}

interface Violation {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  timestamp: Date;
}

export default function ProctoringMonitor({ 
  sessionId, 
  onFlagSession, 
  isActive 
}: ProctoringMonitorProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [cameraPermission, setCameraPermission] = useState<'pending' | 'granted' | 'denied'>('pending');
  const [frameCount, setFrameCount] = useState(0);
  const [totalViolations, setTotalViolations] = useState(0);
  const [lastViolationTime, setLastViolationTime] = useState<Date | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const eventListenerRef = useRef<boolean>(false);

  // Request camera permission and start video stream
  useEffect(() => {
    const startVideoStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 }
          },
          audio: false
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraPermission('granted');
          startFrameCapture();
        }
      } catch (error) {
        console.error('Camera access denied:', error);
        setCameraPermission('denied');
        onFlagSession('Camera access denied - cannot proceed with proctoring');
      }
    };

    if (isActive) {
      startVideoStream();
    }

    return () => {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
      }
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [isActive, onFlagSession]);

  // Start capturing and analyzing frames
  const startFrameCapture = useCallback(() => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
    }

    frameIntervalRef.current = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current || !isMonitoring) return;

      try {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Draw video frame to canvas
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        ctx.drawImage(videoRef.current, 0, 0);

        // Convert to base64
        const frameData = canvas.toDataURL('image/jpeg', 0.7);

        setFrameCount(prev => prev + 1);

        // Send to backend for analysis
        const response = await apiClient.post(
          `/proctoring/analyze-frame/${sessionId}`,
          { frame_data: frameData }
        );

        if (response.data.violations && response.data.violations.length > 0) {
          const newViolations = response.data.violations.map((v: any) => ({
            type: v.type,
            severity: v.severity,
            description: v.description,
            timestamp: new Date()
          }));

          setViolations(prev => [...prev, ...newViolations].slice(-20)); // Keep last 20
          setTotalViolations(prev => prev + newViolations.length);
          setLastViolationTime(new Date());

          // Auto-flag on critical violations
          if (response.data.max_severity === 'critical') {
            onFlagSession(`Critical violation detected: ${newViolations[0].type}`);
            setIsMonitoring(false);
          }
        }
      } catch (error) {
        console.error('Frame analysis error:', error);
      }
    }, 1000); // Capture every 1 second (adjustable)
  }, [sessionId, isMonitoring, onFlagSession]);

  // Monitor keyboard events for copy/paste
  useEffect(() => {
    if (!eventListenerRef.current && isMonitoring) {
      const handleKeyDown = (e: KeyboardEvent) => {
        const isCopyPaste = 
          (e.ctrlKey || e.metaKey) && 
          ['c', 'x', 'v'].includes(e.key.toLowerCase());

        if (isCopyPaste) {
          addViolation({
            type: 'copy_paste',
            severity: 'critical',
            description: 'Copy/paste action detected',
            timestamp: new Date()
          });
          onFlagSession('Copy/paste detected during interview');
        }
      };

      window.addEventListener('keydown', handleKeyDown);
      eventListenerRef.current = true;

      return () => {
        window.removeEventListener('keydown', handleKeyDown);
        eventListenerRef.current = false;
      };
    }
  }, [isMonitoring, onFlagSession]);

  // Monitor window/tab focus changes
  useEffect(() => {
    if (!isMonitoring) return;

    const handleBlur = () => {
      addViolation({
        type: 'window_unfocus',
        severity: 'medium',
        description: 'Window focus lost - attention diverted',
        timestamp: new Date()
      });
      apiClient.post(`/proctoring/track-event/${sessionId}`, {
        event_type: 'focus_lost'
      });
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        addViolation({
          type: 'tab_switch',
          severity: 'medium',
          description: 'Browser tab switched - possible looking up answers',
          timestamp: new Date()
        });
        apiClient.post(`/proctoring/track-event/${sessionId}`, {
          event_type: 'tab_switch'
        });
      }
    };

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        addViolation({
          type: 'fullscreen_exit',
          severity: 'high',
          description: 'Full-screen mode exited',
          timestamp: new Date()
        });
      }
    };

    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [sessionId, isMonitoring, onFlagSession]);

  // Monitor fullscreen requirement
  useEffect(() => {
    if (!isActive) return;

    const requestFullscreen = async () => {
      try {
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen();
        }
      } catch (error) {
        console.error('Fullscreen request failed:', error);
      }
    };

    // Request fullscreen after a short delay
    const timer = setTimeout(requestFullscreen, 1000);
    return () => clearTimeout(timer);
  }, [isActive]);

  const addViolation = (violation: Violation) => {
    setViolations(prev => [...prev, violation].slice(-20));
    setTotalViolations(prev => prev + 1);
    setLastViolationTime(new Date());
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-400 text-red-800';
      case 'high':
        return 'bg-orange-100 border-orange-400 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-400 text-yellow-800';
      default:
        return 'bg-blue-100 border-blue-400 text-blue-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-4 h-4" />;
      case 'medium':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="fixed bottom-6 lg:bottom-10 lg:right-10 right-6 w-80 bg-slate-900 rounded-2xl shadow-2xl overflow-hidden z-50 flex flex-col border border-slate-700 animate-slide-up">
      {/* Header */}
      <div className="bg-slate-950 px-4 py-3 flex justify-between items-center border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-red-500 animate-pulse' : 'bg-slate-500'}`} />
          <span className="text-white text-xs font-bold tracking-widest uppercase">Proctoring</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs font-bold text-red-400">{totalViolations} <span className="font-normal text-slate-500">flags</span></div>
          </div>
        </div>
      </div>

      {/* Video Feed Section */}
      <div className="h-48 bg-slate-800 relative">
        {cameraPermission === 'granted' ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover scale-x-[-1]"
            />
            <canvas ref={canvasRef} className="hidden" />
          </>
        ) : cameraPermission === 'denied' ? (
          <div className="flex items-center justify-center h-full bg-red-950/50">
            <div className="text-center p-4">
              <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <p className="text-xs text-red-200">Camera Access Denied</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <Video className="w-8 h-8 text-slate-600 animate-pulse" />
          </div>
        )}
        
        {/* Overlay violations briefly */}
        {violations.length > 0 && (
          <div className="absolute bottom-2 left-2 right-2 flex flex-col gap-1 pointer-events-none">
            {violations
              .slice(-2)
              .reverse()
              .map((violation, idx) => (
                <div key={idx} className={`rounded p-1.5 text-[10px] backdrop-blur-md font-medium border shadow-lg flex items-center gap-1.5 ${getSeverityColor(violation.severity).replace('bg-', 'bg-opacity-90 bg-')}`}>
                  {getSeverityIcon(violation.severity)}
                  <span className="truncate">{violation.type.replace(/_/g, ' ')}</span>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Footer Controls */}
      <div className="bg-slate-900 p-3 flex justify-between items-center text-xs">
        <span className="text-slate-400 truncate flex-1 mr-2 opacity-80">
          ⚠️ AI Analysis Active
        </span>
        <button
          onClick={() => setIsMonitoring(!isMonitoring)}
          className={`flex-shrink-0 px-3 py-1.5 rounded-lg font-bold transition-colors border ${
            isMonitoring
              ? 'border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white'
              : 'bg-indigo-600 border-indigo-500 text-white hover:bg-indigo-700'
          }`}
        >
          {isMonitoring ? 'Pause' : 'Resume'}
        </button>
      </div>
    </div>
  );
}
