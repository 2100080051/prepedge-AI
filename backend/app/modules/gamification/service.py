from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import (
    User, UserGamification, UserAchievement, 
    Leaderboard, InterviewSession, StudySession
)
from typing import Dict, List, Optional


class GamificationService:
    """Service for managing user gamification - XP, levels, streaks, achievements"""
    
    # XP Rewards
    XP_REWARDS = {
        "interview_completed": 100,
        "interview_perfect_score": 250,
        "study_session_completed": 50,
        "study_streak_milestone": 200,
        "resume_reviewed": 75,
        "achievement_unlocked": 50,
        "daily_login": 10,
        "placement_logged": 50,
        "placement_verified": 50
    }
    
    # Level progression: each level requires 1.1x previous threshold
    BASE_LEVEL_THRESHOLD = 1000
    LEVEL_MULTIPLIER = 1.1
    
    @staticmethod
    def add_xp(user_id: int, activity: str, db: Session) -> Dict:
        """
        Add XP to user for completing an activity
        Returns: {success, new_xp, new_level, level_up, xp_gained}
        """
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not gamification:
            gamification = UserGamification(
                user_id=user_id,
                total_xp=0,
                current_xp=0,
                level=1
            )
            db.add(gamification)
            db.commit()
        
        xp_gained = GamificationService.XP_REWARDS.get(activity, 0)
        old_level = gamification.level
        
        # Add XP to current level
        gamification.current_xp += xp_gained
        gamification.total_xp += xp_gained
        
        # Check for level up
        level_up = False
        threshold = GamificationService._get_level_threshold(old_level)
        
        while gamification.current_xp >= threshold:
            gamification.current_xp -= threshold
            gamification.level += 1
            threshold = GamificationService._get_level_threshold(gamification.level)
            level_up = True
        
        gamification.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "xp_gained": xp_gained,
            "new_xp": gamification.current_xp,
            "new_level": gamification.level,
            "level_up": level_up,
            "total_xp": gamification.total_xp
        }
    
    @staticmethod
    def update_daily_streak(user_id: int, db: Session) -> Dict:
        """
        Update user's daily streak
        Returns: {current_streak, longest_streak, streak_awarded}
        """
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not gamification:
            gamification = UserGamification(user_id=user_id)
            db.add(gamification)
            db.commit()
        
        today = datetime.utcnow().date()
        last_activity = gamification.last_activity_date
        streak_awarded = False
        
        if last_activity:
            last_date = last_activity.date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day, streak continues
                pass
            elif days_diff == 1:
                # Next day, increment streak
                gamification.current_daily_streak += 1
                streak_awarded = True
                
                # Update longest streak
                if gamification.current_daily_streak > gamification.longest_daily_streak:
                    gamification.longest_daily_streak = gamification.current_daily_streak
            else:
                # Gap > 1 day, reset streak
                gamification.current_daily_streak = 1
        else:
            # First activity
            gamification.current_daily_streak = 1
        
        gamification.last_activity_date = datetime.utcnow()
        
        # Award XP for streak milestones (7, 14, 30 days)
        if gamification.current_daily_streak in [7, 14, 30, 60, 100]:
            GamificationService.add_xp(user_id, "study_streak_milestone", db)
            GamificationService.unlock_achievement(
                user_id, 
                f"streak_{gamification.current_daily_streak}_days",
                f"{gamification.current_daily_streak}-Day Streak",
                f"Maintained a {gamification.current_daily_streak} day study streak",
                db
            )
        
        gamification.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "current_streak": gamification.current_daily_streak,
            "longest_streak": gamification.longest_daily_streak,
            "streak_awarded": streak_awarded
        }
    
    @staticmethod
    def unlock_achievement(
        user_id: int, 
        achievement_id: str,
        name: str,
        description: str,
        db: Session,
        xp_reward: int = 50
    ) -> Dict:
        """
        Unlock an achievement for a user
        Returns: {success, already_earned, achievement}
        """
        # Check if already earned
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_name == name
        ).first()
        
        if existing:
            return {
                "success": False,
                "already_earned": True,
                "message": "Achievement already earned"
            }
        
        # Create achievement
        achievement = UserAchievement(
            user_id=user_id,
            achievement_name=name,
            achievement_type="badge",
            description=description,
            xp_reward=xp_reward,
            earned_at=datetime.utcnow()
        )
        db.add(achievement)
        
        # Update gamification stats
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        if gamification:
            gamification.total_achievements += 1
        
        # Award XP
        GamificationService.add_xp(user_id, "achievement_unlocked", db)
        
        db.commit()
        
        return {
            "success": True,
            "already_earned": False,
            "achievement": {
                "name": name,
                "description": description,
                "xp_reward": xp_reward,
                "earned_at": achievement.earned_at
            }
        }
    
    @staticmethod
    def record_interview_completion(
        user_id: int,
        interview_score: float,
        db: Session
    ) -> Dict:
        """
        Record that user completed an interview
        Returns: {xp_gained, achievements_unlocked}
        """
        result = {"xp_gained": 0, "achievements_unlocked": []}
        
        # Add base XP
        xp_result = GamificationService.add_xp(user_id, "interview_completed", db)
        result["xp_gained"] = xp_result["xp_gained"]
        
        # Bonus for perfect score
        if interview_score >= 95:
            bonus_result = GamificationService.add_xp(user_id, "interview_perfect_score", db)
            result["xp_gained"] += bonus_result["xp_gained"]
            result["achievements_unlocked"].append("Perfect Interview Score")
        
        # Update stats
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if gamification:
            gamification.interviews_completed += 1
            current_avg = gamification.average_interview_score
            new_avg = (
                (current_avg * (gamification.interviews_completed - 1) + interview_score) / 
                gamification.interviews_completed
            )
            gamification.average_interview_score = new_avg
            
            # Check for interview milestones (5, 10, 25, 50 interviews)
            if gamification.interviews_completed in [5, 10, 25, 50]:
                achievement_name = f"Interview {gamification.interviews_completed} Times"
                achv = GamificationService.unlock_achievement(
                    user_id,
                    f"interview_{gamification.interviews_completed}",
                    achievement_name,
                    f"Completed {gamification.interviews_completed} interview sessions",
                    db
                )
                if achv.get("success"):
                    result["achievements_unlocked"].append(achievement_name)
        
        # Daily streak update
        GamificationService.update_daily_streak(user_id, db)
        
        return result
    
    @staticmethod
    def record_study_session(
        user_id: int,
        duration_minutes: int,
        db: Session
    ) -> Dict:
        """
        Record that user completed a study session
        Returns: {xp_gained, achievements_unlocked}
        """
        result = {"xp_gained": 0, "achievements_unlocked": []}
        
        # Add XP based on duration (1 XP per 5 minutes, min 50)
        xp_result = GamificationService.add_xp(user_id, "study_session_completed", db)
        result["xp_gained"] = xp_result["xp_gained"]
        
        # Update stats
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if gamification:
            gamification.study_sessions_completed += 1
            gamification.total_study_minutes += duration_minutes
            
            # Check for study milestones
            if gamification.study_sessions_completed in [10, 25, 50]:
                achievement_name = f"Study Session {gamification.study_sessions_completed}"
                achv = GamificationService.unlock_achievement(
                    user_id,
                    f"study_{gamification.study_sessions_completed}",
                    achievement_name,
                    f"Completed {gamification.study_sessions_completed} study sessions",
                    db
                )
                if achv.get("success"):
                    result["achievements_unlocked"].append(achievement_name)
        
        # Daily streak update
        GamificationService.update_daily_streak(user_id, db)
        
        return result
    
    @staticmethod
    def get_user_stats(user_id: int, db: Session) -> Dict:
        """Get comprehensive gamification stats for user"""
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not gamification:
            return {"error": "User not found"}
        
        achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).order_by(UserAchievement.earned_at.desc()).all()
        
        # Calculate XP to next level
        current_threshold = GamificationService._get_level_threshold(gamification.level)
        xp_to_next = current_threshold - gamification.current_xp
        
        return {
            "level": gamification.level,
            "total_xp": gamification.total_xp,
            "current_xp": gamification.current_xp,
            "xp_to_next_level": xp_to_next,
            "level_progress": (gamification.current_xp / current_threshold) * 100,
            "daily_streak": gamification.current_daily_streak,
            "longest_streak": gamification.longest_daily_streak,
            "last_activity": gamification.last_activity_date,
            "interviews_completed": gamification.interviews_completed,
            "average_interview_score": round(gamification.average_interview_score, 2),
            "study_sessions": gamification.study_sessions_completed,
            "total_study_minutes": gamification.total_study_minutes,
            "achievements": [
                {
                    "name": a.achievement_name,
                    "description": a.description,
                    "earned_at": a.earned_at,
                    "xp_reward": a.xp_reward
                }
                for a in achievements
            ],
            "total_achievements": len(achievements),
            "global_rank": gamification.global_rank,
            "monthly_rank": gamification.monthly_rank
        }
    
    @staticmethod
    def get_leaderboard(
        limit: int = 100, 
        period: str = "global",
        db: Session = None
    ) -> List[Dict]:
        """
        Get leaderboard rankings
        period: "global", "weekly", "monthly"
        """
        if period == "global":
            leaderboard = db.query(Leaderboard).order_by(
                Leaderboard.global_rank
            ).limit(limit).all()
        else:  # monthly
            leaderboard = db.query(Leaderboard).order_by(
                Leaderboard.monthly_rank
            ).limit(limit).all()
        
        return [
            {
                "rank": lb.global_rank if period == "global" else lb.monthly_rank,
                "username": lb.username,
                "level": lb.level,
                "total_xp": lb.total_xp,
                "streak": lb.current_streak,
                "interviews": lb.interviews_completed,
                "achievements": lb.total_achievements
            }
            for lb in leaderboard
        ]
    
    @staticmethod
    def update_leaderboard(db: Session) -> None:
        """Recalculate leaderboard rankings (run periodically)"""
        # Get all users sorted by XP
        users = db.query(
            UserGamification.user_id,
            UserGamification.total_xp,
            UserGamification.level,
            UserGamification.current_daily_streak,
            UserGamification.interviews_completed,
            UserGamification.total_achievements,
            User.username
        ).join(User).order_by(UserGamification.total_xp.desc()).all()
        
        for rank, (user_id, xp, level, streak, interviews, achievements, username) in enumerate(users, 1):
            leaderboard = db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id
            ).first()
            
            if leaderboard:
                leaderboard.global_rank = rank
                leaderboard.total_xp = xp
                leaderboard.level = level
                leaderboard.current_streak = streak
                leaderboard.interviews_completed = interviews
                leaderboard.total_achievements = achievements
            else:
                leaderboard = Leaderboard(
                    user_id=user_id,
                    username=username,
                    global_rank=rank,
                    total_xp=xp,
                    level=level,
                    current_streak=streak,
                    interviews_completed=interviews,
                    total_achievements=achievements
                )
                db.add(leaderboard)
        
        db.commit()
    
    @staticmethod
    def _get_level_threshold(level: int) -> int:
        """Calculate XP threshold for next level"""
        return int(
            GamificationService.BASE_LEVEL_THRESHOLD * 
            (GamificationService.LEVEL_MULTIPLIER ** (level - 1))
        )
