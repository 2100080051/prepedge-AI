"""
Job Recommendation Service
Recommends jobs based on user profile, experience, and education
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.modules.company_data.models import CompanyJobOpening, CompanyProfile, CompanySalaryData
from app.database.models import User, UserCompanyInterest
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JobRecommendationService:
    """Recommends jobs based on user profile"""
    
    @staticmethod
    def get_personalized_recommendations(db: Session, user_id: int, limit: int = 20) -> List[Dict]:
        """
        Get personalized job recommendations based on user profile
        
        Factors:
        - Years of experience (match seniority level)
        - College/Education (target companies that hire from that college)
        - Course (match with popular roles)
        - Job interest history
        - Placement rate and company ratings
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Determine seniority level from experience
        seniority = JobRecommendationService._get_seniority_level(user.years_of_experience)
        
        # Get popular roles based on course
        popular_roles = JobRecommendationService._get_roles_from_course(user.course)
        
        # Base query for job openings
        query = db.query(CompanyJobOpening).join(CompanyProfile).filter(
            CompanyJobOpening.is_active == True
        )
        
        # Filter by seniority
        if seniority:
            query = query.filter(
                or_(
                    CompanyJobOpening.seniority == seniority,
                    CompanyJobOpening.seniority.in_(
                        JobRecommendationService._get_compatible_seniorities(seniority)
                    )
                )
            )
        
        # Filter by roles
        if popular_roles:
            query = query.filter(CompanyJobOpening.role.in_(popular_roles))
        
        # Get jobs, sorted by company placement rate and rating
        jobs = query.order_by(
            CompanyProfile.placement_rate.desc(),
            CompanyProfile.average_rating.desc(),
            CompanyJobOpening.posted_date.desc()
        ).limit(limit).all()
        
        # Format response
        recommendations = []
        for job in jobs:
            company = db.query(CompanyProfile).filter(
                CompanyProfile.id == job.company_id
            ).first()
            
            recommendations.append({
                "job_id": job.id,
                "company_name": job.company_name or company.company_name,
                "job_title": job.job_title,
                "role": job.role,
                "seniority": job.seniority,
                "location": job.location,
                "is_remote": job.is_remote,
                "salary_min": job.salary_min_usd,
                "salary_max": job.salary_max_usd,
                "company_placement_rate": company.placement_rate,
                "company_rating": company.average_rating,
                "required_skills": job.required_skills,
                "match_score": JobRecommendationService._calculate_match_score(
                    job, user, seniority, popular_roles
                )
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return recommendations
    
    @staticmethod
    def get_company_specific_jobs(db: Session, company_name: str, user_role: Optional[str] = None) -> List[Dict]:
        """Get all open positions at a specific company"""
        company = db.query(CompanyProfile).filter(
            CompanyProfile.company_name.ilike(company_name)
        ).first()
        
        if not company:
            return []
        
        query = db.query(CompanyJobOpening).filter(
            CompanyJobOpening.company_id == company.id,
            CompanyJobOpening.is_active == True
        )
        
        if user_role:
            query = query.filter(CompanyJobOpening.role == user_role)
        
        jobs = query.all()
        
        return [
            {
                "job_id": job.id,
                "job_title": job.job_title,
                "role": job.role,
                "seniority": job.seniority,
                "location": job.location,
                "is_remote": job.is_remote,
                "salary_min": job.salary_min_usd,
                "salary_max": job.salary_max_usd,
                "required_skills": job.required_skills,
                "posted_date": job.posted_date,
                "required_years_experience": job.required_years_experience,
            }
            for job in jobs
        ]
    
    @staticmethod
    def search_jobs_by_criteria(
        db: Session,
        role: Optional[str] = None,
        seniority: Optional[str] = None,
        location: Optional[str] = None,
        is_remote: Optional[bool] = None,
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search jobs by specific criteria"""
        query = db.query(CompanyJobOpening).join(CompanyProfile).filter(
            CompanyJobOpening.is_active == True
        )
        
        if role:
            query = query.filter(CompanyJobOpening.role == role)
        if seniority:
            query = query.filter(CompanyJobOpening.seniority == seniority)
        if location:
            query = query.filter(CompanyJobOpening.location.ilike(f"%{location}%"))
        if is_remote is not None:
            query = query.filter(CompanyJobOpening.is_remote == is_remote)
        if min_salary:
            query = query.filter(CompanyJobOpening.salary_max_usd >= min_salary)
        if max_salary:
            query = query.filter(CompanyJobOpening.salary_min_usd <= max_salary)
        
        jobs = query.limit(limit).all()
        
        return [
            {
                "job_id": job.id,
                "company_name": job.company_name or db.query(CompanyProfile).filter(
                    CompanyProfile.id == job.company_id
                ).first().company_name,
                "job_title": job.job_title,
                "role": job.role,
                "seniority": job.seniority,
                "location": job.location,
                "is_remote": job.is_remote,
                "salary_min": job.salary_min_usd,
                "salary_max": job.salary_max_usd,
            }
            for job in jobs
        ]
    
    @staticmethod
    def _get_seniority_level(years_of_experience: int) -> Optional[str]:
        """Determine seniority level from years of experience"""
        if years_of_experience == 0:
            return "Fresher"
        elif years_of_experience < 3:
            return "Junior"
        elif years_of_experience < 7:
            return "Senior"
        else:
            return "Lead"
    
    @staticmethod
    def _get_compatible_seniorities(seniority: str) -> List[str]:
        """Get compatible seniority levels (can apply to higher levels)"""
        compatibility_map = {
            "Fresher": ["Junior"],
            "Junior": ["Senior"],
            "Senior": ["Lead"],
            "Lead": []
        }
        return compatibility_map.get(seniority, [])
    
    @staticmethod
    def _get_roles_from_course(course: Optional[str]) -> List[str]:
        """Map course to popular roles"""
        if not course:
            return ["SDE", "QA", "Business Analyst"]
        
        course_lower = course.lower()
        
        # CS/IT courses
        if any(word in course_lower for word in ["computer science", "information technology", "it", "cse", "cs"]):
            return ["SDE", "Data Science", "DevOps", "QA"]
        
        # Electronics/ECE
        elif any(word in course_lower for word in ["electronics", "ece", "electrical", "ece"]):
            return ["SDE", "Embedded Systems", "Hardware", "QA"]
        
        # Mechanical
        elif any(word in course_lower for word in ["mechanical", "mech"]):
            return ["Business Analyst", "Operations", "Quality"]
        
        # Chemical
        elif any(word in course_lower for word in ["chemical", "chem"]):
            return ["Business Analyst", "Operations", "Data Analysis"]
        
        # Civil
        elif any(word in course_lower for word in ["civil"]):
            return ["Business Analyst", "Project Manager", "QA"]
        
        # Default
        return ["Business Analyst", "QA"]
    
    @staticmethod
    def _calculate_match_score(job: CompanyJobOpening, user: User, seniority: str, roles: List[str]) -> float:
        """Calculate match score (0-100) for a job"""
        score = 0.0
        
        # Seniority match (40%)
        if job.seniority == seniority:
            score += 40
        elif job.seniority in JobRecommendationService._get_compatible_seniorities(seniority):
            score += 20
        
        # Role match (35%)
        if job.role in roles:
            score += 35
        elif any(word in job.role.lower() for word in [r.lower() for r in roles]):
            score += 20
        
        # Company metrics (25%)
        # This will be added dynamically in get_personalized_recommendations
        
        return min(score, 100.0)
