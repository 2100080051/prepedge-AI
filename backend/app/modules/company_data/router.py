"""
Company Data Routes
API endpoints for real-time company interview questions, job openings, and salary data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.company_data.service import CompanyDataService
from app.modules.company_data.job_recommendation import JobRecommendationService
from app.auth.dependencies import get_current_user
from typing import Optional, List

router = APIRouter(prefix="/company-data", tags=["company-data"])

@router.get("/trending")
async def get_trending_companies(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get trending companies with most activity
    
    Shows companies with:
    - Most tracked interviews
    - Highest placement rates
    - Latest job openings
    """
    try:
        companies = CompanyDataService.get_trending_companies(db, limit)
        return {
            "status": "success",
            "trending_companies": companies,
            "total": len(companies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/profile")
async def get_company_profile(
    company_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive company profile
    
    Returns:
    - Company info & statistics
    - Hiring pace
    - Average interview rounds
    - Placement rate
    - Popular roles
    - Avg compensation
    """
    try:
        # Track user interest
        CompanyDataService.track_user_company_interest(
            db, current_user.id, company_name
        )
        
        profile = CompanyDataService.get_company_profile(db, company_name)
        if not profile:
            raise HTTPException(status_code=404, detail="Company not found")
        
        stats = CompanyDataService.get_company_statistics(db, company_name)
        
        return {
            "status": "success",
            "company": profile,
            "statistics": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/questions")
async def get_company_questions(
    company_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    role: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get real interview questions asked at a company
    
    Features:
    - Real questions from current/past employees
    - Frequency indicators (how often asked)
    - Success rates from users who practiced
    - Verification count (how many confirmed)
    - Topic breakdown
    - Round type (Technical, System Design, HR, etc.)
    
    Data sources:
    - User submissions (verified)
    - Glassdoor sync
    - LeetCode
    - Blind forum aggregation
    """
    try:
        CompanyDataService.track_user_company_interest(
            db, current_user.id, company_name
        )
        
        questions = CompanyDataService.get_company_questions(
            db, company_name, role, difficulty, limit
        )
        
        if not questions:
            raise HTTPException(
                status_code=404, 
                detail=f"No questions found for {company_name}"
            )
        
        return {
            "status": "success",
            "company": company_name,
            "total_questions": len(questions),
            "questions": questions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/salary")
async def get_salary_data(
    company_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    role: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None)
):
    """
    Get verified salary data for a company
    
    Salary breakdown:
    - Base salary (min/avg/max)
    - Bonus percentage
    - Stock options
    - Total compensation
    
    By role and seniority level:
    - Software Engineer (Fresher, Junior, Senior, Staff)
    - Product Manager
    - Data Science / ML
    - Other roles
    
    Data sources:
    - Levels.fyi verified submissions
    - Blind forum (real employees)
    - User verified offer letters
    - Glassdoor salary reports
    """
    try:
        CompanyDataService.track_user_company_interest(
            db, current_user.id, company_name
        )
        
        salaries = CompanyDataService.get_salary_data(
            db, company_name, role, seniority
        )
        
        if not salaries:
            return {
                "status": "success",
                "company": company_name,
                "message": "No salary data available yet. Help community by sharing verified data!",
                "data": []
            }
        
        return {
            "status": "success",
            "company": company_name,
            "salary_data": salaries,
            "note": "Salaries are converted to USD. Actual numbers vary by location and year."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_name}/jobs")
async def get_job_openings(
    company_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    role: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get active job openings at a company
    
    Includes:
    - Job title and role
    - Seniority level
    - Location (remote/onsite/hybrid)
    - Required & preferred skills
    - Salary range
    - Links to apply
    
    Data sources:
    - LinkedIn
    - Company career pages
    - Glassdoor
    """
    try:
        CompanyDataService.track_user_company_interest(
            db, current_user.id, company_name
        )
        
        jobs = CompanyDataService.get_active_job_openings(
            db, company_name, role, limit
        )
        
        return {
            "status": "success",
            "company": company_name,
            "total_openings": len(jobs),
            "job_openings": jobs,
            "note": "Data last updated today. Check company careers page for latest."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{company_name}/questions/submit")
async def submit_company_question(
    company_name: str,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit an interview question you encountered
    
    Help other candidates by sharing real questions you encountered!
    
    Required:
    - question: The interview question text
    - topic: DSA, System Design, Behavioral, etc.
    - difficulty: easy, medium, hard
    - round_type: Phone Screen, Technical, System Design, HR
    - role: SDE, PM, Data Science, etc.
    
    This data helps:
    - Other candidates prepare for this company
    - Identify trending topics
    - Track company interview patterns
    """
    try:
        success = CompanyDataService.add_company_question(
            db,
            company_name=company_name,
            question_text=question_data.get("question"),
            topic=question_data.get("topic"),
            difficulty=question_data.get("difficulty"),
            round_type=question_data.get("round_type"),
            role=question_data.get("role"),
            source="User Submission"
        )
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Failed to submit question. Company might not exist."
            )
        
        return {
            "status": "success",
            "message": "Question submitted! Thank you for helping the community.",
            "next": "Your question will be verified by other community members"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/personalized")
async def get_personalized_job_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get personalized job recommendations based on user profile
    
    Personalization factors:
    - Years of experience (matches seniority level)
    - College/Education
    - Course/Major
    - Job interest history
    - Company placement rates and ratings
    
    Returns jobs with match scores indicating how well they fit your profile
    """
    try:
        recommendations = JobRecommendationService.get_personalized_recommendations(
            db, current_user.id, limit
        )
        
        return {
            "status": "success",
            "total_recommendations": len(recommendations),
            "user_profile": {
                "college": current_user.college,
                "course": current_user.course,
                "years_of_experience": current_user.years_of_experience,
                "seniority_level": JobRecommendationService._get_seniority_level(current_user.years_of_experience)
            },
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_companies(
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Search for companies by name
    
    Returns matching companies with:
    - Company info
    - Number of tracked interviews
    - Placement rate
    - Average rating
    """
    try:
        from sqlalchemy import and_
        # Search similar companies
        companies = db.query(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(f"%{query}%")
        ).limit(20).all()
        
        if not companies:
            return {
                "status": "success",
                "query": query,
                "results": [],
                "message": "No companies found. You could be the first to share interview data!"
            }
        
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "name": c.company_name,
                    "industry": c.industry,
                    "interviews_tracked": c.total_interviews_tracked,
                    "placement_rate": c.placement_rate,
                    "rating": c.average_rating
                }
                for c in companies
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
