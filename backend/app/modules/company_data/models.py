"""
Company Data Models
Tracks real-time company requirements, interview questions, and salary data
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base


class CompanyProfile(Base):
    """Company information and statistics"""
    __tablename__ = "company_profiles"
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), unique=True, index=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), index=True)
    
    # Hiring info
    active_job_openings = Column(Integer, default=0)
    hiring_pace = Column(String(50))  # fast, moderate, slow
    
    # Interview data
    avg_interview_rounds = Column(Integer, default=0)
    popular_roles = Column(JSON, default=[])  # ['SDE', 'PM', 'Data Science']
    common_interview_types = Column(JSON, default=[])  # ['Technical', 'HR', 'System Design']
    
    # Compensation
    avg_base_salary_usd = Column(Float, nullable=True)
    avg_total_comp_usd = Column(Float, nullable=True)
    avg_bonus_percentage = Column(Float, nullable=True)
    
    # Statistics
    total_interviews_tracked = Column(Integer, default=0)
    placement_rate = Column(Float, default=0.0)  # 0-100%
    average_rating = Column(Float, default=0.0)  # 1-5 stars
    
    # Last updated
    data_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview_questions = relationship("CompanyQuestion", back_populates="company", cascade="all, delete-orphan")
    job_openings = relationship("CompanyJobOpening", back_populates="company", cascade="all, delete-orphan")
    salary_data = relationship("CompanySalaryData", back_populates="company", cascade="all, delete-orphan")


class CompanyQuestion(Base):
    """Real-time interview questions from companies"""
    __tablename__ = "company_questions"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False, index=True)
    
    # Question details
    question_text = Column(Text, nullable=False)
    topic = Column(String(100), index=True)  # DSA, System Design, Behavioral
    difficulty = Column(String(20), index=True)  # easy, medium, hard
    round_type = Column(String(50))  # Phone Screen, Technical, System Design, HR
    role = Column(String(100), index=True)  # SDE, PM, Data Science
    
    # Source info
    source = Column(String(100))  # Glassdoor, LeetCode, Blind, User Submission
    source_url = Column(String(500), nullable=True)
    interview_date = Column(DateTime, nullable=True)  # When the interview happened
    
    # Verification
    verified = Column(Boolean, default=False)
    verification_count = Column(Integer, default=0)  # How many users confirmed
    
    # Frequency
    frequency_score = Column(Integer, default=1)  # 1-10 (how often asked)
    times_asked = Column(Integer, default=1)  # Absolute count
    
    # Success metrics
    success_rate = Column(Float, default=0.0)  # What % solved it
    avg_prep_time_hours = Column(Float, default=0.0)  # Time to prepare
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("CompanyProfile", back_populates="interview_questions")


class CompanyJobOpening(Base):
    """Live job openings from companies"""
    __tablename__ = "company_job_openings"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False, index=True)
    
    # Job details
    job_title = Column(String(255), index=True)
    role = Column(String(100), index=True)  # SDE, PM, Data Science
    seniority = Column(String(50), index=True)  # Fresher, Junior, Senior, Staff
    
    # Requirements
    required_years_experience = Column(Integer, nullable=True)
    required_skills = Column(JSON, default=[])  # ['Python', 'React', 'AWS']
    preferred_skills = Column(JSON, default=[])
    
    # Location
    location = Column(String(255), index=True)
    is_remote = Column(Boolean, default=False)
    remote_type = Column(String(50))  # full-remote, hybrid, onsite
    
    # Compensation
    salary_min_usd = Column(Float, nullable=True)
    salary_max_usd = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    
    # Source
    job_url = Column(String(500), nullable=True)
    source = Column(String(50))  # LinkedIn, Glassdoor, Company Website
    
    # Status
    is_active = Column(Boolean, default=True)
    posted_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("CompanyProfile", back_populates="job_openings")


class CompanySalaryData(Base):
    """Verified salary data by company and role"""
    __tablename__ = "company_salary_data"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_profiles.id"), nullable=False, index=True)
    
    role = Column(String(100), index=True)  # SDE, PM, Data Science
    seniority = Column(String(50), index=True)  # Fresher, Junior, Senior, Staff
    location = Column(String(255), index=True)
    currency = Column(String(10), default="USD")
    
    # Salary breakdown
    base_salary_min = Column(Float)
    base_salary_max = Column(Float)
    base_salary_avg = Column(Float)
    
    bonus_min = Column(Float, default=0)
    bonus_max = Column(Float, default=0)
    bonus_avg = Column(Float, default=0)
    
    stock_min = Column(Float, default=0)
    stock_max = Column(Float, default=0)
    stock_avg = Column(Float, default=0)
    
    # Total compensation
    total_comp_min = Column(Float)
    total_comp_max = Column(Float)
    total_comp_avg = Column(Float)
    
    # Data credibility
    data_points = Column(Integer, default=0)  # Number of reports consolidated
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("CompanyProfile", back_populates="salary_data")


class UserCompanyInterest(Base):
    """Track which companies users are interested in"""
    __tablename__ = "user_company_interests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    company_name = Column(String(255), index=True)
    
    # Interest tracking
    times_viewed = Column(Integer, default=1)
    last_viewed = Column(DateTime, default=datetime.utcnow)
    
    # Engagement
    questions_practiced = Column(Integer, default=0)
    mock_interviews_taken = Column(Integer, default=0)
    resume_customized = Column(Boolean, default=False)
    
    # Status
    target_company = Column(Boolean, default=False)  # Is this their target?
    applied = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InterviewSuccessStory(Base):
    """Success stories from users who got placed"""
    __tablename__ = "interview_success_stories"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True, index=True)
    
    company_name = Column(String(255), index=True)
    role = Column(String(100), index=True)
    seniority = Column(String(50))
    
    # Experience
    background = Column(Text)  # What was user's background
    preparation_hours = Column(Integer)  # How many hours they prepared
    key_preparation_areas = Column(JSON, default=[])  # What helped them
    
    # Results
    total_interview_rounds = Column(Integer)
    time_to_offer_days = Column(Integer)
    accepted_offer = Column(Boolean, default=True)
    
    # Compensation (verified by offer letter)
    base_salary_usd = Column(Float, nullable=True)
    total_comp_usd = Column(Float, nullable=True)
    
    # Feedback
    interview_experience = Column(Text)  # What the interview was like
    tips_for_others = Column(Text)  # Advice for candidates
    helpful_resources = Column(JSON, default=[])  # What helped you
    
    # Engagement
    verified_by_offer_letter = Column(Boolean, default=False)
    likes = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    # Visibility
    published = Column(Boolean, default=False)  # Public story
    anonymized = Column(Boolean, default=True)  # Hide identity
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
