"""
TESS Database Models
Stores conversations, mock interviews, and analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class TESSConversation(Base):
    """Store TESS conversation history"""
    __tablename__ = "tess_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    session_id = Column(String(255), index=True)  # Group conversations by session
    
    # Conversation content
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # Metadata
    mode = Column(String(50), default="mentor")  # mentor, interviewer, coach
    response_time_ms = Column(Float)  # How fast was the response?
    user_feedback = Column(String(10), nullable=True)  # "helpful", "not_helpful", skip
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TESSConversation(id={self.id}, mode={self.mode}, user_id={self.user_id})>"


class TESSMockInterview(Base):
    """Store mock interview sessions"""
    __tablename__ = "tess_mock_interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Interview details
    interview_type = Column(String(100))  # e.g., "Amazon Behavioral", "Google DSA"
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    company = Column(String(100), nullable=True)
    
    # Results
    questions_asked = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)  # 0-100
    
    # Tracking weak & strong areas
    weak_areas = Column(JSON, default=list)  # ["Communication", "Problem Solving"]
    strong_areas = Column(JSON, default=list)  # ["Technical Knowledge"]
    topic_scores = Column(JSON, default=dict)  # {"DSA": 85, "System Design": 72}
    
    # Full transcript
    transcript = Column(JSON, default=list)  # [{q, a, score, feedback}, ...]
    
    # Time tracking
    total_time_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Performance metrics
    clarity_score = Column(Float, nullable=True)  # 0-100: How clear was explanation?
    technical_accuracy = Column(Float, nullable=True)  # 0-100: Technical correctness
    communication_quality = Column(Float, nullable=True)  # 0-100: Communication skills
    
    def __repr__(self):
        return f"<TESSMockInterview(id={self.id}, type={self.interview_type}, score={self.average_score})>"


class TESSAnalytics(Base):
    """User learning analytics and recommendations"""
    __tablename__ = "tess_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Learning metrics
    total_conversations = Column(Integer, default=0)
    total_voice_time_minutes = Column(Float, default=0.0)
    mock_interviews_completed = Column(Integer, default=0)
    total_learning_time_hours = Column(Float, default=0.0)
    
    # Performance tracking
    concept_mastery = Column(JSON, default=dict)  # {"DSA": 0.85, "System Design": 0.60}
    interview_performance_trend = Column(JSON, default=list)  # [85, 78, 82, 90]
    weak_topics = Column(JSON, default=list)  # Auto-identified from interviews
    strong_topics = Column(JSON, default=list)
    
    # Recommendations (AI-generated)
    recommended_practice = Column(JSON, default=list)  # Next recommended topics
    personalized_learning_plan = Column(JSON, default=list)  # Weekly study recommendations
    improvement_areas = Column(JSON, default=dict)  # {"Communication": 0.65, "DSA": 0.72}
    
    # Badges & achievements (gamification)
    badges = Column(JSON, default=list)  # ["first_interview", "100_conversations", ...]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TESSAnalytics(user_id={self.user_id}, interviews={self.mock_interviews_completed})>"


class TESSLearningSession(Base):
    """Track individual learning sessions"""
    __tablename__ = "tess_learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Session details
    session_type = Column(String(50))  # "free_chat", "concept_learning", "mock_interview"
    topic = Column(String(255), nullable=True)
    duration_minutes = Column(Float, default=0.0)
    
    # Learning metrics for this session
    questions_asked = Column(Integer, default=0)
    concepts_covered = Column(JSON, default=list)
    effectiveness_score = Column(Float, nullable=True)  # 0-100: How effective was session?
    
    # Session notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<TESSLearningSession(user_id={self.user_id}, type={self.session_type})>"
