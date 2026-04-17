"""
PHASE 4b: Job Notification System Models

This module contains SQLAlchemy models for:
1. JobPosting - Job listings from company websites
2. UserJobPreference - User's job search criteria
3. JobNotification - Tracks notifications sent to users
4. JobApplication - Tracks user applications to jobs
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base


class JobPosting(Base):
    """Job postings scraped from company websites and APIs"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True)
    
    # Job basics
    job_title = Column(String(255), index=True)  # "Software Engineer", "Data Scientist"
    company = Column(String(100), index=True)  # Company name
    location = Column(String(255), index=True)
    job_description = Column(Text)
    
    # Job details
    job_type = Column(String(50), index=True)  # "Full-time", "Internship", "Contract"
    experience_required = Column(String(100))  # "0-2 years", "3-5 years", "5+ years"
    salary_range = Column(String(100), nullable=True)  # "10-15 LPA", "$80k-$120k"
    skills_required = Column(JSON, default=[])  # ["Python", "React", "AWS"]
    
    # Application details
    url = Column(String(500), unique=True, index=True)  # Direct link to apply
    source = Column(String(100), index=True)  # amazon_careers, google_careers, etc
    source_url = Column(String(500), nullable=True)  # Where we scraped from
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    closing_date = Column(DateTime, nullable=True)
    
    # Tracking
    total_applications = Column(Integer, default=0)  # How many users applied
    total_views = Column(Integer, default=0)  # How many users viewed
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    notifications = relationship("JobNotification", back_populates="job")
    applications = relationship("JobApplication", back_populates="job")


class UserJobPreference(Base):
    """User's job search preferences and criteria"""
    __tablename__ = "user_job_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Job preferences
    desired_roles = Column(JSON, default=["Software Engineer"])  # List of roles user wants
    desired_companies = Column(JSON, default=[])  # Preferred companies
    desired_locations = Column(JSON, default=[])  # Preferred locations
    
    # Qualifications
    skills = Column(JSON, default=[])  # Technical skills
    experience_level = Column(String(50), default="Fresher")  # Fresher, Junior, Senior, Lead
    experience_years = Column(Float, nullable=True)  # Years of experience
    
    # Criteria
    preferred_job_type = Column(JSON, default=["Full-time"])  # Full-time, Internship, etc
    salary_expectation_min = Column(Float, nullable=True)  # Minimum salary
    salary_expectation_max = Column(Float, nullable=True)  # Maximum salary
    
    # Notification settings
    min_match_score = Column(Float, default=60.0)  # Only show jobs >60% match
    notification_frequency = Column(String(50), default="daily")  # daily, weekly, monthly, disabled
    notification_time = Column(String(10), default="09:00")  # Time for daily digest (HH:MM)
    last_notification_sent = Column(DateTime, nullable=True)
    
    # Privacy
    make_profile_visible = Column(Boolean, default=False)  # Show profile to companies
    allow_recruiter_contact = Column(Boolean, default=False)  # Allow recruiters to contact
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="job_preference")


class JobNotification(Base):
    """Tracks job notifications sent to users"""
    __tablename__ = "job_notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    
    # Matching
    match_score = Column(Float, default=0.0)  # 0-100, how well job matches user
    match_breakdown = Column(JSON, default={})  # {role: 40%, skills: 30%, location: 20%, company: 10%}
    
    # Tracking
    was_clicked = Column(Boolean, default=False, index=True)
    clicked_at = Column(DateTime, nullable=True)
    
    was_applied = Column(Boolean, default=False, index=True)
    applied_at = Column(DateTime, nullable=True)
    
    was_rejected = Column(Boolean, default=False)  # User marked as "Not Interested"
    rejected_at = Column(DateTime, nullable=True)
    
    # Timeline
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Notification expires after X days
    
    # Relationships
    job = relationship("JobPosting", back_populates="notifications")


class JobApplication(Base):
    """Tracks user's job applications"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    
    # Application details
    status = Column(String(50), default="applied")  # applied, shortlisted, rejected, offer
    applied_through = Column(String(50))  # prepedge, direct, referral
    
    # Timeline
    applied_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_received_at = Column(DateTime, nullable=True)
    
    # Interview details
    interview_rounds = Column(Integer, default=0)  # Number of rounds
    interviews_completed = Column(Integer, default=0)
    current_round = Column(String(100), nullable=True)  # "Online Test", "Technical", "HR"
    
    # Outcome
    offer_received = Column(Boolean, default=False)
    offer_salary = Column(Float, nullable=True)
    accepted_offer = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text, nullable=True)  # Any notes about the process
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("JobPosting", back_populates="applications")


class JobScrapeLog(Base):
    """Logs for job scraping operations (for debugging/monitoring)"""
    __tablename__ = "job_scrape_logs"
    
    id = Column(Integer, primary_key=True)
    
    # Scraper info
    scraper_name = Column(String(100), index=True)  # google_careers, amazon_jobs, etc
    scheduled_time = Column(DateTime, index=True)  # When the scraper was scheduled to run
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Results
    total_jobs_fetched = Column(Integer, default=0)
    new_jobs_added = Column(Integer, default=0)
    jobs_updated = Column(Integer, default=0)
    jobs_deactivated = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="running")  # running, completed, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Performance
    duration_seconds = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
