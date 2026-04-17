from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Optional for OAuth
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Admin user for verification
    subscription_plan = Column(String(50), default="free")  # free, pro, premium
    
    # NEW FIELDS
    phone_number = Column(String(20), nullable=True)
    college = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    course = Column(String(255), nullable=True)  # e.g., "B.Tech Computer Science"
    years_of_experience = Column(Integer, default=0)  # 0 for fresher, 1-50 for experienced
    profile_picture = Column(String(500), nullable=True)
    is_tess_admin = Column(Boolean, default=False)  # TESS admin with special access
    
    # OAuth Fields
    google_id = Column(String(255), unique=True, nullable=True)
    
    # Email Verification
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(500), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # Password Recovery
    password_reset_token = Column(String(500), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    resume_uploads = relationship("ResumeUpload", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    gamification = relationship("UserGamification", back_populates="user", uselist=False)
    achievements = relationship("UserAchievement", back_populates="user")
    placements = relationship("PlacementRecord", back_populates="user")
    job_preference = relationship("UserJobPreference", back_populates="user", uselist=False)
    job_notifications = relationship("JobNotification", back_populates="user", foreign_keys="JobNotification.user_id")
    job_applications = relationship("JobApplication", back_populates="user", foreign_keys="JobApplication.user_id")

class ResumeUpload(Base):
    __tablename__ = "resume_uploads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String(255))
    content = Column(Text)
    score = Column(Float, default=0.0)
    target_company = Column(String(100), nullable=True)  # e.g., "Google", "Microsoft", "Amazon"
    target_role = Column(String(100), nullable=True)     # e.g., "Senior Software Engineer", "Product Manager"
    job_description = Column(Text, nullable=True)        # Company requirements for the role
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="resume_uploads")
    feedback = relationship("ResumeFeedback", back_populates="resume")

class ResumeFeedback(Base):
    __tablename__ = "resume_feedback"
    
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resume_uploads.id"))
    overall_score = Column(Float, default=0.0)
    ats_score = Column(Float, default=0.0)
    strengths = Column(Text)                    # JSON list
    improvements = Column(Text)                 # JSON list
    keywords_missing = Column(Text)             # JSON list
    summary = Column(Text)
    role_specific_recommendations = Column(Text)  # JSON - what to do for this specific role
    what_to_keep = Column(Text)                 # JSON - what's already good for this role
    what_to_change = Column(Text)               # JSON - what needs updating for this role
    company_match_score = Column(Float, default=0.0)  # How well resume matches company culture/needs
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
    
    # Proctoring fields
    proctoring_enabled = Column(Boolean, default=True)
    proctoring_status = Column(String(50), default="clean")  # clean, flagged, review_needed, cancelled
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    total_violations = Column(Integer, default=0)
    
    # Recording fields
    recording_id = Column(String(100), unique=True, nullable=True, index=True)
    recording_url = Column(String(500), nullable=True)  # Path to recorded video file
    recording_duration_seconds = Column(Integer, default=0)  # Duration in seconds
    recording_status = Column(String(50), default="pending")  # pending, recording, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interview_sessions")
    messages = relationship("InterviewMessage", back_populates="session")
    proctoring_events = relationship("ProctoringEvent", back_populates="session")
    proctoring_report = relationship("ProctoringReport", back_populates="session", uselist=False)

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


# ===== PROCTORING MODELS =====

class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    event_type = Column(String(50))  # face_not_detected, multiple_faces, tab_switch, copy_paste, etc
    severity = Column(Integer)  # 1=low, 2=medium, 3=high, 4=critical
    description = Column(Text)
    data = Column(Text)  # JSON with additional details
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="proctoring_events")


class ProctoringReport(Base):
    __tablename__ = "proctoring_reports"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), unique=True)
    total_violations = Column(Integer, default=0)
    max_severity = Column(Integer, default=0)
    severity_rating = Column(String(50))  # low, medium, high, critical
    
    # Violation breakdown
    face_not_detected_count = Column(Integer, default=0)
    multiple_faces_count = Column(Integer, default=0)
    tab_switch_count = Column(Integer, default=0)
    copy_paste_count = Column(Integer, default=0)
    window_unfocus_count = Column(Integer, default=0)
    unusual_input_count = Column(Integer, default=0)
    
    # Final assessment
    proctoring_result = Column(String(50))  # CLEAN, NEEDS_VERIFICATION, FLAGGED_FOR_REVIEW
    recommendation = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    session = relationship("InterviewSession", back_populates="proctoring_report")


