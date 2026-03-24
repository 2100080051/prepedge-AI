import { useEffect, useRef, useState, useCallback } from 'react';
import { AlertTriangle, Video, AlertCircle, CheckCircle, StopCircle } from 'lucide-react';
import { mockMateApi } from '@/lib/api';

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
        const response = await mockMateApi.post(
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
      mockMateApi.post(`/proctoring/track-event/${sessionId}`, {
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
        mockMateApi.post(`/proctoring/track-event/${sessionId}`, {
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
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col">
      {/* Header */}
      <div className="bg-slate-950 border-b border-slate-700 px-6 py-4">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <Video className="w-6 h-6 text-red-500 animate-pulse" />
            <div>
              <h1 className="text-white font-bold text-xl">Proctoring Active</h1>
              <p className="text-slate-400 text-sm">
                {isMonitoring ? 'Monitoring in progress...' : 'Monitoring paused'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-white">{totalViolations}</div>
              <div className="text-xs text-slate-400">Total Violations</div>
            </div>
            <div className="w-0.5 h-12 bg-slate-600"></div>
            <div className="text-right">
              <div className="text-2xl font-bold text-white">{frameCount}</div>
              <div className="text-xs text-slate-400">Frames Analyzed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-6 p-6 max-w-7xl mx-auto w-full">
        {/* Video Feed Section */}
        <div className="flex-1 flex flex-col gap-4">
          <div className="bg-slate-700 rounded-lg overflow-hidden border-2 border-slate-600 h-full flex flex-col">
            {cameraPermission === 'granted' ? (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover bg-black"
                />
                <canvas ref={canvasRef} className="hidden" />
              </>
            ) : cameraPermission === 'denied' ? (
              <div className="flex items-center justify-center h-full bg-gradient-to-br from-red-900 to-red-950">
                <div className="text-center">
                  <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                  <h2 className="text-white font-bold text-xl mb-2">Camera Access Denied</h2>
                  <p className="text-red-200">
                    Please enable camera access to continue with proctoring
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full bg-gradient-to-br from-slate-800 to-slate-900">
                <div className="text-center">
                  <Video className="w-12 h-12 text-slate-500 mx-auto mb-3 animate-spin" />
                  <p className="text-slate-400">Initializing camera...</p>
                </div>
              </div>
            )}
          </div>

          {/* Monitoring Status */}
          <div className="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {isMonitoring ? (
                  <>
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-400 font-semibold">Monitoring Active</span>
                  </>
                ) : (
                  <>
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span className="text-red-400 font-semibold">Monitoring Paused</span>
                  </>
                )}
              </div>
              <button
                onClick={() => setIsMonitoring(!isMonitoring)}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  isMonitoring
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {isMonitoring ? <StopCircle className="w-4 h-4 inline mr-2" /> : null}
                {isMonitoring ? 'Pause' : 'Resume'}
              </button>
            </div>
          </div>
        </div>

        {/* Violations Panel */}
        <div className="w-80 flex flex-col gap-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-3">
              <div className="text-xs text-red-300 mb-1">Critical</div>
              <div className="text-2xl font-bold text-red-400">
                {violations.filter(v => v.severity === 'critical').length}
              </div>
            </div>
            <div className="bg-orange-900/30 border border-orange-700 rounded-lg p-3">
              <div className="text-xs text-orange-300 mb-1">High</div>
              <div className="text-2xl font-bold text-orange-400">
                {violations.filter(v => v.severity === 'high').length}
              </div>
            </div>
            <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
              <div className="text-xs text-yellow-300 mb-1">Medium</div>
              <div className="text-2xl font-bold text-yellow-400">
                {violations.filter(v => v.severity === 'medium').length}
              </div>
            </div>
            <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3">
              <div className="text-xs text-blue-300 mb-1">Low</div>
              <div className="text-2xl font-bold text-blue-400">
                {violations.filter(v => v.severity === 'low').length}
              </div>
            </div>
          </div>

          {/* Violations List */}
          <div className="bg-slate-700 rounded-lg border border-slate-600 flex-1 flex flex-col overflow-hidden">
            <div className="bg-slate-800 px-4 py-3 border-b border-slate-600">
              <h3 className="text-white font-bold text-sm">Recent Violations</h3>
            </div>
            <div className="flex-1 overflow-y-auto">
              {violations.length === 0 ? (
                <div className="flex items-center justify-center h-full text-slate-400 p-4">
                  <div className="text-center">
                    <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No violations detected</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2 p-3">
                  {violations
                    .slice()
                    .reverse()
                    .slice(0, 10)
                    .map((violation, idx) => (
                      <div
                        key={idx}
                        className={`border rounded p-2 text-xs ${getSeverityColor(violation.severity)}`}
                      >
                        <div className="flex items-start gap-2">
                          {getSeverityIcon(violation.severity)}
                          <div className="flex-1">
                            <div className="font-semibold capitalize">
                              {violation.type.replace(/_/g, ' ')}
                            </div>
                            <div className="text-xs mt-1 opacity-90">
                              {violation.description}
                            </div>
                            <div className="text-xs mt-1 opacity-75">
                              {violation.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>

          {/* Auto-flag Alert */}
          {totalViolations >= 5 && (
            <div className="bg-red-900/50 border border-red-600 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-red-200">
                  <strong>Warning:</strong> Multiple violations detected. 
                  Session may be flagged for review.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="bg-slate-950 border-t border-slate-700 px-6 py-3 text-xs text-slate-400">
        <p>
          ⚠️ This interview is being proctored. Any suspicious activity may result in disqualification. 
          {lastViolationTime && ` Last violation: ${lastViolationTime.toLocaleTimeString()}`}
        </p>
      </div>
    </div>
  );
}
