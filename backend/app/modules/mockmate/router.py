from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.modules.mockmate.service import MockMateService

router = APIRouter(prefix="/mockmate", tags=["mockmate"])

class StartInterviewRequest(BaseModel):
    company: str
    role: str = "Software Engineer"

class AnswerRequest(BaseModel):
    session_id: int
    message: str

@router.post("/start-interview")
def start_interview(
    req: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an AI mock interview session powered by Nvidia Llama"""
    valid_companies = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant"]
    if req.company not in valid_companies:
        raise HTTPException(
            status_code=400,
            detail=f"Company must be one of: {', '.join(valid_companies)}"
        )

    try:
        session, opening_message = MockMateService.start_interview_session(
            user_id=current_user.id,
            company=req.company,
            role=req.role,
            db=db
        )
        return {
            "session_id": session.id,
            "company": session.company,
            "role": session.role,
            "status": session.status,
            "first_message": opening_message,
            "message": f"Interview started with {req.company} AI Interviewer!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
def submit_answer(
    req: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer during mock interview and get AI response"""
    try:
        result = MockMateService.process_answer(
            session_id=req.session_id,
            user_answer=req.message,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview session details and full conversation history"""
    result = MockMateService.get_session_history(session_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result
