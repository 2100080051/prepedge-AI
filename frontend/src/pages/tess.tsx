import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'next/router';
import { tessApi } from '@/lib/api';
import Navbar from '@/components/Navbar';
import { Mic, Send, Globe, BrainCircuit, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';
import RichTextRenderer from '@/components/shared/RichTextRenderer';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

const LANGUAGES = [
  { code: 'en-US', label: 'English' },
  { code: 'hi-IN', label: 'Hindi (हिंदी)' },
  { code: 'te-IN', label: 'Telugu (తెలుగు)' },
  { code: 'ta-IN', label: 'Tamil (தமிழ்)' },
  { code: 'mr-IN', label: 'Marathi (मराठी)' },
];

export default function TESS() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState(LANGUAGES[0]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [handsFree, setHandsFree] = useState(false);

  const [sessionId, setSessionId] = useState<string>('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Auth Guard & Init Session
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/tess');
      return;
    }
    // Generate a unique session ID for this browser tab instance if empty
    if (!sessionId) {
      setSessionId(`sess_${Math.random().toString(36).substring(2, 10)}`);
      // Welcome message
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm TESS, your autonomous internet-connected AI prep mentor. Ask me about **any company, interview trend, or placement query**.",
        timestamp: new Date().toISOString()
      }]);
    }
  }, [isAuthenticated, router, sessionId]);

  // Setup Web Speech API (STT Voice Recognition)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => setIsRecording(true);
        recognition.onend = () => setIsRecording(false);
        recognition.onerror = (event: any) => {
          console.error('Speech recognition error', event.error);
          setIsRecording(false);
        };
        
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          // Automatically send if handsFree mode is ON
          if (handsFree && transcript.trim().length > 0) {
             sendMessage(transcript);
          }
        };
        recognitionRef.current = recognition;
      }
    }
  }, [language, handsFree]);

  // Speak Text Function (TTS)
  const speakText = (text: string) => {
    if (!handsFree || typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    
    // Clean text of markdown asterisks for cleaner speaking
    const cleanText = text.replace(/[*_#`]/g, '');
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = language.code;
    utterance.rate = 1.0;
    utterance.pitch = 1.1; // Slightly higher pitch for "AI" feel
    
    utterance.onstart = () => setIsPlaying(true);
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.speak(utterance);
  };

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.lang = language.code;
        try {
          recognitionRef.current.start();
        } catch(e) {
          console.log("Mic start error", e);
        }
      } else {
        alert("Your browser does not support Voice Recognition.");
      }
    }
  };

  const sendMessage = async (overrideText?: string) => {
    const textToSend = overrideText || input;
    if (!textToSend.trim()) return;

    // Add User Message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // API Call
      const res = await tessApi.chat({
        message: textToSend,
        mode: 'mentor',
        session_id: sessionId,
        language: language.label.split(' ')[0] // e.g. "English", "Hindi"
      });

      if (res.data.success) {
        const aiResponseText = res.data.response;
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: aiResponseText,
          timestamp: res.data.timestamp
        };
        setMessages(prev => [...prev, aiMsg]);
        speakText(aiResponseText);
      }
    } catch (error) {
      console.error("TESS API Error", error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Oops! I encountered a network error connecting to my brain. Please try again.",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>TESS AI - Live Mentor</title>
      </Head>
      <div className="flex flex-col min-h-screen bg-slate-50 text-slate-800">
        <Navbar />
        
        {/* Main Content Area */}
        <main className="flex-1 flex flex-col pt-16 h-[100dvh]">
          {/* Header */}
          <div className="flex-shrink-0 px-4 py-3 border-b border-slate-100 bg-white/80 backdrop-blur z-10 sticky top-[64px] flex justify-between items-center max-w-4xl w-full mx-auto">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-600/20">
                <BrainCircuit className="w-5 h-5 text-white" />
              </div>
              <div className="flex items-baseline gap-2">
                <h1 className="font-bold text-[17px] text-slate-900 leading-none tracking-tight">TESS</h1>
                <span className="bg-emerald-100 text-emerald-700 text-[10px] font-bold px-1.5 py-0.5 rounded-md uppercase tracking-wide">Live</span>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2">
              {/* Language Selector */}
              <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hidden sm:flex hover:bg-slate-100 transition-colors">
                <Globe className="w-3.5 h-3.5 text-slate-500" />
                <select 
                  className="bg-transparent text-xs font-medium text-slate-700 outline-none cursor-pointer"
                  value={language.code}
                  onChange={(e) => setLanguage(LANGUAGES.find(l => l.code === e.target.value) || LANGUAGES[0])}
                >
                  {LANGUAGES.map(lang => (
                    <option key={lang.code} value={lang.code}>{lang.label}</option>
                  ))}
                </select>
              </div>

              {/* Hands free toggle */}
              <button 
                onClick={() => setHandsFree(!handsFree)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-colors ${
                  handsFree 
                    ? 'bg-indigo-50 border-indigo-200 text-indigo-700 font-semibold shadow-sm' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 font-medium'
                }`}
              >
                {handsFree ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
                <span className="text-xs hidden sm:block">Hands-Free Mode</span>
              </button>
            </div>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto px-4 py-8 mb-[120px] scroll-smooth">
            <div className="max-w-4xl mx-auto space-y-8">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center mt-0.5 shadow-sm">
                      <BrainCircuit className="w-4 h-4 text-white" />
                    </div>
                  )}
                  
                  <div className={`relative max-w-[90%] px-6 py-4 rounded-3xl text-base leading-relaxed shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-br-sm' 
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm'
                  }`}>
                    {msg.role === 'assistant' ? (
                      <RichTextRenderer source={msg.content} />
                    ) : (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-4 justify-start max-w-4xl mx-auto animate-fade-in">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center shadow-sm mt-1">
                    <BrainCircuit className="w-4 h-4 text-white animate-pulse" />
                  </div>
                  <div className="bg-white border border-slate-200 px-5 py-3.5 rounded-2xl rounded-tl-sm flex items-center gap-2 shadow-sm">
                    <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />
                    <span className="text-sm font-medium text-slate-500 tracking-wide">Syncing web data...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-white via-white to-transparent pt-12">
            <div className="max-w-4xl mx-auto relative group">
              {/* Hands-Free Warning indicator */}
              {handsFree && isRecording && (
                <div className="absolute -top-10 left-1/2 -translate-x-1/2 text-[11px] font-bold text-red-500 animate-pulse flex items-center gap-2 bg-red-50 px-3 py-1.5 rounded-full border border-red-200 shadow-sm whitespace-nowrap tracking-wide">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div> LISTENING
                </div>
              )}
              
              <div className={`relative flex items-end gap-2 p-2 rounded-2xl border bg-white transition-all duration-300 shadow-lg shadow-slate-200/50 ${
                isRecording 
                  ? 'border-red-400 ring-2 ring-red-100' 
                  : 'border-slate-300 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100'
              }`}>
                {/* Voice Button */}
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`p-3 rounded-xl transition-all flex-shrink-0 outline-none ${
                    isRecording 
                      ? 'bg-red-50 text-red-600 animate-pulse' 
                      : 'bg-slate-50 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50'
                  }`}
                  title="Toggle Voice Input"
                >
                  {isRecording ? <MicOff className="w-[22px] h-[22px]" /> : <Mic className="w-[22px] h-[22px]" />}
                </button>

                {/* Text Input */}
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder={
                    isRecording 
                      ? "Listening via microphone..." 
                      : "Message TESS securely..."
                  }
                  className="flex-1 max-h-40 min-h-[52px] bg-transparent text-slate-800 placeholder-slate-400 resize-none outline-none py-3.5 px-3 leading-relaxed text-[15px]"
                  rows={Math.min(5, input.split('\n').length || 1)}
                  disabled={isLoading}
                />

                {/* Send Button */}
                <button
                  onClick={() => sendMessage()}
                  disabled={!input.trim() || isLoading}
                  className="p-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-100 disabled:text-slate-400 text-white rounded-xl transition-all flex-shrink-0 outline-none"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              
              <div className="text-center mt-3 mb-1 text-[11px] text-slate-400 font-medium">
                TESS can make mistakes. Consider verifying important placement information.
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
