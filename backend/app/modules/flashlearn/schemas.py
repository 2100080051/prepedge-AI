from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FlashcardBase(BaseModel):
    question: str
    answer: str
    topic: str
    company: Optional[str] = None
    difficulty: str = "medium"

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardResponse(FlashcardBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudySessionCreate(BaseModel):
    topic: str
    difficulty: Optional[str] = None
    card_count: int = 10

class StudySessionResponse(BaseModel):
    id: int
    topic: str
    duration_minutes: int
    flashcards_studied: int
    performance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    topic: str

class CompanyResponse(BaseModel):
    company: str
