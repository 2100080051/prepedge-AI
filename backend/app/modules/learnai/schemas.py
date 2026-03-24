from pydantic import BaseModel
from typing import Optional, List

class ConceptExplainRequest(BaseModel):
    domain: str
    subject: str
    concept: str
    language: str = "English"  # English, Telugu, Hindi, Tamil

class ConceptExplainResponse(BaseModel):
    domain: str
    subject: str
    concept: str
    language: str
    explanation: str
    analogy: str
    example: str
    key_points: List[str]
    common_mistakes: List[str]
    image_prompt: str

class ImageGenerateRequest(BaseModel):
    concept: str
    subject: str

class DomainInfo(BaseModel):
    domain: str
    subjects: List[str]
    icon: str
