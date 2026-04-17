"""
TESS (The Educational Support System) - AI Mentor Module
Real-time voice-driven interview preparation and learning platform

Features:
- Conversational AI mentoring (text & voice)
- Mock interviews with auto-scoring
- Concept explanations with examples
- Performance analytics and recommendations
- Cost: $0/month (free LLMs + local voice models)
"""

from app.modules.tess.chat_service import TESSChatService, get_chat_service

try:
    from app.modules.tess.voice_service import TESSVoiceService, get_voice_service
    VOICE_SERVICE_AVAILABLE = True
except ImportError:
    VOICE_SERVICE_AVAILABLE = False
    TESSVoiceService = None
    get_voice_service = None

from app.modules.tess.router import router

__all__ = [
    "TESSChatService",
    "get_chat_service",
    "TESSVoiceService",
    "get_voice_service",
    "router"
]
