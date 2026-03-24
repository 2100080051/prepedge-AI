from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.flashlearn.service import FlashLearnService
from app.modules.flashlearn.schemas import (
    FlashcardResponse, FlashcardCreate, TopicResponse, CompanyResponse
)
from typing import List, Optional

router = APIRouter(prefix="/flashlearn", tags=["flashlearn"])

@router.get("/flashcards", response_model=List[FlashcardResponse])
def get_flashcards(
    topic: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get flashcards with optional filters"""
    return FlashLearnService.get_flashcards(db, topic=topic, company=company, limit=limit)

@router.get("/flashcards/random", response_model=List[FlashcardResponse])
def get_random_flashcards(
    count: int = 10,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None,
    company: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get random flashcards for study, with optional topic, company and difficulty filter"""
    return FlashLearnService.get_random_flashcards(db, count=count, difficulty=difficulty, topic=topic, company=company)

@router.get("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    """Get a specific flashcard"""
    flashcard = FlashLearnService.get_flashcard_by_id(db, flashcard_id)
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return flashcard

@router.post("/flashcards", response_model=FlashcardResponse)
def create_flashcard(
    flashcard: FlashcardCreate,
    db: Session = Depends(get_db)
):
    """Create a new flashcard"""
    return FlashLearnService.create_flashcard(
        db,
        question=flashcard.question,
        answer=flashcard.answer,
        topic=flashcard.topic,
        company=flashcard.company,
        difficulty=flashcard.difficulty
    )

@router.get("/topics", response_model=List[str])
def get_topics(db: Session = Depends(get_db)):
    """Get all available topics"""
    return FlashLearnService.get_topics(db)

@router.get("/companies", response_model=List[str])
def get_companies(db: Session = Depends(get_db)):
    """Get all available companies"""
    return FlashLearnService.get_companies(db)

@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    """Seed database with initial flashcards"""
    result = FlashLearnService.seed_flashcards(db)
    return {"message": "Database seeded successfully", "cards_added": result.get('seeded', 0)}
