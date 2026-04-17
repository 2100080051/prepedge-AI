from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import (
    User, UserGamification, InterviewSession, StudySession, 
    ResumeUpload, ResumeFeedback, Flashcard
)
from typing import Dict, List, Optional
import statistics


class DashboardService:
    """Service for generating performance and analytics dashboards"""
    
    @staticmethod
    def get_overview(user_id: int, db: Session) -> Dict:
        """
        Get overview dashboard with key metrics
        """
        # User gamification stats
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not gamification:
            return {"error": "User not found"}
        
        # Get recent accomplishments
        interviews_this_week = db.query(func.count(InterviewSession.id)).filter(
            InterviewSession.user_id == user_id,
            InterviewSession.created_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar()
        
        study_hours_this_week = db.query(func.sum(StudySession.duration_minutes)).filter(
            StudySession.user_id == user_id,
            StudySession.created_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar() or 0
        
        resumes_reviewed = db.query(func.count(ResumeFeedback.id)).filter(
            ResumeFeedback.resume_id.in_(
                db.query(ResumeUpload.id).filter(ResumeUpload.user_id == user_id)
            )
        ).scalar()
        
        # Calculate progress to next level
        current_level = gamification.level
        current_xp = gamification.current_xp
        threshold = DashboardService._get_level_threshold(current_level)
        level_progress = (current_xp / threshold) * 100
        
        return {
            "profile": {
                "level": gamification.level,
                "total_xp": gamification.total_xp,
                "rank": gamification.global_rank,
                "streak": gamification.current_daily_streak
            },
            "this_week": {
                "interviews": interviews_this_week,
                "study_hours": round(study_hours_this_week / 60, 1),
                "resumes_reviewed": resumes_reviewed
            },
            "progress": {
                "level_completion": round(level_progress, 1),
                "xp_to_next_level": threshold - current_xp
            },
            "targets": {
                "weekly_interviews": 5,
                "weekly_study_hours": 10,
                "monthly_achievements": 5,
                "streak_goal": 30
            }
        }
    
    @staticmethod
    def get_interview_analytics(user_id: int, db: Session, days: int = 30) -> Dict:
        """
        Get interview performance analytics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        interviews = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id,
            InterviewSession.created_at >= cutoff_date,
            InterviewSession.status == "completed"
        ).all()
        
        if not interviews:
            return {
                "total_interviews": 0,
                "average_score": 0,
                "best_score": 0,
                "improvement": 0,
                "trend": []
            }
        
        scores = [i.score for i in interviews]
        
        # Calculate trend
        trend = []
        for interview in sorted(interviews, key=lambda x: x.created_at):
            trend.append({
                "date": interview.created_at.date().isoformat(),
                "score": interview.score,
                "company": interview.company,
                "role": interview.role
            })
        
        # Calculate improvement
        if len(scores) > 1:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            improvement = (
                statistics.mean(second_half) - statistics.mean(first_half)
            )
        else:
            improvement = 0
        
        return {
            "total_interviews": len(interviews),
            "average_score": round(statistics.mean(scores), 1),
            "best_score": max(scores),
            "worst_score": min(scores),
            "improvement": round(improvement, 1),
            "median_score": round(statistics.median(scores), 1),
            "trend": trend
        }
    
    @staticmethod
    def get_study_analytics(user_id: int, db: Session, days: int = 30) -> Dict:
        """
        Get study session analytics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.created_at >= cutoff_date
        ).all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_minutes": 0,
                "average_session_length": 0,
                "topics_studied": [],
                "daily_breakdown": {}
            }
        
        # Calculate metrics
        total_minutes = sum(s.duration_minutes for s in sessions)
        avg_session = round(total_minutes / len(sessions), 1)
        
        # Topics breakdown
        topics = {}
        for session in sessions:
            if session.topic not in topics:
                topics[session.topic] = {"minutes": 0, "sessions": 0}
            topics[session.topic]["minutes"] += session.duration_minutes
            topics[session.topic]["sessions"] += 1
        
        topics_studied = [
            {
                "topic": topic,
                "minutes": data["minutes"],
                "sessions": data["sessions"],
                "avg_per_session": round(data["minutes"] / data["sessions"], 1)
            }
            for topic, data in topics.items()
        ]
        
        # Daily breakdown
        daily = {}
        for session in sessions:
            date = session.created_at.date().isoformat()
            if date not in daily:
                daily[date] = 0
            daily[date] += session.duration_minutes
        
        return {
            "total_sessions": len(sessions),
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "average_session_length": avg_session,
            "topics_studied": sorted(topics_studied, key=lambda x: x["minutes"], reverse=True),
            "daily_breakdown": daily
        }
    
    @staticmethod
    def get_resume_analytics(user_id: int, db: Session) -> Dict:
        """
        Get resume score and feedback analytics
        """
        resumes = db.query(ResumeUpload).filter(
            ResumeUpload.user_id == user_id
        ).order_by(desc(ResumeUpload.created_at)).all()
        
        if not resumes:
            return {
                "total_resumes": 0,
                "highest_score": 0,
                "average_score": 0,
                "latest_score": 0,
                "improvement": 0,
                "history": []
            }
        
        # Get feedback for each resume
        scores = []
        history = []
        
        for resume in resumes:
            feedback = db.query(ResumeFeedback).filter(
                ResumeFeedback.resume_id == resume.id
            ).first()
            
            score = feedback.overall_score if feedback else 0
            scores.append(score)
            
            history.append({
                "resume_id": resume.id,
                "created": resume.created_at.date().isoformat(),
                "score": score,
                "company": resume.target_company,
                "role": resume.target_role,
                "ats_score": feedback.ats_score if feedback else 0
            })
        
        # Calculate improvement
        if len(scores) > 1:
            improvement = scores[0] - scores[-1]  # Latest minus oldest
        else:
            improvement = 0
        
        return {
            "total_resumes": len(resumes),
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "average_score": round(statistics.mean(scores), 1) if scores else 0,
            "latest_score": scores[0] if scores else 0,
            "improvement": round(improvement, 1),
            "history": history
        }
    
    @staticmethod
    def get_skill_breakdown(user_id: int, db: Session) -> Dict:
        """
        Get breakdown of skills/concepts studied
        Aggregated from study sessions and flashcards
        """
        # Get topics from study sessions
        topics_query = db.query(
            StudySession.topic,
            func.count(StudySession.id).label("sessions"),
            func.sum(StudySession.duration_minutes).label("minutes"),
            func.avg(StudySession.performance).label("avg_performance")
        ).filter(
            StudySession.user_id == user_id
        ).group_by(StudySession.topic).all()
        
        skills = {}
        for topic, sessions, minutes, performance in topics_query:
            skills[topic] = {
                "sessions": sessions,
                "minutes": minutes or 0,
                "performance": round(performance or 0, 1),
                "mastery_level": DashboardService._get_mastery_level(
                    minutes or 0, performance or 0
                )
            }
        
        # Get flashcard data by company
        flashcards_query = db.query(
            Flashcard.company,
            func.count(Flashcard.id).label("total"),
            func.sum(func.cast(Flashcard.difficulty == 'hard', func.Integer)).label("hard_count")
        ).group_by(Flashcard.company).all()
        
        companies_breakdown = {}
        for company, total, hard_count in flashcards_query:
            companies_breakdown[company] = {
                "total_flashcards": total,
                "hard_flashcards": hard_count or 0,
                "coverage": f"{(hard_count or 0) / total * 100:.0f}%" if total > 0 else "0%"
            }
        
        return {
            "skills_breakdown": skills,
            "companies_breakdown": companies_breakdown,
            "total_unique_skills": len(skills),
            "total_unique_companies": len(companies_breakdown)
        }
    
    @staticmethod
    def get_goals_progress(user_id: int, db: Session) -> Dict:
        """
        Get progress towards user goals
        """
        gamification = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        # Goals
        level_goal = 50
        interview_goal = 100
        study_hours_goal = 500
        achievement_goal = 50
        
        return {
            "goals": {
                "level_50": {
                    "target": level_goal,
                    "current": gamification.level if gamification else 0,
                    "progress": (gamification.level / level_goal * 100 if gamification else 0)
                },
                "100_interviews": {
                    "target": interview_goal,
                    "current": gamification.interviews_completed if gamification else 0,
                    "progress": (gamification.interviews_completed / interview_goal * 100 if gamification else 0)
                },
                "500_study_hours": {
                    "target": study_hours_goal,
                    "current": (gamification.total_study_minutes // 60) if gamification else 0,
                    "progress": ((gamification.total_study_minutes // 60) / study_hours_goal * 100 if gamification else 0)
                },
                "50_achievements": {
                    "target": achievement_goal,
                    "current": gamification.total_achievements if gamification else 0,
                    "progress": (gamification.total_achievements / achievement_goal * 100 if gamification else 0)
                }
            },
            "overall_progress": DashboardService._calculate_overall_progress(gamification, 
                                                                            level_goal,
                                                                            interview_goal,
                                                                            study_hours_goal,
                                                                            achievement_goal)
        }
    
    @staticmethod
    def get_full_dashboard(user_id: int, db: Session) -> Dict:
        """
        Get complete dashboard with all metrics
        """
        return {
            "overview": DashboardService.get_overview(user_id, db),
            "interview_analytics": DashboardService.get_interview_analytics(user_id, db),
            "study_analytics": DashboardService.get_study_analytics(user_id, db),
            "resume_analytics": DashboardService.get_resume_analytics(user_id, db),
            "skill_breakdown": DashboardService.get_skill_breakdown(user_id, db),
            "goals_progress": DashboardService.get_goals_progress(user_id, db),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _get_level_threshold(level: int) -> int:
        """Calculate XP threshold for next level"""
        return int(1000 * (1.1 ** (level - 1)))
    
    @staticmethod
    def _get_mastery_level(minutes: int, performance: float) -> str:
        """Determine mastery level based on time and performance"""
        if minutes < 60:
            return "Beginner"
        elif minutes < 300:
            if performance >= 70:
                return "Intermediate"
            else:
                return "Learning"
        elif minutes < 600:
            if performance >= 80:
                return "Advanced"
            else:
                return "Intermediate"
        else:
            if performance >= 85:
                return "Expert"
            else:
                return "Advanced"
    
    @staticmethod
    def _calculate_overall_progress(gamification, level_goal, interview_goal, 
                                   study_hours_goal, achievement_goal) -> float:
        """Calculate overall progress across all goals"""
        if not gamification:
            return 0
        
        level_prog = min(gamification.level / level_goal, 1.0) * 25
        interview_prog = min(gamification.interviews_completed / interview_goal, 1.0) * 25
        study_prog = min((gamification.total_study_minutes // 60) / study_hours_goal, 1.0) * 25
        achievement_prog = min(gamification.total_achievements / achievement_goal, 1.0) * 25
        
        return round(level_prog + interview_prog + study_prog + achievement_prog, 1)
