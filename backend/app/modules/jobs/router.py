"""
Job recommendations and notifications API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.models import (
    User, JobPosting, UserJobPreference, JobNotification, 
    JobApplication, JobScrapeLog
)
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.modules.jobs.job_matcher import JobMatcher, SmartJobRecommendation
from pydantic import BaseModel, Field

router = APIRouter(tags=["jobs"], prefix="/jobs")


# ==================== Pydantic Schemas ====================

class JobPreferenceRequest(BaseModel):
    """Request to create/update user job preferences"""
    desired_roles: List[str] = Field(default=["Software Engineer"], description="Desired job roles")
    desired_companies: List[str] = Field(default=[], description="Preferred companies")
    desired_locations: List[str] = Field(default=[], description="Preferred locations")
    skills: List[str] = Field(default=[], description="Technical skills")
    experience_level: str = Field(default="Fresher", description="Experience level")
    experience_years: Optional[float] = Field(description="Years of experience")
    preferred_job_type: List[str] = Field(default=["Full-time"], description="Preferred job types")
    salary_expectation_min: Optional[float] = Field(description="Minimum expected salary")
    salary_expectation_max: Optional[float] = Field(description="Maximum expected salary")
    min_match_score: float = Field(default=60.0, description="Minimum match score to show jobs")
    notification_frequency: str = Field(default="daily", description="daily, weekly, monthly, disabled")
    notification_time: str = Field(default="09:00", description="Time for notifications (HH:MM)")
    make_profile_visible: bool = Field(default=False, description="Show profile to companies")
    allow_recruiter_contact: bool = Field(default=False, description="Allow recruiter contact")

    class Config:
        json_schema_extra = {
            "example": {
                "desired_roles": ["Software Engineer", "Backend Developer"],
                "desired_companies": ["Google", "Amazon"],
                "desired_locations": ["Bangalore", "Remote"],
                "skills": ["Python", "JavaScript", "React"],
                "experience_level": "Junior",
                "preferred_job_type": ["Full-time"],
                "min_match_score": 70.0,
                "notification_frequency": "daily",
                "notification_time": "09:00"
            }
        }


class JobPreferenceResponse(JobPreferenceRequest):
    """Response with user job preferences"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobPostingResponse(BaseModel):
    """Job posting response"""
    id: int
    job_title: str
    company: str
    location: str
    job_description: Optional[str]
    job_type: str
    experience_required: Optional[str]
    salary_range: Optional[str]
    skills_required: List[str]
    url: str
    source: str
    is_active: bool
    closing_date: Optional[datetime]
    total_applications: int
    total_views: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobRecommendationResponse(BaseModel):
    """Job recommendation with match score"""
    job_id: int
    job_title: str
    company: str
    location: str
    url: str
    total_score: float
    role_score: float
    skills_score: float
    location_score: float
    company_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 1,
                "job_title": "Senior Software Engineer",
                "company": "Google",
                "location": "Bangalore",
                "url": "https://careers.google.com/jobs/123",
                "total_score": 85.5,
                "role_score": 90.0,
                "skills_score": 80.0,
                "location_score": 85.0,
                "company_score": 75.0
            }
        }


class JobApplicationRequest(BaseModel):
    """Request to apply for a job"""
    applied_through: str = Field(default="prepedge", description="How user applied: prepedge, direct, referral")
    notes: Optional[str] = Field(description="Notes about application")

    class Config:
        json_schema_extra = {
            "example": {
                "applied_through": "prepedge",
                "notes": "Applied after successful interview prep"
            }
        }


class JobApplicationResponse(BaseModel):
    """Job application response"""
    id: int
    user_id: int
    job_id: int
    status: str
    applied_through: str
    applied_at: datetime
    response_received_at: Optional[datetime]
    interview_rounds: int
    interviews_completed: int
    current_round: Optional[str]
    offer_received: bool
    offer_salary: Optional[float]
    accepted_offer: bool

    class Config:
        from_attributes = True


