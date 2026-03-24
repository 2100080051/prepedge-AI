from sqlalchemy.orm import Session
from app.database.models import InterviewSession, InterviewMessage
from typing import List, Dict, Optional

class MockMateService:
    """Service for mock interview sessions (Week 3 - To be implemented with LangChain)"""
    
    @staticmethod
    def start_interview_session(user_id: int, company: str, role: str, db: Session):
        """Create a new interview session"""
        session = InterviewSession(
            user_id=user_id,
            company=company,
            role=role,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # TODO: Interview with LangChain coming in Week 3
        opening = f"Welcome to your mock interview for {role} at {company}! Let's get started."
        ai_msg = InterviewMessage(session_id=session.id, role="assistant", content=opening)
        db.add(ai_msg)
        db.commit()
        return session, opening
    
    @staticmethod
    def process_answer(session_id: int, user_answer: str, db: Session) -> dict:
        """Process candidate answer and generate next question"""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        
        # Save user answer
        user_msg = InterviewMessage(session_id=session_id, role="user", content=user_answer)
        db.add(user_msg)
        db.commit()
        
        # TODO: Generate next question with LangChain in Week 3
        next_question = "Can you tell me about a challenging project you worked on?"
        ai_msg = InterviewMessage(session_id=session_id, role="assistant", content=next_question)
        db.add(ai_msg)
        db.commit()
        
        return {
            "response": next_question,
            "session_id": session_id,
            "is_complete": False
        }
    
    @staticmethod
    def get_session_history(session_id: int, db: Session) -> Optional[dict]:
        """Get full interview session history"""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return None
        messages = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id
        ).order_by(InterviewMessage.id.asc()).all()
        return {
            "session_id": session.id,
            "company": session.company,
            "role": session.role,
            "status": session.status,
            "score": session.score,
            "messages": [{"role": m.role, "content": m.content} for m in messages]
        }
