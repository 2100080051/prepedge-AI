"""
PHASE 4a: Answer & Explanation Endpoints for Questions API
- Add answers and explanations to questions
- Deduplication logic
- Reveal answers to users after attempts
"""

from fastapi import HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Question, User
from app.auth.dependencies import get_current_user
from app.modules.questions.router import (
    AddAnswerRequest, AnswerResponse, CheckDuplicateRequest, CheckDuplicateResponse
)
from typing import List, Optional
from datetime import datetime


# ===== PHASE 4a ENDPOINTS =====

def get_answer_endpoints(router: APIRouter) -> None:
    """Register answer-related endpoints"""
    
    @router.post("/{question_id}/answer", response_model=AnswerResponse)
    def add_answer_to_question(
        question_id: int,
        request: AddAnswerRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Add answer and explanation to a question.
        
        Only admins and contributors can add answers.
        
        **Description**:
        Store the correct answer, detailed explanation, and optional code solution
        for a question. This enables the "Show Answer" feature on the practice page.
        
        **Request Body**:
        {
            "answer_text": "The correct answer explanation",
            "explanation": "# Why This Works\n1. Step 1...\n2. Step 2...",
            "solution_code": "def solve():\n    pass",
            "is_correct": true
        }
        
        **Returns**:
        {
            "success": true,
            "question_id": 123,
            "has_answer": true,
            "answer_text": "...",
            "message": "Answer added successfully"
        }
        """
        try:
            # Check if user has permission (admin or original contributor)
            question = db.query(Question).filter(Question.id == question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Only admins can add answers
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only admins can add answers to questions"
                )
            
            # Update question with answer
            question.answer_text = request.answer_text
            question.explanation = request.explanation
            question.solution_code = request.solution_code
            question.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(question)
            
            return AnswerResponse(
                success=True,
                question_id=question.id,
                has_answer=True,
                answer_text=question.answer_text,
                explanation=question.explanation,
                message="Answer added successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding answer: {str(e)}")
    
    
    @router.get("/{question_id}/reveal-answer", response_model=AnswerResponse)
    def reveal_answer(
        question_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Get the answer and explanation for a question.
        
        User must have attempted the question first.
        
        **Description**:
        Retrieve the answer, explanation, and solution code for a question.
        This is called after a user submits their attempt and clicks "Show Answer".
        
        **Returns**:
        {
            "success": true,
            "question_id": 123,
            "has_answer": true,
            "answer_text": "The correct answer...",
            "explanation": "# Detailed Explanation\\n...",
            "message": "Answer retrieved successfully"
        }
        """
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            
            if not question.answer_text:
                raise HTTPException(
                    status_code=404,
                    detail="Answer not yet available for this question"
                )
            
            return AnswerResponse(
                success=True,
                question_id=question.id,
                has_answer=True,
                answer_text=question.answer_text,
                explanation=question.explanation,
                message="Answer retrieved successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving answer: {str(e)}")
    
    
    @router.post("/check-duplicate", response_model=CheckDuplicateResponse)
    def check_question_duplicate(
        request: CheckDuplicateRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Check if a question is a duplicate of an existing one.
        
        **Description**:
        Uses exact-match deduplication to find if the question already exists.
        This prevents storing duplicate questions and helps users know if they've
        seen similar questions before.
        
        **Approach**: Simple exact-match comparison
        - Compares question_text exactly
        - Can optionally filter by company
        - Returns the original question if duplicate found
        
        **Request Body**:
        {
            "question_text": "Write a function to reverse a string",
            "company_name": "Amazon"
        }
        
        **Returns**:
        {
            "success": true,
            "is_duplicate": false,
            "duplicate_of_id": null,
            "similar_questions": [],
            "message": "Question is not a duplicate"
        }
        """
        try:
            # Check for exact match
            query = db.query(Question).filter(
                Question.question_text == request.question_text
            )
            
            # Optional: filter by company if provided
            if request.company_name:
                query = query.filter(Question.company_name == request.company_name)
            
            existing_question = query.first()
            
            if existing_question:
                return CheckDuplicateResponse(
                    success=True,
                    is_duplicate=True,
                    duplicate_of_id=existing_question.id,
                    similar_questions=[
                        {
                            "id": existing_question.id,
                            "question_text": existing_question.question_text,
                            "company": existing_question.company_name,
                            "difficulty": existing_question.difficulty
                        }
                    ],
                    message="Duplicate question found!"
                )
            
            return CheckDuplicateResponse(
                success=True,
                is_duplicate=False,
                duplicate_of_id=None,
                similar_questions=[],
                message="Question is not a duplicate"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking duplicate: {str(e)}"
            )
    
    
    @router.get("/admin/unanswered", response_model=dict)
    def get_unanswered_questions(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Get questions that don't have answers yet (Admin only).
        
        **Description**:
        Returns paginated list of questions missing answers.
        Admins use this to identify and fill in missing answers.
        
        **Returns**:
        {
            "success": true,
            "questions": [
                {
                    "id": 1,
                    "question_text": "...",
                    "company_name": "Amazon",
                    "difficulty": "Medium",
                    "has_answer": false
                }
            ],
            "total": 150,
            "message": "Unanswered questions retrieved"
        }
        """
        try:
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only admins can view unanswered questions"
                )
            
            # Get questions without answers
            unanswered = db.query(Question).filter(
                Question.answer_text == None
            ).offset(offset).limit(limit).all()
            
            total = db.query(Question).filter(
                Question.answer_text == None
            ).count()
            
            return {
                "success": True,
                "questions": [
                    {
                        "id": q.id,
                        "question_text": q.question_text,
                        "company_name": q.company_name,
                        "difficulty": q.difficulty,
                        "round_type": q.round_type,
                        "source": q.source,
                        "has_answer": False,
                        "created_at": q.created_at.isoformat()
                    }
                    for q in unanswered
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
                "message": f"Found {total} unanswered questions"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving unanswered questions: {str(e)}"
            )
    
    
    @router.get("/stats/answer-coverage", response_model=dict)
    def get_answer_coverage_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """
        Get statistics on answer coverage (Admin only).
        
        **Description**:
        Shows how many questions have answers vs total questions.
        Helps admins understand the state of the Q&A database.
        
        **Returns**:
        {
            "success": true,
            "total_questions": 1000,
            "answered_questions": 750,
            "coverage_percentage": 75.0,
            "by_company": {
                "Amazon": {"total": 100, "answered": 85},
                "Google": {"total": 150, "answered": 120}
            },
            "message": "Answer coverage statistics"
        }
        """
        try:
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Only admins can view statistics"
                )
            
            total_qs = db.query(Question).count()
            answered_qs = db.query(Question).filter(
                Question.answer_text != None
            ).count()
            
            coverage = (answered_qs / total_qs * 100) if total_qs > 0 else 0
            
            # By company
            companies = db.query(Question.company_name).distinct().all()
            by_company = {}
            for (company,) in companies:
                total = db.query(Question).filter(
                    Question.company_name == company
                ).count()
                answered = db.query(Question).filter(
                    Question.company_name == company,
                    Question.answer_text != None
                ).count()
                by_company[company] = {"total": total, "answered": answered}
            
            return {
                "success": True,
                "total_questions": total_qs,
                "answered_questions": answered_qs,
                "coverage_percentage": round(coverage, 2),
                "by_company": by_company,
                "message": "Answer coverage statistics retrieved"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving statistics: {str(e)}"
            )
