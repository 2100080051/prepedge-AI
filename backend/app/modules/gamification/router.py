from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.gamification.service import GamificationService
from typing import Dict, List

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.post("/add-xp")
async def add_xp(
    activity: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Add XP to user for an activity
    Activities: interview_completed, study_session_completed, resume_reviewed, etc.
    """
    try:
        result = GamificationService.add_xp(current_user.id, activity, db)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/daily-check-in")
async def daily_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Daily check-in for streak tracking and bonus XP
    Automatically awards daily login XP
    """
    try:
        # Award daily login XP
        xp_result = GamificationService.add_xp(current_user.id, "daily_login", db)
        
        # Update streak
        streak_result = GamificationService.update_daily_streak(current_user.id, db)
        
        return {
            "success": True,
            "xp_gained": xp_result["xp_gained"],
            "streak": streak_result["current_streak"],
            "new_level": xp_result["new_level"],
            "level_up": xp_result["level_up"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/record-interview")
async def record_interview(
    score: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Record interview completion and award XP
    Score: 0-100
    """
    if not 0 <= score <= 100:
        raise HTTPException(status_code=400, detail="Score must be between 0-100")
    
    try:
        result = GamificationService.record_interview_completion(
            current_user.id,
            score,
            db
        )
        user_stats = GamificationService.get_user_stats(current_user.id, db)
        
        return {
            "success": True,
            "xp_gained": result["xp_gained"],
            "achievements_unlocked": result["achievements_unlocked"],
            "user_stats": user_stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/record-study-session")
async def record_study_session(
    duration_minutes: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Record study session completion and award XP
    Duration: minutes spent studying
    """
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="Duration must be positive")
    
    try:
        result = GamificationService.record_study_session(
            current_user.id,
            duration_minutes,
            db
        )
        user_stats = GamificationService.get_user_stats(current_user.id, db)
        
        return {
            "success": True,
            "xp_gained": result["xp_gained"],
            "achievements_unlocked": result["achievements_unlocked"],
            "user_stats": user_stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user-stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get comprehensive gamification statistics for current user
    Includes: level, XP, streaks, achievements, rankings
    """
    try:
        stats = GamificationService.get_user_stats(current_user.id, db)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 100,
    period: str = "global",
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get leaderboard rankings
    period: "global" (all-time) or "monthly"
    """
    if period not in ["global", "monthly"]:
        raise HTTPException(status_code=400, detail="Period must be 'global' or 'monthly'")
    
    if limit > 1000:
        limit = 1000
    
    try:
        leaderboard = GamificationService.get_leaderboard(limit, period, db)
        
        return {
            "success": True,
            "period": period,
            "count": len(leaderboard),
            "data": leaderboard
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unlock-achievement")
async def unlock_achievement(
    achievement_id: str,
    achievement_name: str,
    description: str,
    xp_reward: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Unlock an achievement (internal use)
    """
    try:
        result = GamificationService.unlock_achievement(
            current_user.id,
            achievement_id,
            achievement_name,
            description,
            db,
            xp_reward
        )
        return {
            "success": result["success"],
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/streak-info")
async def get_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get detailed streak information
    """
    try:
        stats = GamificationService.get_user_stats(current_user.id, db)
        
        return {
            "success": True,
            "current_streak": stats["daily_streak"],
            "longest_streak": stats["longest_streak"],
            "last_activity": stats["last_activity"],
            "streak_xp": 200,  # XP earned at milestone streaks
            "milestones": [7, 14, 30, 60, 100]  # Days when bonus XP is awarded
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-leaderboard")
async def update_leaderboard_rankings(
    db: Session = Depends(get_db)
) -> Dict:
    """
    Manually trigger leaderboard recalculation
    (Should be called by scheduler, not by users)
    """
    try:
        GamificationService.update_leaderboard(db)
        return {
            "success": True,
            "message": "Leaderboard updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
