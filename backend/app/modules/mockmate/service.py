from sqlalchemy.orm import Session
from app.database.models import InterviewSession, InterviewMessage
from typing import List, Dict, Optional
from app.llm.provider import get_llm_router

class MockMateService:
    """Service for mock interview sessions (Week 3 - To be implemented with LangChain)"""
    
    @staticmethod
    async def start_interview_session(user_id: int, company: str, role: str, db: Session):
        """Create a new interview session and generate first question using Groq"""
        session = InterviewSession(
            user_id=user_id,
            company=company,
            role=role,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        try:
            # Get the LLM router instance
            llm_router = get_llm_router()
            
            # Generate first interview question using Groq
            question_data = await llm_router.generate_mockmate_question(
                company=company,
                role=role,
                topic="General experience and background",
                difficulty="easy"
            )
            
            opening = question_data.get("question", f"Welcome to your mock interview for {role} at {company}! Tell me about yourself.")
        except Exception as e:
            print(f"Error generating interview question: {e}")
            opening = f"Welcome to your mock interview for {role} at {company}! Tell me about yourself."
        
        # Save opening message
        ai_msg = InterviewMessage(session_id=session.id, role="assistant", content=opening)
        db.add(ai_msg)
        db.commit()
        return session, opening
    
    @staticmethod
    async def process_answer(session_id: int, user_answer: str, db: Session) -> dict:
        """Process candidate answer and generate next question using Groq"""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        
        # Save user answer
        user_msg = InterviewMessage(session_id=session_id, role="user", content=user_answer)
        db.add(user_msg)
        db.commit()
        
        try:
            # Get the LLM router instance
            llm_router = get_llm_router()
            
            # Generate next interview question using Groq based on topics
            topics = [
                "Technical fundamentals",
                "System design",
                "Problem-solving approach",
                "Experience with projects",
                "Team collaboration"
            ]
            
            # Rotate through topics for variety
            message_count = db.query(InterviewMessage).filter(
                InterviewMessage.session_id == session_id,
                InterviewMessage.role == "assistant"
            ).count()
            
            topic = topics[message_count % len(topics)]
            difficulty = "easy" if message_count < 2 else ("medium" if message_count < 4 else "hard")
            
            question_data = await llm_router.generate_mockmate_question(
                company=session.company,
                role=session.role,
                topic=topic,
                difficulty=difficulty
            )
            
            next_question = question_data.get("question", "Can you tell me about a challenging project you worked on?")
        except Exception as e:
            print(f"Error generating interview question: {e}")
            next_question = "Can you tell me about a challenging project you worked on?"
        
        # Save AI response
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
