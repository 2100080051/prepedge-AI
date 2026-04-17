"""
PHASE 4b: Job Matching Algorithm

Matches user preferences with job postings using a score-based system:
- Role Match: 40%
- Skills Match: 30%
- Location Match: 20%
- Company Match: 10%
- Job Type: Bonus points
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JobMatch:
    """Result of matching a user to a job"""
    def __init__(
        self,
        job_id: int,
        job_title: str,
        company: str,
        location: str,
        url: str,
        total_score: float,
        role_score: float,
        skills_score: float,
        location_score: float,
        company_score: float,
        reason: str
    ):
        self.job_id = job_id
        self.job_title = job_title
        self.company = company
        self.location = location
        self.url = url
        self.total_score = total_score
        self.role_score = role_score
        self.skills_score = skills_score
        self.location_score = location_score
        self.company_score = company_score
        self.reason = reason
    
    def to_dict(self) -> Dict:
        return {
            'job_id': self.job_id,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'url': self.url,
            'match_score': round(self.total_score, 2),
            'breakdown': {
                'role': round(self.role_score, 2),
                'skills': round(self.skills_score, 2),
                'location': round(self.location_score, 2),
                'company': round(self.company_score, 2)
            },
            'reason': self.reason
        }


class JobMatcher:
    """Core job matching algorithm"""
    
    ROLE_WEIGHT = 0.40  # 40%
    SKILLS_WEIGHT = 0.30  # 30%
    LOCATION_WEIGHT = 0.20  # 20%
    COMPANY_WEIGHT = 0.10  # 10%
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        return text.lower().strip()
    
    @classmethod
    def calculate_role_match(cls, job_title: str, desired_roles: List[str]) -> tuple:
        """
        Calculate role match score (0-100)
        
        Returns: (score, reason)
        """
        if not desired_roles:
            return 0, "No desired roles specified"
        
        job_title_normalized = cls.normalize_text(job_title)
        
        # Exact role match
        for role in desired_roles:
            role_normalized = cls.normalize_text(role)
            if role_normalized in job_title_normalized or role_normalized == job_title_normalized:
                return 100, f"Exact match: {role}"
        
        # Partial match (keywords)
        keywords = []
        for role in desired_roles:
            keywords.extend(cls.normalize_text(role).split())
        
        matched_keywords = sum(1 for keyword in keywords if keyword in job_title_normalized)
        if keywords:
            score = (matched_keywords / len(keywords)) * 100
            return score, f"Partial match: {matched_keywords}/{len(keywords)} keywords"
        
        return 0, "No role match"
    
    @classmethod
    def calculate_skills_match(cls, job_skills: List[str], user_skills: List[str]) -> tuple:
        """
        Calculate skills match score (0-100)
        
        Returns: (score, reason)
        """
        if not user_skills or not job_skills:
            return 0, "Skills not specified"
        
        # Normalize skills
        job_skills_normalized = set(cls.normalize_text(s) for s in job_skills)
        user_skills_normalized = set(cls.normalize_text(s) for s in user_skills)
        
        # Calculate overlap
        overlap = job_skills_normalized & user_skills_normalized
        if not job_skills_normalized:
            return 0, "Job has no skills specified"
        
        score = (len(overlap) / len(job_skills_normalized)) * 100
        reason = f"Skills match: {len(overlap)}/{len(job_skills_normalized)} ({', '.join(list(overlap)[:3])})"
        
        return score, reason
    
    @classmethod
    def calculate_location_match(cls, job_location: str, desired_locations: List[str]) -> tuple:
        """
        Calculate location match score (0-100)
        
        Returns: (score, reason)
        """
        if not desired_locations:
            return 0, "No location preference"
        
        job_location_normalized = cls.normalize_text(job_location)
        
        # Check for exact match or remote
        if 'remote' in job_location_normalized:
            return 100, "Remote job"
        
        for location in desired_locations:
            location_normalized = cls.normalize_text(location)
            if location_normalized in job_location_normalized:
                return 100, f"Location match: {location}"
        
        return 0, f"Location mismatch ({job_location} vs {', '.join(desired_locations)})"
    
    @classmethod
    def calculate_company_match(cls, job_company: str, desired_companies: List[str]) -> tuple:
        """
        Calculate company match score (0-100)
        
        Returns: (score, reason)
        """
        if not desired_companies or not job_company:
            return 0, "No company match"
        
        company_normalized = cls.normalize_text(job_company)
        
        for desired in desired_companies:
            desired_normalized = cls.normalize_text(desired)
            if desired_normalized == company_normalized:
                return 100, f"Preferred company: {desired}"
        
        return 0, "Company not in preferences"
    
    @classmethod
    def match_job(
        cls,
        job_id: int,
        job_title: str,
        company: str,
        location: str,
        url: str,
        job_skills: List[str],
        desired_roles: List[str],
        user_skills: List[str],
        desired_locations: List[str],
        desired_companies: List[str]
    ) -> JobMatch:
        """
        Calculate overall job match score
        
        Returns: JobMatch object with detailed breakdown
        """
        # Calculate individual scores
        role_score, role_reason = cls.calculate_role_match(job_title, desired_roles)
        skills_score, skills_reason = cls.calculate_skills_match(job_skills, user_skills)
        location_score, location_reason = cls.calculate_location_match(location, desired_locations)
        company_score, company_reason = cls.calculate_company_match(company, desired_companies)
        
        # Calculate weighted total (0-100)
        total_score = (
            (role_score * cls.ROLE_WEIGHT) +
            (skills_score * cls.SKILLS_WEIGHT) +
            (location_score * cls.LOCATION_WEIGHT) +
            (company_score * cls.COMPANY_WEIGHT)
        )
        
        # Build reason string
        reason = f"{role_reason} | {skills_reason} | {location_reason} | {company_reason}"
        
        return JobMatch(
            job_id=job_id,
            job_title=job_title,
            company=company,
            location=location,
            url=url,
            total_score=total_score,
            role_score=role_score,
            skills_score=skills_score,
            location_score=location_score,
            company_score=company_score,
            reason=reason
        )
    
    @classmethod
    def rank_jobs(
        cls,
        jobs: List[Dict],
        desired_roles: List[str],
        user_skills: List[str],
        desired_locations: List[str],
        desired_companies: List[str],
        min_score: float = 60.0,
        limit: int = 10
    ) -> List[JobMatch]:
        """
        Rank all jobs and return top N matches
        
        Args:
            jobs: List of job dictionaries
            desired_roles: Roles user is interested in
            user_skills: User's technical skills
            desired_locations: Preferred locations
            desired_companies: Preferred companies
            min_score: Minimum match score threshold (0-100)
            limit: Maximum number of jobs to return
        
        Returns: List of top JobMatch objects (descending score)
        """
        matches = []
        
        for job in jobs:
            match = cls.match_job(
                job_id=job.get('id'),
                job_title=job.get('job_title', ''),
                company=job.get('company', ''),
                location=job.get('location', ''),
                url=job.get('url', ''),
                job_skills=job.get('skills_required', []),
                desired_roles=desired_roles,
                user_skills=user_skills,
                desired_locations=desired_locations,
                desired_companies=desired_companies
            )
            
            if match.total_score >= min_score:
                matches.append(match)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.total_score, reverse=True)
        
        # Return top N
        return matches[:limit]


class SmartJobRecommendation:
    """Smart recommendation engine with learning"""
    
    def __init__(self):
        self.matcher = JobMatcher()
    
    def boost_by_user_history(
        self,
        matches: List[JobMatch],
        user_application_history: List[Dict]
    ) -> List[JobMatch]:
        """
        Boost scores based on user's application history
        
        If user has applied to similar jobs before, boost similar ones.
        """
        if not user_application_history:
            return matches
        
        # Analyze what user applied to
        applied_companies = set(h.get('company').lower() for h in user_application_history)
        applied_roles = set(h.get('job_title').lower().split() for h in user_application_history)
        
        # Boost matching jobs
        for match in matches:
            if match.company.lower() in applied_companies:
                match.total_score = min(100, match.total_score * 1.1)  # 10% boost
        
        return matches
    
    def diversify_recommendations(
        self,
        matches: List[JobMatch],
        diversity_factor: float = 0.3
    ) -> List[JobMatch]:
        """
        Return diverse recommendations
        
        Mix highest scoring jobs with good but different companies/roles
        """
        if len(matches) <= 5:
            return matches
        
        # Top 50% by score
        top_half = matches[:len(matches)//2]
        
        # Filter bottom 50% to include different companies
        bottom_half = matches[len(matches)//2:]
        diverse = []
        companies_seen = set()
        
        for match in bottom_half:
            if match.company not in companies_seen and \
               match.total_score >= (100 * diversity_factor):  # Ensure quality
                diverse.append(match)
                companies_seen.add(match.company)
            if len(diverse) >= len(matches) // 2:
                break
        
        return top_half + diverse


# Example usage:
if __name__ == "__main__":
    # Sample job
    sample_job = {
        'id': 1,
        'job_title': 'Senior Software Engineer - Python/React',
        'company': 'Google',
        'location': 'Bangalore, India',
        'url': 'https://...',
        'skills_required': ['Python', 'React', 'AWS', 'Docker']
    }
    
    # User preferences
    desired_roles = ['Software Engineer', 'Python Developer']
    user_skills = ['Python', 'JavaScript', 'React']
    desired_locations = ['Bangalore', 'Remote']
    desired_companies = ['Google', 'Amazon']
    
    # Match
    match = JobMatcher.match_job(
        job_id=sample_job['id'],
        job_title=sample_job['job_title'],
        company=sample_job['company'],
        location=sample_job['location'],
        url=sample_job['url'],
        job_skills=sample_job['skills_required'],
        desired_roles=desired_roles,
        user_skills=user_skills,
        desired_locations=desired_locations,
        desired_companies=desired_companies
    )
    
    print(f"Match Score: {match.total_score}%")
    print(f"Breakdown: {match.to_dict()['breakdown']}")
    print(f"Reason: {match.reason}")
