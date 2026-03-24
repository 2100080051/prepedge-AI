from pydantic import BaseModel
from typing import List

class ResumeFeedbackResponse(BaseModel):
    score: float
    strengths: List[str]
    gaps: List[str]
    improvements: List[str]

class ResumeUploadResponse(BaseModel):
    id: int
    score: float
    
    class Config:
        from_attributes = True
