"""
TESS API Router - REST Endpoints
Phase 1: Text-based chat and concept explanations
Phase 2: Voice I/O (WebSocket)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.database.session import get_db
from app.database.models import TESSConversation, TESSAnalytics, User
from app.auth.dependencies import get_current_user
from app.modules.tess.chat_service import get_chat_service, TESSChatService
from app.modules.tess.voice_websocket import handle_voice_websocket

logger = logging.getLogger(__name__)

# ============ PYDANTIC SCHEMAS ============

class TESSChatRequest(BaseModel):
    """Text chat request"""
    message: str
    mode: str = "mentor"  # mentor, interviewer, coach
    session_id: Optional[str] = None
    language: str = "English"


class TESSChatResponse(BaseModel):
    """Chat response"""
    response: str
    mode: str
    session_id: str
    timestamp: str
    success: bool


class TESSExplainRequest(BaseModel):
    """Concept explanation request"""
    concept: str
    depth: str = "beginner"  # beginner, intermediate, advanced
    examples: int = 2


class TESSExplainResponse(BaseModel):
    """Concept explanation response"""
    concept: str
    explanation: str
    depth: str
    success: bool


# ============ ROUTER ============

router = APIRouter(
    prefix="/tess",
    tags=["tess"],
    responses={404: {"description": "Not found"}}
)


# ============ TEXT CHAT ENDPOINTS ============

@router.post("/chat", response_model=TESSChatResponse)
async def text_chat(
    request: TESSChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send text message to TESS
    
    Modes:
    - **mentor**: Explaining concepts, answering questions
    - **interviewer**: Conducting mock interviews
    - **coach**: Career coaching and feedback
    
    Example:
    ```json
    {
        "message": "Explain binary search tree insertion",
        "mode": "mentor",
        "session_id": "session_123"
    }
    ```
    """
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{current_user.id}_{int(datetime.now().timestamp())}"
        
        # Get chat service
        chat_service: TESSChatService = get_chat_service()
        
        # Get response
        logger.info(f"👤 User {current_user.id} ({request.language}) → TESS: {request.message[:50]}...")
        
        # Load the LAST 4 previous messages for short-term conversation memory
        history = db.query(TESSConversation).filter(
            TESSConversation.session_id == session_id,
            TESSConversation.user_id == current_user.id
        ).order_by(TESSConversation.created_at.desc()).limit(4).all()
        
        # Reverse to get chronological order (oldest -> newest of the subset)
        history = history[::-1]
        
        previous_messages_list = []
        for h in history:
            previous_messages_list.append(f"User: {h.user_message}")
            previous_messages_list.append(f"TESS: {h.ai_response}")
        
        context = {
            "language": request.language,
            "previous_messages": previous_messages_list
        }
        
        ai_response = await chat_service.chat(
            user_message=request.message,
            user_id=current_user.id,
            session_id=session_id,
            mode=request.mode,
            context=context
        )
        
        # Save to database
        if ai_response["success"]:
            conversation = TESSConversation(
                user_id=current_user.id,
                session_id=session_id,
                user_message=request.message,
                ai_response=ai_response["response"],
                mode=request.mode,
                response_time_ms=ai_response.get("response_time_seconds", 0) * 1000
            )
            db.add(conversation)
            
            # Update user analytics
            analytics = db.query(TESSAnalytics).filter_by(user_id=current_user.id).first()
            if analytics:
                analytics.total_conversations += 1
            else:
                analytics = TESSAnalytics(user_id=current_user.id, total_conversations=1)
                db.add(analytics)
            
            db.commit()
            logger.info(f"✅ Conversation saved (ID: {conversation.id})")
        
        return TESSChatResponse(
            response=ai_response["response"],
            mode=request.mode,
            session_id=session_id,
            timestamp=ai_response["timestamp"],
            success=ai_response["success"]
        )
    
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=TESSExplainResponse)
async def explain_concept(
    request: TESSExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation of a concept
    
    Example:
    ```json
    {
        "concept": "Binary Search Tree",
        "depth": "intermediate",
        "examples": 2
    }
    ```
    """
    
    try:
        chat_service: TESSChatService = get_chat_service()
        
        logger.info(f"📚 User {current_user.id} requested explanation: {request.concept}")
        
        result = await chat_service.get_explanation(
            concept=request.concept,
            depth=request.depth,
            examples=request.examples
        )
        
        return TESSExplainResponse(
            concept=result["concept"],
            explanation=result.get("explanation", ""),
            depth=request.depth,
            success=result["success"]
        )
    
    except Exception as e:
        logger.error(f"❌ Explain error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ HISTORY & SESSION ENDPOINTS ============

@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a session
    
    Returns last N conversations in the session
    """
    
    try:
        conversations = db.query(TESSConversation).filter(
            TESSConversation.user_id == current_user.id,
            TESSConversation.session_id == session_id
        ).order_by(TESSConversation.created_at.desc()).limit(limit).all()
        
        return {
            "session_id": session_id,
            "conversation_count": len(conversations),
            "conversations": [{
                "user_message": c.user_message,
                "ai_response": c.ai_response,
                "mode": c.mode,
                "timestamp": c.created_at.isoformat(),
                "response_time_ms": c.response_time_ms
            } for c in reversed(conversations)]
        }
    
    except Exception as e:
        logger.error(f"❌ History error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's TESS analytics dashboard
    
    Returns:
    - Total conversations, learning time
    - Concept mastery levels
    - Weak/strong topics
    - Personalized recommendations
    """
    
    try:
        analytics = db.query(TESSAnalytics).filter_by(user_id=current_user.id).first()
        
        if not analytics:
            analytics = TESSAnalytics(user_id=current_user.id)
            db.add(analytics)
            db.commit()
        
        return {
            "user_id": current_user.id,
            "total_conversations": analytics.total_conversations,
            "mock_interviews_completed": analytics.mock_interviews_completed,
            "total_learning_time_hours": analytics.total_learning_time_hours,
            "weak_topics": analytics.weak_topics,
            "strong_topics": analytics.strong_topics,
            "recommended_practice": analytics.recommended_practice,
            "badges": analytics.badges
        }
    
    except Exception as e:
        logger.error(f"❌ Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ HEALTH & STATUS ============

@router.get("/health")
async def tess_health():
    """Check TESS service health"""
    
    try:
        chat_service = get_chat_service()
        
        status = {
            "status": "healthy",
            "llm_providers": {
                "groq": chat_service.groq_available,
                "nvidia": chat_service.nvidia_available,
                "openrouter": chat_service.openrouter_available
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure at least one provider is available
        if not any(status["llm_providers"].values()):
            status["status"] = "unhealthy"
        
        return status
    
    except Exception as e:
        logger.error(f"❌ Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/feedback/{conversation_id}")
async def save_feedback(
    conversation_id: int,
    feedback: str = Query(..., pattern="^(helpful|not_helpful|skip)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save user feedback on a conversation
    Helps improve future responses
    """
    
    try:
        conversation = db.query(TESSConversation).filter(
            TESSConversation.id == conversation_id,
            TESSConversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.user_feedback = feedback
        db.commit()
        
        logger.info(f"💬 Feedback saved: {feedback} for conversation {conversation_id}")
        
        return {
            "success": True,
            "message": "Feedback saved, thanks for improving TESS!"
        }
    
    except Exception as e:
        logger.error(f"❌ Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ WEBSOCKET - VOICE I/O ============

@router.websocket("/ws/voice/{user_id}/{session_id}")
async def websocket_voice_endpoint(
    websocket: WebSocket,
    user_id: int,
    session_id: str,
    mode: str = "mentor"
):
    """
    WebSocket endpoint for real-time voice conversations with TESS
    
    **Features:**
    - Real-time speech-to-text (transcription)
    - AI response generation
    - Real-time text-to-speech (voice synthesis)
    - Bidirectional audio streaming
    
    **Client Protocol:**
    ```
    Connect: ws://localhost:8000/api/v1/tess/ws/voice/{user_id}/{session_id}?mode=mentor
    
    Send Message:
    {
        "type": "audio",
        "data": "<base64_encoded_wav_audio>",
        "format": "wav"
    }
    
    Change Mode:
    {
        "type": "mode",
        "mode": "mentor|interviewer|coach"
    }
    
    Keep Alive:
    {
        "type": "ping"
    }
    
    Receive Responses:
    {
        "type": "status",
        "status": "transcribing|thinking|generating_voice|ready|error",
        "timestamp": "2026-03-31T..."
    }
    {
        "type": "text",
        "text": "**You said:** ... **TESS:** ...",
        "timestamp": "2026-03-31T..."
    }
    {
        "type": "audio",
        "audio": "<base64_encoded_wav_response>",
        "length": 24000
    }
    ```
    
    **Example (JavaScript):**
    ```javascript
    const ws = new WebSocket(
        'ws://localhost:8000/api/v1/tess/ws/voice/1/session_123?mode=mentor'
    );
    
    // Listen for messages
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'text') {
            console.log(msg.text);
        } else if (msg.type === 'audio') {
            const audio = new Audio(
                'data:audio/wav;base64,' + msg.audio
            );
            audio.play();
        }
    };
    
    // Send audio
    mediaRecorder.ondataavailable = (e) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            ws.send(JSON.stringify({
                type: 'audio',
                data: base64,
                format: 'wav'
            }));
        };
        reader.readAsDataURL(e.data);
    };
    ```
    """
    
    await handle_voice_websocket(websocket, user_id, session_id, mode)
