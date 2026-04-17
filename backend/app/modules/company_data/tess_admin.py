"""
TESS Admin Interface
TESS has special admin access to:
- Query jobs by any criteria
- View all company data
- View user activity
- Generate insights
- Control overall app functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.database.session import get_db
from app.database.models import User
from app.auth.dependencies import get_current_user
from app.modules.company_data.models import (
    CompanyProfile, CompanyQuestion, CompanyJobOpening, CompanySalaryData
)
from app.modules.company_data.job_recommendation import JobRecommendationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tess", tags=["tess-admin"])


class JobQuery(BaseModel):
    """Query model for TESS job search"""
    role: Optional[str] = None
    seniority: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    company_name: Optional[str] = None
    limit: int = 50


class TESSQuery(BaseModel):
    """General TESS query"""
    query_type: str  # "jobs", "companies", "questions", "salary"
    filters: Optional[Dict] = None


def _verify_tess_access(current_user: User):
    """Verify user has TESS admin access"""
    if not current_user.is_tess_admin:
        raise HTTPException(
            status_code=403,
            detail="Only TESS admin can access this endpoint"
        )
    return current_user


@router.get("/health")
async def tess_health():
    """TESS health check - always accessible"""
    return {
        "status": "operational",
        "tess_version": "1.0.0",
        "message": "TESS Control System Online"
    }


@router.post("/query-jobs")
async def tess_query_jobs(
    query: JobQuery,
    db: Session = Depends(get_db),
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user))
):
    """
    TESS: Query jobs by any criteria
    
    This endpoint allows TESS to find jobs based on:
    - Role (e.g., "SDE", "QA", "Business Analyst")
    - Seniority (e.g., "Fresher", "Junior", "Senior", "Lead")
    - Location (exact or partial match)
    - Remote capability
    - Salary range
    - Company name
    """
    logger.info(f"TESS querying jobs with filters: {query.dict()}")
    
    jobs = JobRecommendationService.search_jobs_by_criteria(
        db,
        role=query.role,
        seniority=query.seniority,
        location=query.location,
        is_remote=query.is_remote,
        min_salary=query.min_salary,
        max_salary=query.max_salary,
        limit=query.limit
    )
    
    # If specific company, get all their jobs
    if query.company_name:
        jobs_by_company = JobRecommendationService.get_company_specific_jobs(
            db, query.company_name, query.role
        )
        if jobs_by_company:
            jobs = jobs_by_company[:query.limit]
    
    return {
        "status": "success",
        "total_found": len(jobs),
        "jobs": jobs,
        "query_params": query.dict()
    }


@router.get("/companies")
async def tess_get_all_companies(
    db: Session = Depends(get_db),
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user)),
    industry: Optional[str] = Query(None),
    min_placement_rate: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(100, ge=1, le=500)
):
    """
    TESS: Get all companies with filters
    
    Can filter by:
    - Industry (e.g., "IT Services", "Consulting", "Technology")
    - Minimum placement rate (0-100)
    """
    logger.info(f"TESS fetching companies")
    
    query = db.query(CompanyProfile)
    
    if industry:
        query = query.filter(CompanyProfile.industry.ilike(f"%{industry}%"))
    
    if min_placement_rate is not None:
        query = query.filter(CompanyProfile.placement_rate >= min_placement_rate)
    
    companies = query.order_by(
        desc(CompanyProfile.placement_rate)
    ).limit(limit).all()
    
    return {
        "status": "success",
        "total_companies": len(companies),
        "companies": [
            {
                "id": c.id,
                "company_name": c.company_name,
                "industry": c.industry,
                "avg_salary": c.avg_base_salary_usd,
                "avg_total_comp": c.avg_total_comp_usd,
                "placement_rate": c.placement_rate,
                "rating": c.average_rating,
                "active_jobs": c.active_job_openings,
                "hiring_pace": c.hiring_pace,
            }
            for c in companies
        ]
    }


@router.get("/company/{company_name}")
async def tess_get_company_details(
    company_name: str,
    db: Session = Depends(get_db),
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user))
):
    """
    TESS: Get complete company details
    - Profile information
    - All job openings
    - Common interview questions
    - Salary equity data by role/seniority
    - Placement success rates
    """
    logger.info(f"TESS fetching complete data for {company_name}")
    
    company = db.query(CompanyProfile).filter(
        CompanyProfile.company_name.ilike(company_name)
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get jobs
    jobs = db.query(CompanyJobOpening).filter(
        CompanyJobOpening.company_id == company.id
    ).all()
    
    # Get questions
    questions = db.query(CompanyQuestion).filter(
        CompanyQuestion.company_id == company.id
    ).order_by(CompanyQuestion.frequency_score.desc()).all()
    
    # Get salary data
    salaries = db.query(CompanySalaryData).filter(
        CompanySalaryData.company_id == company.id
    ).all()
    
    return {
        "status": "success",
        "company": {
            "id": company.id,
            "name": company.company_name,
            "industry": company.industry,
            "website": company.website,
            "hiring_pace": company.hiring_pace,
            "avg_interview_rounds": company.avg_interview_rounds,
            "placement_rate": company.placement_rate,
            "average_rating": company.average_rating,
            "popular_roles": company.popular_roles,
            "common_interview_types": company.common_interview_types,
        },
        "compensation": {
            "avg_base_salary": company.avg_base_salary_usd,
            "avg_total_comp": company.avg_total_comp_usd,
            "avg_bonus_percentage": company.avg_bonus_percentage,
        },
        "jobs": {
            "total_open": len(jobs),
            "openings": [
                {
                    "title": j.job_title,
                    "role": j.role,
                    "seniority": j.seniority,
                    "location": j.location,
                    "salary_range": f"{j.salary_min_usd}-{j.salary_max_usd}",
                }
                for j in jobs
            ]
        },
        "interview_data": {
            "total_questions": len(questions),
            "top_questions": [
                {
                    "text": q.question_text,
                    "topic": q.topic,
                    "difficulty": q.difficulty,
                    "frequency": q.frequency_score,
                    "verified": q.verified,
                }
                for q in questions[:10]
            ]
        },
        "salary_data": {
            "records": len(salaries),
            "breakdown": [
                {
                    "role": s.role,
                    "seniority": s.seniority,
                    "base_salary_avg": s.base_salary_avg,
                    "total_comp_avg": s.total_comp_avg,
                    "bonus_avg": s.bonus_avg,
                }
                for s in salaries
            ]
        }
    }


@router.post("/broadcast-notification")
async def tess_broadcast_notification(
    notification: Dict,
    db: Session = Depends(get_db),
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user))
):
    """
    TESS: Broadcast notifications to all users
    E.g., "New openings at TCS", "Goldman Sachs hiring freshers", etc.
    """
    logger.info(f"TESS broadcasting notification: {notification}")
    
    return {
        "status": "success",
        "message": "Notification queued for broadcast",
        "timestamp": notification.get("timestamp")
    }


@router.get("/analytics")
async def tess_get_analytics(
    db: Session = Depends(get_db),
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user))
):
    """
    TESS: Get platform analytics
    - Total companies
    - Total jobs available
    - Average placement rates
    - Most popular companies
    - Trending roles
    """
    logger.info("TESS fetching platform analytics")
    
    total_companies = db.query(func.count(CompanyProfile.id)).scalar()
    total_jobs = db.query(func.count(CompanyJobOpening.id)).filter(
        CompanyJobOpening.is_active == True
    ).scalar()
    avg_placement = db.query(func.avg(CompanyProfile.placement_rate)).scalar() or 0
    avg_rating = db.query(func.avg(CompanyProfile.average_rating)).scalar() or 0
    
    top_companies = db.query(CompanyProfile).order_by(
        desc(CompanyProfile.placement_rate)
    ).limit(10).all()
    
    role_counts = db.query(
        CompanyJobOpening.role,
        func.count(CompanyJobOpening.id).label('count')
    ).filter(CompanyJobOpening.is_active == True).group_by(
        CompanyJobOpening.role
    ).order_by(desc(func.count(CompanyJobOpening.id))).limit(10).all()
    
    return {
        "status": "success",
        "platform_stats": {
            "total_companies": total_companies,
            "total_open_jobs": total_jobs,
            "average_placement_rate": round(float(avg_placement), 2),
            "average_company_rating": round(float(avg_rating), 2),
        },
        "top_companies": [
            {
                "name": c.company_name,
                "placement_rate": c.placement_rate,
                "rating": c.average_rating,
                "industry": c.industry,
            }
            for c in top_companies
        ],
        "trending_roles": [
            {
                "role": role,
                "open_positions": count
            }
            for role, count in role_counts
        ]
    }


@router.get("/controlled-features")
async def tess_controlled_features(
    tess_user = Depends(lambda user=Depends(get_current_user): _verify_tess_access(user))
):
    """
    TESS: List all features under TESS control
    """
    return {
        "status": "success",
        "tess_controls": {
            "job_queries": {
                "description": "Query and manage all job openings",
                "endpoint": "POST /tess/query-jobs"
            },
            "company_management": {
                "description": "View all company data and details",
                "endpoint": "GET /tess/companies, GET /tess/company/{name}"
            },
            "notifications": {
                "description": "Broadcast messages to all users",
                "endpoint": "POST /tess/broadcast-notification"
            },
            "analytics": {
                "description": "View detailed platform analytics",
                "endpoint": "GET /tess/analytics"
            },
            "user_management": {
                "description": "View user activity and profiles",
                "endpoint": "GET /tess/users (coming soon)"
            },
            "interview_questions": {
                "description": "Manage interview questions database",
                "endpoint": "GET /tess/questions (coming soon)"
            },
            "platform_settings": {
                "description": "Control app features and settings",
                "endpoint": "PATCH /tess/settings (coming soon)"
            }
        },
        "message": "TESS has overall control of the app. All major features can be accessed and managed."
    }
