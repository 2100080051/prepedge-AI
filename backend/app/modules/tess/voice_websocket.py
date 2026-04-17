"""
TESS Voice WebSocket Handler
Real-time bidirectional audio streaming for voice conversations
Handles: STT (speech→text), LLM (text→response), TTS (response→speech)
"""

import asyncio
import io
import json
import base64
from datetime import datetime
from typing import Dict, Set, Optional
import logging

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.modules.tess.voice_service import get_voice_service
from app.modules.tess.chat_service import get_chat_service
from app.database.session import SessionLocal
from app.database.models import TESSConversation

logger = logging.getLogger(__name__)


class TESSVoiceConnectionManager:
    """Manage WebSocket connections for voice conversations"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[int, str] = {}  # user_id -> session_id
        self.session_data: Dict[str, Dict] = {}  # session_id -> {mode, messages, etc}
    
    async def connect(self, websocket: WebSocket, user_id: int, session_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_sessions[user_id] = session_id
        
        logger.info(f"✅ Voice connection established: user={user_id}, session={session_id}")
        
        # Initialize session data
        self.session_data[session_id] = {
            "user_id": user_id,
            "mode": "mentor",
            "messages": [],
            "started_at": datetime.now(),
            "audio_chunks_received": 0,
            "responses_generated": 0
        }
    
    def disconnect(self, session_id: str):
        """Close WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_data:
            del self.session_data[session_id]
        
        logger.info(f"❌ Voice connection closed: {session_id}")
    
    async def send_status(self, session_id: str, status: str, details: str = ""):
        """Send status update to client"""
        if session_id not in self.active_connections:
            return
        
        message = {
            "type": "status",
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        try:
            await self.active_connections[session_id].send_json(message)
        except Exception as e:
            logger.error(f"Failed to send status: {e}")
    
    async def send_text_response(self, session_id: str, text: str):
        """Send text response to client"""
        if session_id not in self.active_connections:
            return
        
        message = {
            "type": "text",
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.active_connections[session_id].send_json(message)
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
    
    async def send_audio(self, session_id: str, audio_bytes: bytes):
        """Send audio bytes to client (base64 encoded)"""
        if session_id not in self.active_connections:
            return
        
        # Encode audio as base64 for JSON transmission
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        message = {
            "type": "audio",
            "audio": audio_b64,
            "length": len(audio_bytes),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.active_connections[session_id].send_json(message)
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """Broadcast message to all user's sessions"""
        if user_id in self.user_sessions:
            session_id = self.user_sessions[user_id]
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")


# Global connection manager
manager = TESSVoiceConnectionManager()


class TESSVoiceHandler:
    """Handle voice conversation flow"""
    
    def __init__(self):
        self.voice_service = get_voice_service()
        self.chat_service = get_chat_service()
    
    async def process_voice_message(
        self,
        audio_bytes: bytes,
        session_id: str,
        mode: str = "mentor"
    ) -> Dict:
        """
        Complete voice processing pipeline:
        1. Transcribe audio (STT)
        2. Generate AI response (LLM)
        3. Synthesize speech (TTS)
        
        Returns:
            {
                "user_text": "...",
                "ai_response": "...",
                "audio": b"...",
                "success": True
            }
        """
        
        try:
            # Step 1: Speech-to-Text
            logger.info("🎤 Transcribing audio...")
            await manager.send_status(session_id, "transcribing", "Converting speech to text...")
            
            transcription = await self.voice_service.transcribe_audio(audio_bytes)
            
            if not transcription["success"]:
                logger.error(f"Transcription failed: {transcription.get('error')}")
                return {
                    "success": False,
                    "error": "Could not understand audio, please try again",
                    "user_text": ""
                }
            
            user_text = transcription["text"]
            logger.info(f"✅ Transcribed: {user_text[:50]}...")
            
            # Send transcription to client immediately
            await manager.send_text_response(session_id, f"**You said:** {user_text}")
            
            # Step 2: Get Session Data
            session_data = manager.session_data.get(session_id, {})
            user_id = session_data.get("user_id", 1)
            
            # Step 3: Generate AI Response
            logger.info("🧠 Generating AI response...")
            await manager.send_status(session_id, "thinking", "TESS is thinking...")
            
            ai_response = await self.chat_service.chat(
                user_message=user_text,
                user_id=user_id,
                session_id=session_id,
                mode=mode
            )
            
            if not ai_response["success"]:
                logger.error(f"Chat failed: {ai_response.get('error')}")
                return {
                    "success": False,
                    "error": "Could not generate response",
                }
            
            response_text = ai_response["response"]
            logger.info(f"✅ Response: {response_text[:50]}...")
            
            # Send response text
            await manager.send_text_response(session_id, f"**TESS:** {response_text}")
            
            # Step 4: Text-to-Speech
            logger.info("🔊 Synthesizing speech...")
            await manager.send_status(session_id, "generating_voice", "Creating voice response...")
            
            audio_output = await self.voice_service.synthesize_speech(
                text=response_text,
                speaker_id=0,
                emotion="enthusiastic" if mode == "mentor" else "professional"
            )
            
            if not audio_output:
                logger.warning("TTS returned empty audio, skipping voice")
                audio_output = b""
            
            logger.info(f"✅ Audio generated: {len(audio_output)} bytes")
            
            # Step 5: Save to Database
            try:
                db = SessionLocal()
                conversation = TESSConversation(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=user_text,
                    ai_response=response_text,
                    mode=mode,
                    response_time_ms=ai_response.get("response_time_seconds", 0) * 1000
                )
                db.add(conversation)
                db.commit()
                logger.info(f"✅ Conversation saved")
                db.close()
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")
            
            # Update session stats
            session_data["messages"].append({
                "user": user_text,
                "ai": response_text,
                "timestamp": datetime.now().isoformat()
            })
            session_data["audio_chunks_received"] += 1
            session_data["responses_generated"] += 1
            
            return {
                "success": True,
                "user_text": user_text,
                "ai_response": response_text,
                "audio": audio_output,
                "response_time_seconds": ai_response.get("response_time_seconds", 0)
            }
        
        except Exception as e:
            logger.error(f"❌ Error processing voice: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


async def handle_voice_websocket(
    websocket: WebSocket,
    user_id: int,
    session_id: str,
    mode: str = "mentor"
):
    """
    WebSocket handler for real-time voice conversation
    
    Client Protocol:
    - Send: {"type": "audio", "data": "base64_audio", "format": "wav"}
    - Send: {"type": "mode", "mode": "mentor|interviewer|coach"}
    - Receive: {"type": "status", "status": "..."}
    - Receive: {"type": "text", "text": "..."}
    - Receive: {"type": "audio", "audio": "base64_audio"}
    """
    
    await manager.connect(websocket, user_id, session_id)
    handler = TESSVoiceHandler()
    
    try:
        # Welcome message
        await manager.send_status(
            session_id,
            "connected",
            f"Connected! Ready to chat in {mode} mode. Send audio to begin."
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type", "audio")
            
            # Handle different message types
            if message_type == "audio":
                # Receive and process audio
                try:
                    # Decode base64 audio
                    audio_data = data.get("data", "")
                    if not audio_data:
                        await manager.send_status(session_id, "error", "No audio data received")
                        continue
                    
                    audio_bytes = base64.b64decode(audio_data)
                    logger.info(f"📦 Received audio: {len(audio_bytes)} bytes")
                    
                    # Process voice message
                    result = await handler.process_voice_message(
                        audio_bytes=audio_bytes,
                        session_id=session_id,
                        mode=mode
                    )
                    
                    # Send audio response if available
                    if result.get("audio"):
                        await manager.send_audio(session_id, result["audio"])
                    
                    # Send ready status
                    await manager.send_status(session_id, "ready", "Ready for next message")
                
                except Exception as e:
                    logger.error(f"Audio processing error: {e}")
                    await manager.send_status(session_id, "error", str(e))
            
            elif message_type == "mode":
                # Change conversation mode
                new_mode = data.get("mode", mode)
                if new_mode in ["mentor", "interviewer", "coach"]:
                    mode = new_mode
                    manager.session_data[session_id]["mode"] = mode
                    await manager.send_status(session_id, "mode_changed", f"Switched to {mode} mode")
                    logger.info(f"🔄 Mode changed to: {mode}")
            
            elif message_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
        manager.disconnect(session_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(session_id)
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