# ===== GAMIFICATION MODELS =====

class UserGamification(Base):
    __tablename__ = "user_gamification"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Experience and Levels
    total_xp = Column(Integer, default=0)
    current_xp = Column(Integer, default=0)  # XP in current level
    level = Column(Integer, default=1)
    level_up_threshold = Column(Integer, default=1000)  # XP needed for next level
    
    # Streaks
    current_daily_streak = Column(Integer, default=0)
    longest_daily_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Performance Metrics
    interviews_completed = Column(Integer, default=0)
    study_sessions_completed = Column(Integer, default=0)
    total_study_minutes = Column(Integer, default=0)
    average_interview_score = Column(Float, default=0.0)
    
    # Badges/Achievements
    total_achievements = Column(Integer, default=0)
    
    # Rank (for leaderboard)
    global_rank = Column(Integer, nullable=True)
    monthly_rank = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="gamification")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    achievement_name = Column(String(100))  # e.g., "First Interview", "Week Warrior", "Perfect Score"
    achievement_type = Column(String(50))  # badge, milestone, streak
    description = Column(Text)
    xp_reward = Column(Integer, default=0)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="achievements")


class Leaderboard(Base):
    __tablename__ = "leaderboards"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    username = Column(String(255))
    global_rank = Column(Integer)
    monthly_rank = Column(Integer)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    total_achievements = Column(Integer, default=0)
    region = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===== AUDIT LOG MODEL =====

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), index=True)  # user_action, system_event, api_call, etc
    resource_type = Column(String(50), index=True)  # resume, interview, gamification, etc
    resource_id = Column(Integer, nullable=True)
    method = Column(String(10))  # GET, POST, PUT, DELETE, PATCH
    endpoint = Column(String(255), index=True)
    status_code = Column(Integer)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_body = Column(Text, nullable=True)  # JSON string
    response_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Float, default=0)  # Request duration
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ===== PLACEMENT TRACKING MODELS =====

class PlacementRecord(Base):
    __tablename__ = "placement_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    company_name = Column(String(100), index=True)
    salary_lpa = Column(Float, nullable=True)  # Salary in LPA (Lac Per Annum)
    offer_letter_url = Column(String(500), nullable=True)  # URL to uploaded offer letter
    verification_status = Column(String(50), default="pending", index=True)  # pending, verified, rejected
    verified_by_admin = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)  # If rejected, why
    
    # Additional fields for insights
    round_type = Column(String(100), nullable=True)  # Online Test, Technical, HR, etc
    total_rounds = Column(Integer, nullable=True)
    interview_duration_days = Column(Integer, nullable=True)  # How many days from first to final round
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="placements")


class PlacementStats(Base):
    __tablename__ = "placement_stats"
    
    id = Column(Integer, primary_key=True)
    
    # Overall stats
    total_placements = Column(Integer, default=0)
    total_verified_placements = Column(Integer, default=0)
    average_salary_lpa = Column(Float, default=0.0)
    highest_salary_lpa = Column(Float, default=0.0)
    
    # Company breakdown (top 5 most common)
    top_companies = Column(Text, default="{}")  # JSON: {company_name: count}
    
    # Cache metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    cache_ttl_seconds = Column(Integer, default=3600)  # 1 hour
    
    # For single global stats record, we'll use id=1
    created_at = Column(DateTime, default=datetime.utcnow)


