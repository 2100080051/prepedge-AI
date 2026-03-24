from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String(50), default="free")  # free, pro, premium
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resume_uploads = relationship("ResumeUpload", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")

class ResumeUpload(Base):
    __tablename__ = "resume_uploads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String(255))
    content = Column(Text)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="resume_uploads")
    feedback = relationship("ResumeFeedback", back_populates="resume")

class ResumeFeedback(Base):
    __tablename__ = "resume_feedback"
    
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resume_uploads.id"))
    overall_score = Column(Float, default=0.0)
    ats_score = Column(Float, default=0.0)
    strengths = Column(Text)           # JSON list
    improvements = Column(Text)        # JSON list
    keywords_missing = Column(Text)    # JSON list
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("ResumeUpload", back_populates="feedback")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String(100))
    role = Column(String(100))
    duration_minutes = Column(Integer)
    score = Column(Float, default=0.0)
    status = Column(String(50), default="active")  # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interview_sessions")
    messages = relationship("InterviewMessage", back_populates="session")

class InterviewMessage(Base):
    __tablename__ = "interview_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    role = Column(String(20))  # user or assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="messages")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String(255))
    duration_minutes = Column(Integer)
    flashcards_studied = Column(Integer, default=0)
    performance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="study_sessions")

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(255), index=True)
    question = Column(Text)
    answer = Column(Text)
    difficulty = Column(String(20))  # easy, medium, hard
    company = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    razorpay_order_id = Column(String(100), unique=True)
    razorpay_payment_id = Column(String(100), unique=True, nullable=True)
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="pending")  # pending, completed, failed
    subscription_plan = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
