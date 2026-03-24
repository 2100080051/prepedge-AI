from pydantic import BaseModel
from typing import List, Optional

class InterviewStartRequest(BaseModel):
    company: str
    role: str

class InterviewMessageRequest(BaseModel):
    message: str

class InterviewMessageResponse(BaseModel):
    question: str
    feedback: Optional[str] = None