class Question(Base):
    """Company interview questions database"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    
    # Question metadata
    company_name = Column(String(100), index=True)  # TCS, Infosys, Amazon, etc.
    round_type = Column(String(100), index=True)    # Online Test, Technical Round, HR Round
    difficulty = Column(String(20), index=True)     # Easy, Medium, Hard
    
    # Question content
    question_text = Column(Text, nullable=False)
    solution_text = Column(Text, nullable=True)
    solution_explanation = Column(Text, nullable=True)
    
    # Data source and tracking
    source = Column(String(100))  # Glassdoor, Reddit, Blind, Telegram, etc.
    frequency_score = Column(Integer, default=1)    # 1-10: How often this question is asked
    total_attempts = Column(Integer, default=0)     # Cumulative attempts by all users
    correct_attempts = Column(Integer, default=0)   # How many users got it right
    
    # Question difficulty scoring (auto-calculated)
    avg_difficulty_rating = Column(Float, default=0.0)  # 1-10 rating
    
    # Admin verification
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    verified_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_timestamp = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Auto categorization from LLM
    detected_topics = Column(JSON, default={})  # {'DSA': True, 'Arrays': True, 'DP': True}
    detected_skills = Column(JSON, default={})  # {'Problem Solving': 8, 'Code Quality': 7}
    
    # PHASE 4a: Answer & Explanation fields (added for comprehensive Q&A system)
    answer_text = Column(Text, nullable=True)  # Correct answer/solution (can be code or text)
    explanation = Column(Text, nullable=True)  # Detailed explanation (markdown format)
    solution_code = Column(Text, nullable=True)  # Code solution for coding problems
    
    # PHASE 4a: Deduplication fields
    is_duplicate = Column(Boolean, default=False, index=True)  # Is this a duplicate question?
    duplicate_of_id = Column(Integer, ForeignKey("questions.id"), nullable=True)  # Points to original if duplicate
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempts = relationship("QuestionAttempt", back_populates="question", cascade="all, delete-orphan")
    verified_by_admin = relationship("User", foreign_keys=[verified_by_admin_id])
    duplicate_of = relationship("Question", remote_side=[id], foreign_keys=[duplicate_of_id])


class QuestionAttempt(Base):
    """User attempts/solutions to questions"""
    __tablename__ = "question_attempts"
    
    id = Column(Integer, primary_key=True)
    
    # References
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), index=True)
    
    # Attempt data
    user_answer_text = Column(Text, nullable=True)  # Code/answer provided by user
    is_correct = Column(Boolean, default=False)     # Did they get it right
    user_difficulty_rating = Column(Integer, nullable=True)  # 1-10 rating from user
    
    # Performance metrics
    time_spent_seconds = Column(Integer, default=0)  # How long they spent
    attempt_number = Column(Integer, default=1)      # 1st, 2nd, 3rd attempt on this question
    hints_used = Column(Integer, default=0)          # Number of hints viewed
    attempts_before_correct = Column(Integer, nullable=True)  # If correct, how many total attempts
    
    # Interaction tracking
    viewed_solution = Column(Boolean, default=False)
    solution_view_time = Column(DateTime, nullable=True)
    skipped = Column(Boolean, default=False)
    
    # Timestamps
    attempt_date = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question", back_populates="attempts")


class StudyPlan(Base):
    """AI-generated personalized study plans"""
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True)
    
    # User and target
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    target_company = Column(String(100), index=True)  # TCS, Infosys, etc.
    target_role = Column(String(100), nullable=True)  # Software Engineer, Data Scientist, etc.
    
    # Plan details
    days_until_interview = Column(Integer, nullable=True)  # User's timeline
    estimated_hours_needed = Column(Integer, default=0)    # AI's estimate
    
    # Question distribution
    questions_json = Column(JSON, default=[])  # [{day: 1, question_id: 5, target_time: 20}, ...]
    difficulty_progression = Column(JSON, default={})  # {'Day 1-2': 'Easy', 'Day 3-4': 'Medium', ...}
    
    # Progress tracking
    completion_percentage = Column(Integer, default=0)
    questions_completed = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="active")  # active, completed, paused, archived
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)


# ===== TESS (THE EDUCATIONAL SUPPORT SYSTEM) MODELS =====

class TESSConversation(Base):
    """Store TESS conversation history"""
    __tablename__ = "tess_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    session_id = Column(String(255), index=True)
    
    # Conversation content
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # Metadata
    mode = Column(String(50), default="mentor")  # mentor, interviewer, coach
    response_time_ms = Column(Float)
    user_feedback = Column(String(10), nullable=True)  # helpful, not_helpful
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class TESSMockInterview(Base):
    """Store mock interview sessions"""
    __tablename__ = "tess_mock_interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Interview details
    interview_type = Column(String(100))
    difficulty = Column(String(20), default="medium")
    company = Column(String(100), nullable=True)
    
    # Results
    questions_asked = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    weak_areas = Column(JSON, default=list)
    strong_areas = Column(JSON, default=list)
    transcript = Column(JSON, default=list)
    
    # Time tracking
    total_time_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# Job System Models
# ============================================================================

class JobPosting(Base):
    """Store job postings from various sources"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(200), index=True)
    company = Column(String(200), index=True)
    location = Column(String(200), index=True)
    description = Column(Text)
    job_type = Column(String(50))  # Full-time, Part-time, Contract, etc.
    experience_required = Column(String(100))  # e.g., "2-5 years"
    salary_range = Column(String(100), nullable=True)  # e.g., "100k-150k"
    skills_required = Column(JSON, default=list)  # List of required skills
    url = Column(String(500), unique=True, index=True)
    source = Column(String(100), index=True)  # google, amazon, tcs, etc.
    is_active = Column(Boolean, default=True, index=True)
    closing_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notifications = relationship("JobNotification", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")


class UserJobPreference(Base):
    """Store user preferences for job recommendations"""
    __tablename__ = "user_job_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Job preferences
    desired_roles = Column(JSON, default=list)  # e.g., ["Software Engineer", "Full Stack Developer"]
    desired_companies = Column(JSON, default=list)  # e.g., ["Google", "Microsoft"]
    desired_locations = Column(JSON, default=list)  # e.g., ["San Francisco", "New York", "Remote"]
    skills = Column(JSON, default=list)  # User's technical skills
    
    # Experience and job type preferences
    experience_level = Column(String(50), default="mid-level")  # entry-level, mid-level, senior
    preferred_job_type = Column(JSON, default=list)  # Full-time, Part-time, Contract
    
    # Salary expectations
    salary_expectation_min = Column(Integer, nullable=True)
    salary_expectation_max = Column(Integer, nullable=True)
    
    # Matching preferences
    min_match_score = Column(Integer, default=50)  # Minimum score out of 100 for recommendations
    notification_frequency = Column(String(50), default="daily")  # daily, weekly, immediately
    notification_time = Column(String(10), default="09:00")  # Preferred time for digest (HH:MM)
    
    # Privacy
    is_publicly_visible = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="job_preference")


