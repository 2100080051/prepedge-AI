"""
Questions API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.questions.service import QuestionService
from app.llm.provider import get_llm_router


# ===== SCHEMAS =====

class CreateQuestionRequest(BaseModel):
    """Schema for creating a question"""
    company_name: str
    round_type: str
    question_text: str
    difficulty: str  # Easy, Medium, Hard
    source: Optional[str] = "User Submitted"
    solution_text: Optional[str] = None
    solution_explanation: Optional[str] = None
    frequency_score: Optional[int] = 1


class QuestionResponse(BaseModel):
    """Response schema for a question"""
    success: bool
    question: Optional[dict] = None
    message: str


class QuestionsListResponse(BaseModel):
    """Response for list of questions"""
    success: bool
    questions: List[dict]
    count: int
    total: int


class SubmitAttemptRequest(BaseModel):
    """Schema for submitting an answer"""
    user_answer: Optional[str] = None
    is_correct: bool
    difficulty_rating: Optional[int] = None
    time_spent_seconds: int = 0


class AttemptResponse(BaseModel):
    """Response for attempt submission"""
    success: bool
    attempt_id: Optional[int] = None
    xp_awarded: int = 0
    message: str


class VerifyQuestionRequest(BaseModel):
    """Schema for verifying a question"""
    verification_status: str  # verified, rejected
    notes: Optional[str] = None
    detected_topics: Optional[Dict] = None
    detected_skills: Optional[Dict] = None


class UpdateQuestionRequest(BaseModel):
    """Schema for updating a question"""
    company: Optional[str] = None
    difficulty: Optional[str] = None
    round_type: Optional[str] = None
    question: Optional[str] = None


class GenerateStudyPlanRequest(BaseModel):
    """Schema for generating study plan"""
    target_company: str
    target_role: Optional[str] = None
    days_until_interview: int = 30
    weak_areas: Optional[List[str]] = None


class StudyPlanResponse(BaseModel):
    """Response for study plan generation"""
    success: bool
    plan_id: Optional[int] = None
    estimated_hours: int = 0
    questions_count: int = 0
    message: str


class UserStatsResponse(BaseModel):
    """Response for user question stats"""
    success: bool
    total_attempts: int
    correct_answers: int
    accuracy_percentage: float
    easy_solved: int
    medium_solved: int
    hard_solved: int
    companies_practiced: List[dict]
    total_time_minutes: int


# ===== SCRAPER & IMPORT SCHEMAS =====

class ImportQuestionRequest(BaseModel):
    """Schema for importing a single question from scraper"""
    company_name: str
    round_type: str
    question_text: str
    difficulty: str  # Easy, Medium, Hard
    source: str  # Glassdoor, Reddit, Blind, Telegram, etc.
    solution_text: Optional[str] = None
    solution_explanation: Optional[str] = None
    frequency_score: Optional[int] = 1


class BatchImportRequest(BaseModel):
    """Schema for batch importing multiple questions"""
    questions: List[ImportQuestionRequest]
    source: Optional[str] = None  # Override source for all if provided
    auto_verify: bool = False  # Auto-verify if True, set pending if False


class ImportResponse(BaseModel):
    """Response for import operation"""
    success: bool
    imported_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    imported_ids: List[int] = []
    errors: List[Dict] = []
    message: str


# ===== ADVANCED SEARCH SCHEMAS =====

class AdvancedSearchRequest(BaseModel):
    """Schema for advanced question search"""
    search_text: Optional[str] = None  # Full-text search
    company: Optional[str] = None
    difficulty: Optional[str] = None
    round_type: Optional[str] = None
    source: Optional[str] = None
    topics: Optional[List[str]] = None  # Filter by detected topics
    skills: Optional[List[str]] = None  # Filter by detected skills
    min_frequency: Optional[int] = None
    sort_by: Optional[str] = "frequency"  # frequency, difficulty, attempts, recent
    sort_order: Optional[str] = "desc"  # asc, desc
    limit: int = 50
    offset: int = 0


# ===== PHASE 4a: ANSWER & EXPLANATION SCHEMAS =====

class AddAnswerRequest(BaseModel):
    """Schema for adding answer and explanation to a question"""
    answer_text: str  # The correct answer
    explanation: str  # Detailed explanation (markdown format)
    solution_code: Optional[str] = None  # Code solution for coding problems
    is_correct: bool = True


class AnswerResponse(BaseModel):
    """Response for answer operations"""
    success: bool
    question_id: Optional[int] = None
    has_answer: bool
    answer_text: Optional[str] = None
    explanation: Optional[str] = None
    message: str


class CheckDuplicateRequest(BaseModel):
    """Schema for checking duplicate questions"""
    question_text: str
    company_name: Optional[str] = None


class CheckDuplicateResponse(BaseModel):
    """Response for duplicate check"""
    success: bool
    is_duplicate: bool
    duplicate_of_id: Optional[int] = None
    similar_questions: List[dict] = []
    message: str


# ===== ROUTES =====

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/", response_model=QuestionResponse)
async def create_question(
    request: CreateQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Create a new interview question (Admin only).
    
    Args:
        request: Question details
        current_user: Authenticated user (must be admin)
        db: Database session
    
    Returns:
        Successfully created question with ID
    
    Example:
        POST /api/v1/questions
        {
            "company_name": "TCS",
            "round_type": "Tech Interview",
            "question_text": "Reverse a linked list...",
            "difficulty": "Medium",
            "source": "Glassdoor",
            "solution_text": "def reverse(head): ...",
            "solution_explanation": "Use three pointers...",
            "frequency_score": 8
        }
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = QuestionService.create_question(
            company_name=request.company_name,
            round_type=request.round_type,
            question_text=request.question_text,
            difficulty=request.difficulty,
            source=request.source,
            solution_text=request.solution_text,
            solution_explanation=request.solution_explanation,
            frequency_score=request.frequency_score or 1,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating question: {str(e)}")


@router.get("/", response_model=QuestionsListResponse)
async def search_questions(
    company_name: Optional[str] = Query(None),
    round_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Search for interview questions with filters.
    
    Args:
        company_name: Filter by company (partial match)
        round_type: Filter by round type
        difficulty: Filter by difficulty (Easy, Medium, Hard)
        limit: Results per page (1-100, default 50)
        offset: Pagination offset
        db: Database session
    
    Returns:
        List of matching questions
    
    Example:
        GET /api/v1/questions?company_name=TCS&difficulty=Medium&limit=20
    """
    try:
        result = QuestionService.get_questions(
            company_name=company_name,
            round_type=round_type,
            difficulty=difficulty,
            limit=limit,
            offset=offset,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        # DYNAMIC WEB SCRAPING FALLBACK
        # If no questions found and user searched for a specific company
        if result.get("count", 0) == 0 and company_name:
            llm_router = get_llm_router()
            new_questions = await llm_router.generate_questions_from_web(
                company=company_name,
                round_type=round_type or "Technical Interview",
                difficulty=difficulty or "Medium"
            )
            
            if new_questions and isinstance(new_questions, list):
                # Format to match normal get_questions structure
                for q in new_questions:
                    # Default values for missing keys to avoid breaks
                    q.setdefault("frequency_score", 1)
                    q.setdefault("total_attempts", 0)
                    q.setdefault("correct_attempts", 0)
                    q.setdefault("avg_difficulty_rating", 0.0)
                    
                # Store them to the DB via batch import
                try:
                    saved_questions = QuestionService.batch_import_questions(new_questions, auto_verify=True, db=db)
                    # Re-fetch newly saved questions from DB to get their IDs
                    if saved_questions:
                        db.commit()
                        # Re-fetch from database to get proper IDs and all fields
                        fresh_result = QuestionService.get_questions(
                            company_name=company_name,
                            round_type=round_type,
                            difficulty=difficulty,
                            limit=limit,
                            offset=offset,
                            db=db
                        )
                        if fresh_result.get("success"):
                            result = fresh_result
                except Exception as import_err:
                    print(f"Non-fatal error auto-saving scraped questions: {import_err}")
                    # Fallback: still return the questions but without IDs (won't work for practice)
                    result["questions"] = []
                    result["count"] = 0
                    result["total"] = 0
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching questions: {str(e)}")


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get full details of a single question.
    
    Args:
        question_id: Question ID
        db: Database session
    
    Returns:
        Complete question with solution
    
    Example:
        GET /api/v1/questions/5
    """
    try:
        result = QuestionService.get_question_detail(
            question_id=question_id,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if result.get("error") == "not_found" else 400,
                detail=result.get("message")
            )
        
        return {
            "success": True,
            "question": result.get("question"),
            "message": "Question retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving question: {str(e)}")


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    request: UpdateQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Update a question (Admin only)
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = QuestionService.update_question(
            question_id=question_id,
            admin_id=current_user.id,
            company=request.company,
            difficulty=request.difficulty,
            round_type=request.round_type,
            question_text=request.question,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating question: {str(e)}")


@router.post("/{question_id}/attempt", response_model=AttemptResponse)
async def submit_attempt(
    question_id: int,
    request: SubmitAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Submit an attempt/answer to a question.
    
    Args:
        question_id: Question being attempted
        request: Answer details
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Attempt recorded with XP awarded
    
    Example:
        POST /api/v1/questions/5/attempt
        {
            "user_answer": "def reverse(head): ...",
            "is_correct": true,
            "difficulty_rating": 7,
            "time_spent_seconds": 2400
        }
    """
    try:
        result = QuestionService.submit_attempt(
            user_id=current_user.id,
            question_id=question_id,
            user_answer=request.user_answer,
            is_correct=request.is_correct,
            difficulty_rating=request.difficulty_rating,
            time_spent_seconds=request.time_spent_seconds,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if result.get("error") == "not_found" else 400,
                detail=result.get("message")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting attempt: {str(e)}")


@router.post("/{question_id}/verify", response_model=QuestionResponse)
async def verify_question(
    question_id: int,
    request: VerifyQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Verify a question (Admin only).
    
    Args:
        question_id: Question to verify
        request: Verification details
        current_user: Authenticated user (must be admin)
        db: Database session
    
    Returns:
        Verification result
    
    Example:
        POST /api/v1/questions/5/verify
        {
            "verification_status": "verified",
            "notes": "Good question, added",
            "detected_topics": {"DSA": true, "LinkedList": true},
            "detected_skills": {"Problem Solving": 8}
        }
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = QuestionService.verify_question(
            question_id=question_id,
            admin_id=current_user.id,
            verification_status=request.verification_status,
            notes=request.notes,
            detected_topics=request.detected_topics,
            detected_skills=request.detected_skills,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return {
            "success": True,
            "message": result.get("message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying question: {str(e)}")


@router.get("/pending/all", response_model=QuestionsListResponse)
async def get_pending_questions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get questions pending verification (Admin only).
    
    Args:
        limit: Results per page
        offset: Pagination offset
        current_user: Authenticated user (must be admin)
        db: Database session
    
    Returns:
        List of pending questions
    
    Example:
        GET /api/v1/questions/pending/all?limit=20&offset=0
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = QuestionService.get_pending_questions(
            limit=limit,
            offset=offset,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pending questions: {str(e)}")


@router.post("/study-plans/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: GenerateStudyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Generate a personalized AI study plan.
    
    Args:
        request: Target company and timeline
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Generated study plan with questions and timeline
    
    Example:
        POST /api/v1/questions/study-plans/generate
        {
            "target_company": "TCS",
            "target_role": "Software Engineer",
            "days_until_interview": 30
        }
    """
    try:
        result = QuestionService.generate_study_plan(
            user_id=current_user.id,
            target_company=request.target_company,
            target_role=request.target_role,
            days_until_interview=request.days_until_interview,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study plan: {str(e)}")


@router.get("/user/stats", response_model=UserStatsResponse)
async def get_user_question_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get current user's question statistics.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        User's practice statistics and performance metrics
    
    Example:
        GET /api/v1/questions/user/stats
    """
    try:
        result = QuestionService.get_user_stats(
            user_id=current_user.id,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user stats: {str(e)}")


# ===== ADMIN ANALYTICS ENDPOINTS =====

class AnalyticsResponse(BaseModel):
    """Response schema for analytics"""
    success: bool
    dashboard: Optional[dict] = None
    message: Optional[str] = None


class QuestionAnalyticsResponse(BaseModel):
    """Response schema for question analytics"""
    success: bool
    question: Optional[dict] = None
    analytics: Optional[dict] = None
    successful_users: Optional[List[dict]] = None
    message: Optional[str] = None


class ExportDataResponse(BaseModel):
    """Response schema for data export"""
    success: bool
    data: Optional[List[dict]] = None  # Changed: Can be list of dicts or list representation will be converted to string
    count: Optional[int] = None
    format: Optional[str] = None
    message: Optional[str] = None


@router.get("/admin/analytics", response_model=AnalyticsResponse)
async def get_admin_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get comprehensive admin analytics dashboard.
    
    Requires: Admin role
    
    Returns:
        Complete analytics including:
        - Questions: Total, verified, pending, rejected
        - Questions by company, difficulty, round, source
        - Attempts: Total, successful, accuracy
        - Top companies and questions
        - User engagement metrics
    
    Example:
        GET /api/v1/questions/admin/analytics
    """
    # Admin role check
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = QuestionService.get_analytics(db=db)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")


@router.get("/admin/analytics/{question_id}", response_model=QuestionAnalyticsResponse)
async def get_question_analytics(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get detailed analytics for a specific question.
    
    Requires: Admin role
    
    Args:
        question_id: Question to analyze
    
    Returns:
        Detailed question analytics including:
        - Attempt statistics
        - User performance metrics
        - Difficulty feedback
        - Successful user examples
    
    Example:
        GET /api/v1/questions/admin/analytics/123
    """
    # Admin role check
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = QuestionService.get_question_analytics_detailed(
            question_id=question_id,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving question analytics: {str(e)}")


@router.get("/admin/export")
async def export_questions(
    company: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    round_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Export questions data in JSON or CSV format.
    
    Requires: Admin role
    
    Query Parameters:
        - company: Filter by company name (optional)
        - difficulty: Filter by Easy/Medium/Hard (optional)
        - round_type: Filter by round type (optional)
        - source: Filter by source (optional)
        - verification_status: Filter by verified/pending/rejected (optional)
        - format: Export format - "json" or "csv" (default: json)
    
    Returns:
        Exported questions data in requested format
    
    Examples:
        GET /api/v1/questions/admin/export?format=json
        GET /api/v1/questions/admin/export?company=Amazon&difficulty=Hard&format=csv
        GET /api/v1/questions/admin/export?verification_status=pending&format=json
    """
    # Admin role check
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Build filters dict
        filters = {}
        if company:
            filters["company"] = company
        if difficulty:
            filters["difficulty"] = difficulty
        if round_type:
            filters["round_type"] = round_type
        if source:
            filters["source"] = source
        if verification_status:
            filters["verification_status"] = verification_status
        
        result = QuestionService.export_questions_data(
            filters=filters if filters else None,
            format=format,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


# ===== SCRAPER & IMPORT ENDPOINTS =====

@router.post("/import/batch", response_model=ImportResponse)
async def batch_import_questions(
    request: BatchImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Batch import multiple questions from scraper or external source.
    
    Requires: Admin role
    
    Request Body:
        {
            "questions": [
                {
                    "company_name": "Amazon",
                    "round_type": "Online Test",
                    "question_text": "Two Sum problem...",
                    "difficulty": "Medium",
                    "source": "Glassdoor",
                    "solution_text": "def twoSum(...)",
                    "solution_explanation": "Use hash map",
                    "frequency_score": 8
                },
                ...more questions...
            ],
            "source": "Glassdoor",  // Optional: override source for all
            "auto_verify": false    // false=pending, true=verified
        }
    
    Returns:
        Import result with counts, imported IDs, and error details
    
    Example:
        POST /api/v1/questions/import/batch
        Authorization: Bearer ADMIN_TOKEN
    """
    # Admin role check
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Prepare questions data
        questions_data = []
        for q in request.questions:
            q_dict = q.dict()
            # Override source if provided
            if request.source:
                q_dict['source'] = request.source
            questions_data.append(q_dict)
        
        result = QuestionService.batch_import_questions(
            questions_data=questions_data,
            auto_verify=request.auto_verify,
            db=db
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing questions: {str(e)}")


@router.post("/search/advanced", response_model=QuestionsListResponse)
async def advanced_search_questions(
    request: AdvancedSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Advanced search with full-text, multi-filter, and sorting.
    
    Requires: Authentication
    
    Request Body:
        {
            "search_text": "two sum",           // Full-text search
            "company": "Amazon",                 // Company filter
            "difficulty": "Medium",              // Difficulty filter
            "round_type": "Online Test",        // Round type filter
            "source": "Glassdoor",              // Source filter
            "topics": ["Array", "Hashing"],     // Topic filters (any match)
            "skills": ["Algorithms", "DSA"],    // Skill filters (any match)
            "min_frequency": 5,                  // Minimum frequency score
            "sort_by": "frequency",              // frequency|difficulty|attempts|recent
            "sort_order": "desc",                // asc|desc
            "limit": 50,
            "offset": 0
        }
    
    Returns:
        Filtered and sorted questions
    
    Examples:
        POST /api/v1/questions/search/advanced
        {
            "search_text": "linked list",
            "difficulty": "Medium",
            "sort_by": "recent"
        }
    """
    try:
        result = QuestionService.advanced_search(
            search_text=request.search_text,
            company_name=request.company,
            round_type=request.round_type,
            difficulty=request.difficulty,
            source=request.source,
            topics=request.topics,
            skills=request.skills,
            min_frequency=request.min_frequency,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            limit=request.limit,
            offset=request.offset,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in advanced search: {str(e)}")


@router.get("/search/advanced", response_model=QuestionsListResponse)
async def advanced_search_questions_get(
    search_text: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    round_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    topics: Optional[str] = Query(None),  # Comma-separated
    skills: Optional[str] = Query(None),  # Comma-separated
    min_frequency: Optional[int] = Query(None),
    sort_by: str = Query("frequency"),
    sort_order: str = Query("desc"),
    limit: int = Query(50),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Advanced search via GET parameters (alternative to POST).
    
    Query Parameters:
        - search_text: Full-text search
        - company, difficulty, round_type, source: Filters
        - topics: Comma-separated topic list
        - skills: Comma-separated skill list
        - min_frequency: Minimum frequency score
        - sort_by: frequency|difficulty|attempts|recent
        - sort_order: asc|desc
        - limit, offset: Pagination
    
    Example:
        GET /api/v1/questions/search/advanced?search_text=array&difficulty=Medium&sort_by=recent
    """
    try:
        # Parse comma-separated lists
        topics_list = [t.strip() for t in topics.split(",")] if topics else None
        skills_list = [s.strip() for s in skills.split(",")] if skills else None
        
        result = QuestionService.advanced_search(
            search_text=search_text,
            company_name=company,
            round_type=round_type,
            difficulty=difficulty,
            source=source,
            topics=topics_list,
            skills=skills_list,
            min_frequency=min_frequency,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in advanced search: {str(e)}")


# ===== PHASE 4a: ANSWER & EXPLANATION ENDPOINTS =====

@router.post("/{question_id}/answer", response_model=AnswerResponse)
async def add_answer_to_question(
    question_id: int,
    request: AddAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Add answer and explanation to a question (Admin only).
    
    Store the correct answer, detailed explanation, and optional code solution.
    This enables the "Show Answer" feature on the practice page.
    """
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only admins can add answers to questions"
            )
        
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
async def reveal_answer(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get the answer and explanation for a question.
    
    User must attempt the question first before viewing answers.
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
async def check_question_duplicate(
    request: CheckDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Check if a question is a duplicate of an existing one.
    
    Uses exact-match deduplication to prevent storing duplicate questions.
    """
    try:
        query = db.query(Question).filter(
            Question.question_text == request.question_text
        )
        
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
async def get_unanswered_questions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get questions that don't have answers yet (Admin only).
    
    Returns paginated list of questions missing answers.
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only admins can view unanswered questions"
            )
        
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
async def get_answer_coverage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get statistics on answer coverage (Admin only).
    
    Shows how many questions have answers vs total.
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
