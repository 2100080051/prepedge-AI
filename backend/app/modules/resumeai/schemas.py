from pydantic import BaseModel
from typing import List, Dict, Optional

class ATSBreakdown(BaseModel):
    score_reason: str
    red_flags: List[str] = []
    improvements: List[str] = []

class ResumeFeedbackResponse(BaseModel):
    overall_score: float
    ats_score: float
    ats_breakdown: Optional[Dict] = {}
    strengths: List[str]
    gaps: List[str]
    role_specific_recommendations: List[str]
    what_to_keep: List[str]
    what_to_change: List[str]
    company_match_score: float = 0
    keywords_missing: List[str]

class ResumeUploadResponse(BaseModel):
    id: int
    overall_score: float
    ats_score: float
    target_company: Optional[str]
    target_role: Optional[str]
    role_specific_recommendations: List[str]
    what_to_keep: List[str]
    what_to_change: List[str]
    company_match_score: float = 0
    
    class Config:
        from_attributes = True

class CompanyJobRequirements(BaseModel):
    company: str
    role: str
    description: str
    requirements: str
    key_skills: List[str]
    experience_level: str
    optimization_tips: List[str]
