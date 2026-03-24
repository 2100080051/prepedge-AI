"""
Proctoring API Endpoints
Handles: frame analysis, event tracking, report generation, status checks
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User, InterviewSession, ProctoringReport
from app.modules.proctoring.service import ProctoringService

router = APIRouter(prefix="/proctoring", tags=["proctoring"])


@router.post("/analyze-frame/{session_id}")
async def analyze_frame(
    session_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze video frame for violations
    Payload: {"frame_data": "base64_encoded_image"}
    Returns: violations detected, severity, recommendation
    """
    try:
        # Verify session belongs to user
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.proctoring_enabled:
            raise HTTPException(status_code=400, detail="Proctoring not enabled for this session")
        
        # Analyze frame
        frame_data = payload.get('frame_data')
        if not frame_data:
            raise HTTPException(status_code=400, detail="No frame data provided")
        
        analysis_result = ProctoringService.analyze_frame(
            session_id=session_id,
            frame_data=frame_data,
            db_session=db
        )
        
        return {
            "status": "analyzed",
            "timestamp": analysis_result['timestamp'],
            "violations": analysis_result.get('violations', []),
            "is_suspicious": analysis_result.get('is_suspicious', False),
            "max_severity": analysis_result.get('max_severity', 'low'),
            "confidence": analysis_result.get('confidence', 0.0)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frame analysis failed: {str(e)}")


@router.post("/track-event/{session_id}")
async def track_event(
    session_id: int,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track a violation event
    Payload: {"event_type": "tab_switch", "data": {...}}
    Returns: event tracked confirmation
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        event_type = payload.get('event_type')
        if not event_type:
            raise HTTPException(status_code=400, detail="Event type required")
        
        # Track the event
        if event_type == 'copy_paste':
            ProctoringService.track_keyboard_input('ctrl+v', db)
        elif event_type in ['tab_switch', 'focus_lost', 'fullscreen_exit']:
            ProctoringService.track_window_event(session_id, event_type, db)
        
        return {
            "status": "tracked",
            "event_type": event_type,
            "session_id": session_id,
            "total_violations": session.total_violations + 1
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event tracking failed: {str(e)}")


@router.get("/status/{session_id}")
async def get_proctoring_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time proctoring status for session
    Returns: violations count, flags, status
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        status = ProctoringService.get_session_proctoring_status(session_id, db)
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/report/{session_id}")
async def generate_proctoring_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate final proctoring report after session ends
    Returns: detailed violation analysis and recommendations
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != 'completed':
            raise HTTPException(status_code=400, detail="Session must be completed before generating report")
        
        # Check if report already exists
        existing_report = db.query(ProctoringReport).filter(
            ProctoringReport.session_id == session_id
        ).first()
        
        if existing_report:
            return {
                "status": "generated",
                "report_id": existing_report.id,
                "total_violations": existing_report.total_violations,
                "severity_rating": existing_report.severity_rating,
                "proctoring_result": existing_report.proctoring_result,
                "recommendation": existing_report.recommendation,
                "violations_breakdown": {
                    "critical_faces": existing_report.multiple_faces_count,
                    "no_face_detected": existing_report.face_not_detected_count,
                    "copy_paste": existing_report.copy_paste_count,
                    "tab_switches": existing_report.tab_switch_count,
                    "window_unfocus": existing_report.window_unfocus_count
                }
            }
        
        # Generate new report
        report_data = ProctoringService.generate_proctoring_report(session_id, db)
        
        return report_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/report/{session_id}/details")
async def get_report_details(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed proctoring report with all violation details"""
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        report = db.query(ProctoringReport).filter(
            ProctoringReport.session_id == session_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "report_id": report.id,
            "session_id": session_id,
            "total_violations": report.total_violations,
            "severity_rating": report.severity_rating,
            "max_severity": report.max_severity,
            "violations_breakdown": {
                "critical_multiple_faces": report.multiple_faces_count,
                "high_no_face_detected": report.face_not_detected_count,
                "critical_copy_paste": report.copy_paste_count,
                "medium_tab_switches": report.tab_switch_count,
                "medium_window_unfocus": report.window_unfocus_count,
                "low_unusual_input": report.unusual_input_count
            },
            "proctoring_result": report.proctoring_result,
            "recommendation": report.recommendation,
            "created_at": report.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report fetch failed: {str(e)}")


@router.websocket("/ws/{session_id}")
async def websocket_proctoring(websocket: WebSocket, session_id: int):
    """
    WebSocket for real-time proctoring monitoring
    Receives frame data and events, sends back violation alerts
    """
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'frame':
                # Process frame (would integrate with analysis)
                await websocket.send_json({
                    'type': 'frame_processed',
                    'violations': 0,
                    'status': 'clean'
                })
            
            elif data.get('type') == 'event':
                # Process event
                await websocket.send_json({
                    'type': 'event_tracked',
                    'event_type': data.get('event_type'),
                    'severity': 'medium'
                })
    
    except WebSocketDisconnect:
        print(f"Client disconnected from proctoring session {session_id}")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })
        await websocket.close()
