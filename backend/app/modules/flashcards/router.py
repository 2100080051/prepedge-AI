from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.flashcards.service import FlashcardService
from typing import Dict, List
from pydantic import BaseModel

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


class CreateFlashcardRequest(BaseModel):
    topic: str
    question: str
    answer: str
    difficulty: str = "medium"
    company: str = None


class GenerateFromContentRequest(BaseModel):
    content: str
    topic: str
    company: str = None


class ReviewRequest(BaseModel):
    card_id: int
    quality: int  # 0-5


class BatchCreateRequest(BaseModel):
    topic: str
    company: str = None
    cards: List[Dict]  # [{question, answer, difficulty}]


@router.post("/create")
async def create_flashcard(
    request: CreateFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Create a single flashcard"""
    try:
        result = FlashcardService.create_flashcard(
            topic=request.topic,
            question=request.question,
            answer=request.answer,
            difficulty=request.difficulty,
            company=request.company,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-content")
async def generate_from_content(
    request: GenerateFromContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Auto-generate flashcards from learning content"""
    try:
        result = FlashcardService.generate_from_content(
            user_id=current_user.id,
            content=request.content,
            topic=request.topic,
            company=request.company,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch-create")
async def batch_create(
    request: BatchCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Create multiple flashcards at once"""
    try:
        result = FlashcardService.batch_create_from_list(
            cards_list=request.cards,
            topic=request.topic,
            company=request.company,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/review-session")
async def get_review_session(
    session_size: int = 20,
    topic: str = None,
    company: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Start a new review session"""
    try:
        result = FlashcardService.get_review_session(
            user_id=current_user.id,
            session_size=session_size,
            topic=topic,
            company=company,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/record-review")
async def record_review(
    request: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Record a single card review and get next review date"""
    try:
        result = FlashcardService.record_review(
            user_id=current_user.id,
            card_id=request.card_id,
            quality=request.quality,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end-session")
async def end_review_session(
    session_data: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """End a review session and get statistics"""
    try:
        result = FlashcardService.end_review_session(
            user_id=current_user.id,
            session_data=session_data,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_stats(
    topic: str = None,
    company: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get flashcard statistics"""
    try:
        stats = FlashcardService.get_stats(
            user_id=current_user.id,
            topic=topic,
            company=company,
            db=db
        )
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search")
async def search_cards(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict:
    """Search flashcards by question or topic"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

    try:
        cards = FlashcardService.search_cards(
            query_text=q,
            limit=limit,
            db=db
        )
        return {
            "success": True,
            "count": len(cards),
            "data": cards
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/learning-plan/{company}/{role}")
async def get_learning_plan(
    company: str,
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get personalized learning plan for a company/role"""
    try:
        result = FlashcardService.get_learning_plan(
            user_id=current_user.id,
            company=company,
            role=role,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/for-review")
async def get_cards_for_review(
    limit: int = 20,
    topic: str = None,
    company: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get cards due for review"""
    try:
        cards = FlashcardService.get_cards_for_review(
            user_id=current_user.id,
            limit=limit,
            topic=topic,
            company=company,
            db=db
        )
        return {
            "success": True,
            "count": len(cards),
            "data": cards
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