class JobNotificationResponse(BaseModel):
    """Job notification response"""
    id: int
    job_id: int
    job_title: str
    company: str
    match_score: float
    match_breakdown: dict
    was_clicked: bool
    was_applied: bool
    was_rejected: bool
    sent_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== API Endpoints ====================

@router.post("/preferences", response_model=JobPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_job_preference(
    preferences: JobPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update user's job preferences
    
    **Description**: User can set their job search criteria including desired roles,
    companies, locations, skills, salary expectations, and notification preferences.
    
    **Requirements**: User must be authenticated
    
    **Use Cases**:
    - New user setting up job search profile on first login
    - User updating preferences after job search progress
    - User changing notification frequency
    
    **Returns**: Updated user job preference record with all settings
    """
    # Check if user already has preferences
    user_pref = db.query(UserJobPreference).filter(
        UserJobPreference.user_id == current_user.id
    ).first()
    
    try:
        if user_pref:
            # Update existing preferences
            for field, value in preferences.dict().items():
                setattr(user_pref, field, value)
            user_pref.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            user_pref = UserJobPreference(
                user_id=current_user.id,
                **preferences.dict()
            )
        
        db.add(user_pref)
        db.commit()
        db.refresh(user_pref)
        return user_pref
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save preferences: {str(e)}"
        )


@router.get("/preferences", response_model=JobPreferenceResponse)
def get_job_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's current job preferences
    
    **Description**: Retrieve the user's saved job search criteria and notification settings
    
    **Returns**: User's job preference record or 404 if not set
    """
    user_pref = db.query(UserJobPreference).filter(
        UserJobPreference.user_id == current_user.id
    ).first()
    
    if not user_pref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preferences not found. Please create preferences first."
        )
    
    return user_pref


@router.get("/recommendations", response_model=List[JobRecommendationResponse])
def get_job_recommendations(
    limit: int = 10,
    min_score: float = 60.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized job recommendations based on user profile
    
    **Description**: Returns ranked list of jobs matching user's profile using the
    scoring algorithm (40% role, 30% skills, 20% location, 10% company).
    
    **Parameters**:
    - limit: Maximum number of recommendations (default: 10)
    - min_score: Minimum match score 0-100 (default: 60)
    
    **Algorithm**: 
    - Role matching: Exact/keyword comparison
    - Skills: User skills intersection with job requirements
    - Location: Exact match or remote support
    - Company: Preferred company match
    
    **Returns**: List of recommended jobs with score breakdown
    """
    # Get user's job preferences
    user_pref = db.query(UserJobPreference).filter(
        UserJobPreference.user_id == current_user.id
    ).first()
    
    if not user_pref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set up job preferences first"
        )
    
    # Get active job postings
    jobs = db.query(JobPosting).filter(JobPosting.is_active == True).limit(100).all()
    
    if not jobs:
        return []
    
    # Score each job using the matcher
    matcher = JobMatcher()
    scored_jobs = []
    
    for job in jobs:
        match = matcher.match_job(
            job_id=job.id,
            job_title=job.job_title,
            company=job.company,
            location=job.location,
            url=job.url,
            job_skills=job.skills_required or [],
            desired_roles=user_pref.desired_roles,
            user_skills=user_pref.skills,
            desired_locations=user_pref.desired_locations,
            desired_companies=user_pref.desired_companies
        )
        
        if match.total_score >= min_score:
            scored_jobs.append(match)
    
    # Sort by total score (descending) and limit results
    scored_jobs = sorted(scored_jobs, key=lambda x: x.total_score, reverse=True)[:limit]
    
    # Apply smart recommendations (boost scores based on user history)
    smart_rec = SmartJobRecommendation()
    scored_jobs = smart_rec.diversify_recommendations(scored_jobs, top_n=limit)
    
    return [
        JobRecommendationResponse(
            job_id=job.job_id,
            job_title=job.job_title,
            company=job.company,
            location=job.location,
            url=job.url,
            total_score=job.total_score,
            role_score=job.role_score,
            skills_score=job.skills_score,
            location_score=job.location_score,
            company_score=job.company_score
        )
        for job in scored_jobs
    ]


@router.get("/jobs/{job_id}", response_model=JobPostingResponse)
def get_job_details(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific job
    
    **Description**: Retrieve full job details including description, requirements,
    salary, skills, and application link
    
    **Track**: Increments job view count for analytics
    
    **Returns**: Complete job posting information
    """
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    job.total_views += 1
    db.commit()
    
    return job


@router.post("/jobs/{job_id}/apply", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    job_id: int,
    application: JobApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply for a job
    
    **Description**: Record that user applied for a job. Creates application record
    and links to the job posting for tracking.
    
    **Track**: Increments job application count for analytics
    
    **Returns**: Job application record with status tracking
    """
    # Check if job exists
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user already applied
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == job_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    try:
        # Create application record
        job_application = JobApplication(
            user_id=current_user.id,
            job_id=job_id,
            applied_through=application.applied_through,
            notes=application.notes,
            status="applied"
        )
        
        # Increment job application count
        job.total_applications += 1
        
        db.add(job_application)
        db.commit()
        db.refresh(job_application)
        return job_application
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to apply: {str(e)}"
        )


@router.get("/my-applications", response_model=List[JobApplicationResponse])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all of user's job applications
    
    **Description**: List all jobs the user has applied for with current status
    
    **Returns**: List of user's job applications sorted by most recent
    """
    applications = db.query(JobApplication)\
        .filter(JobApplication.user_id == current_user.id)\
        .order_by(JobApplication.applied_at.desc())\
        .all()
    
    return applications


@router.post("/jobs/{job_id}/click")
def track_job_click(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track when user clicks on a job notification
    
    **Description**: Records engagement metric - user clicked a job recommendation
    
    **Returns**: Confirmation message
    """
    notification = db.query(JobNotification).filter(
        JobNotification.user_id == current_user.id,
        JobNotification.job_id == job_id
    ).first()
    
    if notification:
        notification.was_clicked = True
        notification.clicked_at = datetime.utcnow()
        db.commit()
    
    return {"status": "success", "message": "Job click tracked"}


@router.get("/daily-digest")
def get_daily_digest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's job digest for user
    
    **Description**: Returns personalized daily job digest based on user's 
    preferences and schedule. Only includes new jobs since last digest.
    
    **Returns**: List of job recommendations for today
    """
    # Get fresh recommendations
    recommendations = get_job_recommendations(
        limit=10,
        current_user=current_user,
        db=db
    )
    
    # Get user preferences to check digest timing
    user_pref = db.query(UserJobPreference).filter(
        UserJobPreference.user_id == current_user.id
    ).first()
    
    if user_pref:
        user_pref.last_notification_sent = datetime.utcnow()
        db.commit()
    
    return {
        "digest_date": datetime.utcnow().date(),
        "total_jobs": len(recommendations),
        "jobs": recommendations,
        "notification_settings": user_pref
    }


@router.get("/stats/active")
def get_job_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get job market statistics
    
    **Description**: Returns aggregated job market stats (total jobs, by company, by location)
    
    **Returns**: Job market statistics and trends
    """
    total_jobs = db.query(JobPosting).filter(JobPosting.is_active == True).count()
    
    # Top companies (by number of job postings)
    companies = db.query(
        JobPosting.company, 
        func.count(JobPosting.id).label("count")
    ).filter(JobPosting.is_active == True).group_by(JobPosting.company).limit(10).all()
    
    # Top locations
    locations = db.query(
        JobPosting.location,
        func.count(JobPosting.id).label("count")
    ).filter(JobPosting.is_active == True).group_by(JobPosting.location).limit(10).all()
    
    return {
        "total_active_jobs": total_jobs,
        "top_companies": [{"company": c[0], "count": c[1]} for c in companies],
        "top_locations": [{"location": l[0], "count": l[1]} for l in locations],
        "timestamp": datetime.utcnow()
    }
