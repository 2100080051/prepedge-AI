from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Request
from fastapi.responses import StreamingResponse
import os
from typing import Optional
from app.services.interview_recording import InterviewRecordingService
from app.utils.logger import get_logger, LogCategory

router = APIRouter()
recording_service = InterviewRecordingService()


@router.post("/api/v1/interview/recording/{session_id}/start")
async def start_recording(
    session_id: int,
    user_id: int = Query(...),
    video_codec: Optional[str] = Query("h264"),
    audio_codec: Optional[str] = Query("aac"),
    bitrate: Optional[str] = Query("5000k"),
    resolution: Optional[str] = Query("1080p"),
    fps: Optional[int] = Query(30)
):
    """
    Start recording an interview session
    
    Query Parameters:
    - session_id: Interview session ID (path)
    - user_id: User ID (required)
    - video_codec: Video codec (h264, h265, vp8, vp9) - default: h264
    - audio_codec: Audio codec (aac, opus, vorbis) - default: aac
    - bitrate: Recording bitrate (e.g., 5000k, 10000k) - default: 5000k
    - resolution: Video resolution (720p, 1080p, 2k, 4k) - default: 1080p
    - fps: Frames per second (15, 24, 30, 60) - default: 30
    
    Returns:
    - success: Whether recording started successfully
    - recording_id: Unique recording identifier
    - session_id: Associated interview session
    - upload_url: Endpoint for uploading recording chunks
    - started_at: Timestamp when recording started
    """
    try:
        recording_config = {
            "video_codec": video_codec,
            "audio_codec": audio_codec,
            "bitrate": bitrate,
            "resolution": resolution,
            "fps": fps
        }
        
        result = recording_service.start_recording_session(
            session_id=session_id,
            user_id=user_id,
            recording_config=recording_config
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/interview/recording/{recording_id}/chunk")
async def upload_chunk(
    recording_id: str,
    chunk_index: int = Query(...),
    chunk_duration_ms: int = Query(...),
    user_id: int = Query(...),
    file: UploadFile = File(...)
):
    """
    Upload a chunk of recording data
    Supports incremental upload for streaming/large interviews
    
    Query Parameters:
    - recording_id: Recording ID (path)
    - chunk_index: Sequential index of this chunk (0-based)
    - chunk_duration_ms: Duration of audio/video in this chunk (milliseconds)
    - user_id: User ID (required)
    
    Body:
    - file: WebM/MP4 chunk file
    
    Returns:
    - success: Upload status
    - chunk_index: Which chunk was uploaded
    - total_chunks: Total chunks received so far
    - total_duration_seconds: Cumulative duration
    """
    try:
        # Read chunk data
        chunk_data = await file.read()
        
        result = recording_service.upload_recording_chunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            chunk_data=chunk_data,
            chunk_duration_ms=chunk_duration_ms
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/interview/recording/{recording_id}/stop")
async def stop_recording(
    recording_id: str,
    session_id: int = Query(...),
    user_id: int = Query(...)
):
    """
    Stop recording and finalize the recording file
    Merges all chunks into single playable file
    
    Query Parameters:
    - recording_id: Recording ID (path)
    - session_id: Associated interview session ID
    - user_id: User ID (required)
    
    Returns:
    - success: Whether recording was stopped successfully
    - duration_seconds: Total recording duration
    - file_size_bytes: Size of final recording file
    - file_size_mb: Size in megabytes
    - completed_at: Timestamp when recording completed
    """
    try:
        result = recording_service.stop_recording_session(
            session_id=session_id,
            recording_id=recording_id,
            user_id=user_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/interview/recording/{recording_id}/metadata")
async def get_recording_metadata(
    recording_id: str,
    user_id: int = Query(...)
):
    """
    Get recording metadata and configuration
    
    Query Parameters:
    - recording_id: Recording ID (path)
    - user_id: User ID (required)
    
    Returns:
    - recording_id: The recording ID
    - metadata: Recording configuration, chunks, duration, status, etc.
    """
    try:
        result = recording_service.get_recording_metadata(
            recording_id=recording_id,
            user_id=user_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/interview/recording/{recording_id}/playback")
async def playback_recording(
    recording_id: str,
    user_id: int = Query(...),
    start_byte: int = Query(0, ge=0),
    request: Request = None
):
    """
    Stream recording file for playback
    Supports range requests for browser compatibility and seeking
    
    Query Parameters:
    - recording_id: Recording ID (path)
    - user_id: User ID (required)
    - start_byte: Starting byte position for range requests (default: 0)
    
    Returns:
    - Streaming response with video/webm content
    """
    try:
        result = recording_service.get_recording_stream(
            recording_id=recording_id,
            user_id=user_id,
            start_byte=start_byte
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        recording_file = result.get("file_path")
        file_size = result.get("file_size_bytes")
        
        if not os.path.exists(recording_file):
            raise HTTPException(status_code=404, detail="Recording file not found")
        
        def file_iterator(chunk_size=1024 * 1024):  # 1MB chunks
            with open(recording_file, "rb") as f:
                f.seek(start_byte)
                remaining = file_size - start_byte
                while remaining > 0:
                    chunk_size_to_read = min(chunk_size, remaining)
                    data = f.read(chunk_size_to_read)
                    if not data:
                        break
                    yield data
                    remaining -= len(data)
        
        get_logger().log_action(
            LogCategory.INTERVIEW,
            "recording_playback",
            user_id=user_id,
            details={"recording_id": recording_id}
        )
        
        return StreamingResponse(
            file_iterator(),
            media_type="video/webm",
            headers={
                "Content-Length": str(file_size - start_byte),
                "Accept-Ranges": "bytes"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/interview/recording/{session_id}/export")
async def export_recording_with_violations(
    session_id: int,
    user_id: int = Query(...),
    include_violations: bool = Query(True)
):
    """
    Export interview recording with proctoring violations
    Complete package for compliance, review, and appeal purposes
    
    Query Parameters:
    - session_id: Interview session ID (path)
    - user_id: User ID (required)
    - include_violations: Include proctoring events in export (default: true)
    
    Returns:
    - data: Complete export with:
      - Session details (company, role, score, etc.)
      - Recording info (URL, duration)
      - Proctoring report (violations count, severity)
      - Violations timeline (with timestamps and descriptions)
    """
    try:
        result = recording_service.export_with_proctoring(
            session_id=session_id,
            user_id=user_id,
            include_violations=include_violations
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/v1/interview/recording/{recording_id}")
async def delete_recording(
    recording_id: str,
    user_id: int = Query(...)
):
    """
    Delete a recording (for privacy/storage management)
    Permanently removes files from storage
    
    Query Parameters:
    - recording_id: Recording ID (path)
    - user_id: User ID (required)
    
    Returns:
    - success: Whether deletion was successful
    - message: Confirmation message
    """
    try:
        result = recording_service.delete_recording(
            recording_id=recording_id,
            user_id=user_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/interview/{session_id}/recording-status")
async def get_session_recording_status(
    session_id: int,
    user_id: int = Query(...)
):
    """
    Get recording status for an interview session
    Quick status check without full metadata
    
    Query Parameters:
    - session_id: Interview session ID (path)
    - user_id: User ID (required)
    
    Returns:
    - session_id: The session ID
    - recording_id: Associated recording ID (if any)
    - recording_status: Status (pending, recording, completed, failed)
    - recording_duration_seconds: Duration in seconds
    - has_recording: Whether recording exists
    """
    try:
        from app.database.models import InterviewSession
        from app.database.session import SessionLocal
        
        db = SessionLocal()
        
        try:
            session = db.query(InterviewSession).filter(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id
            ).first()
            
            if not session:
                raise HTTPException(status_code=404, detail="Interview session not found")
            
            return {
                "session_id": session_id,
                "recording_id": session.recording_id,
                "recording_status": session.recording_status,
                "recording_duration_seconds": session.recording_duration_seconds,
                "has_recording": bool(session.recording_url),
                "can_playback": bool(session.recording_url) and session.recording_status == "completed"
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))
