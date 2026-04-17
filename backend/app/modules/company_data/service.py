"""
Company Data Service
Fetches and manages real-time company interview questions, job openings, and salary data
"""

from sqlalchemy.orm import Session
from app.modules.company_data.models import (
    CompanyProfile, CompanyQuestion, CompanyJobOpening, 
    CompanySalaryData, UserCompanyInterest
)
import requests
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CompanyDataService:
    """Service to manage real-time company data"""
    
    # IMPORTANT COMPANIES FOR TRACKING
    TARGET_COMPANIES = [
        "Google", "Microsoft", "Amazon", "Meta", "Apple",
        "Tesla", "Netflix", "Uber", "Airbnb", "Stripe",
        "TCS", "Infosys", "Accenture", "Wipro", "Cognizant",
        "Goldman Sachs", "JP Morgan", "Morgan Stanley",
        "Oracle", "Salesforce", "Adobe"
    ]
    
    @staticmethod
    def get_company_profile(db: Session, company_name: str) -> Optional[Dict]:
        """Get company profile with latest data"""
        company = db.query(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name)
        ).first()
        
        if not company:
            return None
        
        return {
            "id": company.id,
            "company_name": company.company_name,
            "industry": company.industry,
            "hiring_pace": company.hiring_pace,
            "active_job_openings": company.active_job_openings,
            "avg_interview_rounds": company.avg_interview_rounds,
            "average_rating": company.average_rating,
            "placement_rate": company.placement_rate,
            "popular_roles": company.popular_roles,
            "common_interview_types": company.common_interview_types,
            "avg_base_salary_usd": company.avg_base_salary_usd,
            "avg_total_comp_usd": company.avg_total_comp_usd,
            "data_updated_at": company.data_updated_at
        }
    
    @staticmethod
    def get_company_questions(
        db: Session, 
        company_name: str, 
        role: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get real interview questions for a company
        
        This data comes from:
        - User submissions (verified by other users)
        - Glassdoor (with permission)
        - LeetCode (public data)
        - Blind forum (aggregated)
        """
        query = db.query(CompanyQuestion).join(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name)
        )
        
        if role:
            query = query.filter(CompanyQuestion.role == role)
        if difficulty:
            query = query.filter(CompanyQuestion.difficulty == difficulty)
        
        questions = query.order_by(
            CompanyQuestion.frequency_score.desc(),
            CompanyQuestion.verification_count.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": q.id,
                "question": q.question_text,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "round_type": q.round_type,
                "role": q.role,
                "frequency_score": q.frequency_score,
                "times_asked": q.times_asked,
                "success_rate": q.success_rate,
                "avg_prep_time_hours": q.avg_prep_time_hours,
                "verified": q.verified,
                "verification_count": q.verification_count,
                "source": q.source
            }
            for q in questions
        ]
    
    @staticmethod
    def get_salary_data(
        db: Session, 
        company_name: str, 
        role: Optional[str] = None,
        seniority: Optional[str] = None
    ) -> List[Dict]:
        """
        Get verified salary data for a company
        
        This data is collected from:
        - Levels.fyi (verified submissions)
        - Blind forum (real employees)
        - Glassdoor (with salary reporting)
        - User submissions (offer letter verification)
        """
        query = db.query(CompanySalaryData).join(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name)
        )
        
        if role:
            query = query.filter(CompanySalaryData.role == role)
        if seniority:
            query = query.filter(CompanySalaryData.seniority == seniority)
        
        salaries = query.all()
        
        return [
            {
                "role": s.role,
                "seniority": s.seniority,
                "location": s.location,
                "base_salary_avg": s.base_salary_avg,
                "bonus_avg": s.bonus_avg,
                "stock_avg": s.stock_avg,
                "total_comp_avg": s.total_comp_avg,
                "data_points": s.data_points,
                "last_updated": s.last_updated
            }
            for s in salaries
        ]
    
    @staticmethod
    def get_active_job_openings(
        db: Session,
        company_name: str,
        role: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get active job openings for a company
        
        Live job data from:
        - LinkedIn (via web scraping or API)
        - Company careers page
        - Glassdoor
        """
        query = db.query(CompanyJobOpening).join(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name),
            CompanyJobOpening.is_active == True
        )
        
        if role:
            query = query.filter(CompanyJobOpening.role == role)
        
        openings = query.order_by(
            CompanyJobOpening.posted_date.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": o.id,
                "job_title": o.job_title,
                "role": o.role,
                "seniority": o.seniority,
                "location": o.location,
                "remote_type": o.remote_type,
                "salary_min": o.salary_min_usd,
                "salary_max": o.salary_max_usd,
                "required_skills": o.required_skills,
                "preferred_skills": o.preferred_skills,
                "job_url": o.job_url,
                "source": o.source,
                "posted_date": o.posted_date
            }
            for o in openings
        ]
    
    @staticmethod
    def add_company_question(
        db: Session,
        company_name: str,
        question_text: str,
        topic: str,
        difficulty: str,
        round_type: str,
        role: str,
        source: str = "User Submission"
    ) -> bool:
        """Add a new interview question from user submission"""
        try:
            company = db.query(CompanyProfile).filter(
                CompanyProfile.company_name.ilike(company_name)
            ).first()
            
            if not company:
                logger.warning(f"Company {company_name} not found")
                return False
            
            new_question = CompanyQuestion(
                company_id=company.id,
                question_text=question_text,
                topic=topic,
                difficulty=difficulty,
                round_type=round_type,
                role=role,
                source=source,
                frequency_score=1
            )
            
            db.add(new_question)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding company question: {e}")
            return False
    
    @staticmethod
    def track_user_company_interest(
        db: Session,
        user_id: int,
        company_name: str
    ) -> bool:
        """Track user interest in a company for recommendation analytics"""
        try:
            interest = db.query(UserCompanyInterest).filter(
                UserCompanyInterest.user_id == user_id,
                UserCompanyInterest.company_name.ilike(company_name)
            ).first()
            
            if interest:
                interest.times_viewed += 1
                interest.last_viewed = datetime.utcnow()
            else:
                interest = UserCompanyInterest(
                    user_id=user_id,
                    company_name=company_name
                )
                db.add(interest)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error tracking company interest: {e}")
            return False
    
    @staticmethod
    def get_trending_companies(db: Session, limit: int = 10) -> List[Dict]:
        """Get companies with most active questions/updates"""
        companies = db.query(CompanyProfile).order_by(
            CompanyProfile.total_interviews_tracked.desc()
        ).limit(limit).all()
        
        return [
            {
                "company_name": c.company_name,
                "total_interviews_tracked": c.total_interviews_tracked,
                "placement_rate": c.placement_rate,
                "average_rating": c.average_rating,
                "avg_total_comp_usd": c.avg_total_comp_usd,
                "popular_roles": c.popular_roles[:3]  # Top 3 roles
            }
            for c in companies
        ]
    
    @staticmethod
    def get_company_statistics(db: Session, company_name: str) -> Optional[Dict]:
        """Get comprehensive statistics for a company"""
        company = db.query(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name)
        ).first()
        
        if not company:
            return None
        
        total_questions = db.query(CompanyQuestion).filter(
            CompanyQuestion.company_id == company.id
        ).count()
        
        total_salaries = db.query(CompanySalaryData).filter(
            CompanySalaryData.company_id == company.id
        ).count()
        
        return {
            "company_name": company.company_name,
            "total_questions_tracked": total_questions,
            "total_salary_data_points": total_salaries,
            "placement_rate": company.placement_rate,
            "average_rating": company.average_rating,
            "avg_interview_rounds": company.avg_interview_rounds,
            "avg_base_salary": company.avg_base_salary_usd,
            "avg_total_comp": company.avg_total_comp_usd,
            "hiring_pace": company.hiring_pace,
            "active_jobs": company.active_job_openings,
            "most_asked_topics": self._get_most_asked_topics(db, company.id),
            "success_rate": company.placement_rate
        }
    
    @staticmethod
    def _get_most_asked_topics(db: Session, company_id: int) -> List[str]:
        """Get most frequently asked topics at a company"""
        from sqlalchemy import func
        
        topics = db.query(
            CompanyQuestion.topic,
            func.count(CompanyQuestion.id).label('count')
        ).filter(
            CompanyQuestion.company_id == company_id
        ).group_by(
            CompanyQuestion.topic
        ).order_by(
            func.count(CompanyQuestion.id).desc()
        ).limit(5).all()
        
        return [topic[0] for topic in topics]
