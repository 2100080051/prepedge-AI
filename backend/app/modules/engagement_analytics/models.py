"""
User Engagement Analytics
Track what features users engage with most to understand user behavior and preferences
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base


class UserEngagement(Base):
    """Daily engagement metrics for each user"""
    __tablename__ = "user_engagement"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Daily activity
    date = Column(DateTime, default=datetime.utcnow, index=True)
    session_count = Column(Integer, default=0)  # Sessions per day
    total_session_minutes = Column(Integer, default=0)
    
    # Feature usage today
    features_used = Column(JSON, default=[])  # ['resume', 'flashcards', 'interview']
    most_used_feature = Column(String(50))
    
    # Achievements today
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)  # 0-100%
    xp_earned = Column(Integer, default=0)
    
    # Engagement score
    engagement_score = Column(Float, default=0.0)  # 0-100
    streak = Column(Integer, default=0)  # Days in a row
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeatureUsageMetric(Base):
    """Track usage of each feature"""
    __tablename__ = "feature_usage_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Feature identification
    feature_name = Column(String(100), index=True)
    # Options: resume, flashcards, mock_interview, company_questions, gamification, 
    #          dashboard, linkedin, study_session, questions_practice
    
    # Usage metrics
    times_accessed = Column(Integer, default=0)
    total_time_minutes = Column(Integer, default=0)
    avg_session_time_minutes = Column(Float, default=0.0)
    
    # Engagement
    actions_performed = Column(Integer, default=0)  # Clicks, submissions, etc.
    completion_rate = Column(Float, default=0.0)  # %
    
    # Value perception
    helpful_count = Column(Integer, default=0)  # Times user marked helpful
    would_recommend = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)  # 1-5 stars
    
    # Last usage
    last_accessed = Column(DateTime, nullable=True)
    first_accessed = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserJourney(Base):
    """Track user's journey from signup to placement"""
    __tablename__ = "user_journeys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Journey timeline
    signup_date = Column(DateTime, default=datetime.utcnow)
    first_action_date = Column(DateTime, nullable=True)
    
    # Features discovered in order
    features_sequence = Column(JSON, default=[])  # Order of feature discovery
    first_feature = Column(String(50))  # Which feature engaged them first
    
    # Conversion stages
    profiles_viewed = Column(Integer, default=0)
    questions_attempted = Column(Integer, default=0)
    mock_interviews_taken = Column(Integer, default=0)
    resume_optimized = Column(Boolean, default=False)
    company_target_set = Column(Boolean, default=False)
    
    # Engagement depth
    days_active = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_minutes_spent = Column(Integer, default=0)
    
    # Outcomes
    applications_submitted = Column(Integer, default=0)
    interviews_landed = Column(Integer, default=0)
    offers_received = Column(Integer, default=0)
    placement_success = Column(Boolean, default=False)
    placement_date = Column(DateTime, nullable=True)
    
    # Lifetime value
    user_lifetime_value = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AttractiveFeatureAnalysis(Base):
    """Overall metrics on which features attract and retain users"""
    __tablename__ = "attractive_feature_analysis"
    
    id = Column(Integer, primary_key=True)
    
    # Feature name
    feature_name = Column(String(100), unique=True, index=True)
    # Options: Company Questions, Mock Interviews, Resume Builder, Flashcards, etc.
    
    # Attraction metrics
    users_tried = Column(Integer, default=0)
    conversion_to_repeat = Column(Float, default=0.0)  # % who use again
    avg_time_to_first_use = Column(Float, default=0.0)  # Days after signup
    
    # Retention metrics
    daily_active_users = Column(Integer, default=0)
    weekly_returning_rate = Column(Float, default=0.0)  # %
    monthly_returning_rate = Column(Float, default=0.0)  # %
    churn_rate = Column(Float, default=0.0)  # % who stop using
    
    # Value metrics
    avg_rating = Column(Float, default=0.0)  # 1-5 stars
    positive_feedback_rate = Column(Float, default=0.0)  # % positive reviews
    
    # Impact on outcomes
    avg_questions_attempted = Column(Integer, default=0)
    avg_interview_rounds_cleared = Column(Integer, default=0)
    placement_rate_when_used = Column(Float, default=0.0)  # %
    
    # Stickiness (how addictive)
    addiction_score = Column(Float, default=0.0)  # 0-100, based on behavior
    # Calculated from: frequency, session length, return rate
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserFeedback(Base):
    """Collect user feedback on features"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Feedback details
    feature_name = Column(String(100), index=True)
    feedback_type = Column(String(50))  # bug, suggestion, compliment, complaint
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    
    # Context
    context = Column(JSON, default={})  # When/where feedback given
    # e.g., {"feature": "mock_interview", "after_round": 2, "time_spent": 45}
    
    # Resolution
    resolved = Column(Boolean, default=False)
    resolved_by_team = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
class ConversionFunnel(Base):
    """Track conversion at each stage of user journey"""
    __tablename__ = "conversion_funnel"
    
    id = Column(Integer, primary_key=True)
    
    # Funnel stages
    stage = Column(String(100), unique=True)  # signup, first_login, explore_features, try_feature, subscribe, apply, landed_interview, placement
    
    # Metrics
    total_users = Column(Integer, default=0)
    conversion_from_previous = Column(Float, default=0.0)  # % from previous stage
    dropout_rate = Column(Float, default=0.0)  # % who leave at this stage
    avg_time_in_stage = Column(Float, default=0.0)  # Hours
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
