from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.dashboard.service import DashboardService
from typing import Dict

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_overview_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get overview dashboard with key metrics
    - Current level, XP, rank, streak
    - This week's activities (interviews, study, resumes)
    - Progress to next level
    - Weekly targets
    """
    try:
        data = DashboardService.get_overview(current_user.id, db)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/interviews")
async def get_interview_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get interview performance analytics
    - Total interviews, average/best score
    - Score trend over time
    - Performance improvement
    """
    if days <= 0 or days > 365:
        days = 30
    
    try:
        data = DashboardService.get_interview_analytics(current_user.id, db, days)
        return {
            "success": True,
            "period_days": days,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/study")
async def get_study_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get study session analytics
    - Total study time, number of sessions
    - Topics studied with breakdown
    - Daily study time pattern
    """
    if days <= 0 or days > 365:
        days = 30
    
    try:
        data = DashboardService.get_study_analytics(current_user.id, db, days)
        return {
            "success": True,
            "period_days": days,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/resume")
async def get_resume_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get resume score analytics
    - Resume upload history with scores
    - Score improvement over time
    - ATS scores by role/company
    """
    try:
        data = DashboardService.get_resume_analytics(current_user.id, db)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/skills")
async def get_skill_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get skills and concepts breakdown
    - Skills studied with time and performance
    - Mastery levels (Beginner, Intermediate, Advanced, Expert)
    - Companies' skill requirements coverage
    """
    try:
        data = DashboardService.get_skill_breakdown(current_user.id, db)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals")
async def get_goals_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get progress towards goals
    - Level 50 goal
    - 100 interviews goal
    - 500 study hours goal
    - 50 achievements goal
    - Overall progress percentage
    """
    try:
        data = DashboardService.get_goals_progress(current_user.id, db)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/full")
async def get_full_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get complete dashboard with all metrics
    Combines: overview, interviews, study, resume, skills, goals
    """
    try:
        data = DashboardService.get_full_dashboard(current_user.id, db)
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