class JobNotification(Base):
    """Store job notifications sent to users"""
    __tablename__ = "job_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    
    # Match information
    match_score = Column(Integer)  # Score out of 100
    match_breakdown = Column(JSON, default=dict)  # {role: 40, skills: 30, location: 20, company: 10}
    
    # User interactions
    was_clicked = Column(Boolean, default=False)
    was_applied = Column(Boolean, default=False)
    was_rejected = Column(Boolean, default=False)
    
    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # When the notification is no longer relevant
    
    # Relationships
    job = relationship("JobPosting", back_populates="notifications")
    user = relationship("User", back_populates="job_notifications", foreign_keys=[user_id])


class JobApplication(Base):
    """Track user applications and interview progress"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    
    # Application status
    status = Column(String(50), default="applied")  # applied, shortlisted, interview_1, interview_2, offer, rejected, accepted
    applied_through = Column(String(100))  # direct_apply, referral, job_board, etc.
    
    # Timeline
    applied_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Interview tracking
    interview_rounds = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    current_round = Column(Integer, default=0)
    
    # Offer details
    offer_received = Column(Boolean, default=False)
    offer_salary = Column(Integer, nullable=True)
    accepted_offer = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    job = relationship("JobPosting", back_populates="applications")
    user = relationship("User", back_populates="job_applications", foreign_keys=[user_id])


class JobScrapeLog(Base):
    """Track job scraper health and performance"""
    __tablename__ = "job_scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    scraper_name = Column(String(100), index=True)  # google, amazon, tcs, etc.
    
    # Scrape statistics
    jobs_scraped = Column(Integer, default=0)
    jobs_added = Column(Integer, default=0)
    jobs_duplicated = Column(Integer, default=0)
    
    # Performance
    duration_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    status = Column(String(50), default="success")  # success, partial, failed
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_run = Column(DateTime, default=datetime.utcnow, index=True)


class TESSAnalytics(Base):
    """User learning analytics and recommendations"""
    __tablename__ = "tess_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Learning metrics
    total_conversations = Column(Integer, default=0)
    mock_interviews_completed = Column(Integer, default=0)
    
    # Performance tracking
    concept_mastery = Column(JSON, default=dict)
    weak_topics = Column(JSON, default=list)
    strong_topics = Column(JSON, default=list)
    
    # Recommendations
    recommended_practice = Column(JSON, default=list)
    badges = Column(JSON, default=list)
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Import module models to register them with SQLAlchemy Base
# This ensures all models are available for create_all()
from app.modules.company_data.models import (
    CompanyProfile, CompanyQuestion, CompanyJobOpening, CompanySalaryData, 
    UserCompanyInterest, InterviewSuccessStory
)
from app.modules.engagement_analytics.models import (
    UserEngagement, FeatureUsageMetric, UserJourney, AttractiveFeatureAnalysis, 
    UserFeedback, ConversionFunnel
)
from app.modules.image_generation.models import (
    ImageGenerationBase
)
