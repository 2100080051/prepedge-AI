"""
QuestionService - Manages question bank, attempts, and study plans
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database.models import Question, QuestionAttempt, StudyPlan, User
from app.modules.gamification.service import GamificationService
from typing import Dict, List, Optional
import json
import random
import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """Service for managing questions, attempts, and study plans"""
    
    # XP rewards for question activities
    QUESTION_ATTEMPT_XP = 10
    CORRECT_ANSWER_XP = 25
    ALL_EASY_SOLVED_XP = 50
    ALL_MEDIUM_SOLVED_XP = 100
    ALL_HARD_SOLVED_XP = 200
    
    # Difficulty multipliers for time estimation
    DIFFICULTY_TIME = {
        "Easy": 15,      # 15 minutes
        "Medium": 30,    # 30 minutes
        "Hard": 60       # 60 minutes
    }
    
    @staticmethod
    def create_question(
        company_name: str,
        round_type: str,
        question_text: str,
        difficulty: str,
        source: str = "Admin Created",
        solution_text: Optional[str] = None,
        solution_explanation: Optional[str] = None,
        frequency_score: int = 1,
        db: Session = None
    ) -> Dict:
        """
        Create a new question (admin endpoint).
        
        Args:
            company_name: Company name
            round_type: Online Test, Technical, HR, etc.
            question_text: The question itself
            difficulty: Easy, Medium, Hard
            source: Where the question came from
            solution_text: Code/answer solution
            solution_explanation: Explanation of solution
            frequency_score: How often asked (1-10)
            db: Database session
            
        Returns:
            {
                'success': bool,
                'question_id': int,
                'message': str
            }
        """
        try:
            # Validate difficulty
            if difficulty not in ["Easy", "Medium", "Hard"]:
                return {
                    "success": False,
                    "message": "Invalid difficulty. Must be Easy, Medium, or Hard",
                    "error": "invalid_difficulty"
                }
            
            # Create question
            question = Question(
                company_name=company_name.strip(),
                round_type=round_type.strip(),
                question_text=question_text.strip(),
                difficulty=difficulty,
                source=source,
                solution_text=solution_text,
                solution_explanation=solution_explanation,
                frequency_score=min(frequency_score, 10),  # Cap at 10
                verification_status="pending"  # Requires admin review
            )
            
            db.add(question)
            db.flush()
            question_id = question.id
            db.commit()
            
            return {
                "success": True,
                "question_id": question_id,
                "message": "Question created successfully. Pending verification."
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error creating question: {str(e)}",
                "error": "create_error"
            }
    
    @staticmethod
    def get_questions(
        company_name: Optional[str] = None,
        round_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> Dict:
        """
        Search questions by filters (verified only).
        
        Args:
            company_name: Filter by company
            round_type: Filter by round
            difficulty: Filter by difficulty
            limit: Results per page
            offset: Pagination offset
            db: Database session
            
        Returns:
            {
                'success': bool,
                'questions': [question objects],
                'count': int,
                'total': int
            }
        """
        try:
            if db is None:
                logger.error("Database session is None in get_questions")
                return {
                    "success": False,
                    "message": "Database session not provided",
                    "error": "no_db_session"
                }
            
            # Build query - only verified questions
            query = db.query(Question).filter(
                Question.verification_status == "verified"
            )
            
            # Apply filters
            if company_name:
                query = query.filter(
                    Question.company_name.ilike(f"%{company_name}%")
                )
            if round_type:
                query = query.filter(
                    Question.round_type.ilike(f"%{round_type}%")
                )
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            
            # Count total
            total = query.count()
            
            # Apply pagination and order
            questions = query.order_by(
                Question.frequency_score.desc(),
                Question.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            question_list = []
            for q in questions:
                question_list.append({
                    "id": q.id,
                    "company_name": q.company_name,
                    "round_type": q.round_type,
                    "difficulty": q.difficulty,
                    "question_text": q.question_text,
                    "frequency_score": q.frequency_score,
                    "total_attempts": q.total_attempts,
                    "correct_attempts": q.correct_attempts,
                    "avg_difficulty_rating": q.avg_difficulty_rating,
                    "created_at": q.created_at.isoformat() if q.created_at else None
                })
            
            logger.info(f"Retrieved {len(questions)} questions (total: {total}) with filters - company: {company_name}, type: {round_type}, difficulty: {difficulty}")
            
            return {
                "success": True,
                "questions": question_list,
                "count": len(questions),
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Error retrieving questions: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error retrieving questions: {str(e)}",
                "error": "query_error"
            }
    
    @staticmethod
    def get_question_detail(question_id: int, db: Session = None) -> Dict:
        """
        Get full details of a single question (verified).
        
        Returns:
            {
                'success': bool,
                'question': {
                    'id', 'company_name', 'round_type', 'difficulty',
                    'question_text', 'solution_text', 'solution_explanation',
                    'frequency_score', 'total_attempts', 'correct_attempts',
                    'detected_topics', 'detected_skills'
                }
            }
        """
        try:
            question = db.query(Question).filter(
                Question.id == question_id,
                Question.verification_status == "verified"
            ).first()
            
            if not question:
                return {
                    "success": False,
                    "message": "Question not found or not verified",
                    "error": "not_found"
                }
            
            return {
                "success": True,
                "question": {
                    "id": question.id,
                    "company_name": question.company_name,
                    "round_type": question.round_type,
                    "difficulty": question.difficulty,
                    "question_text": question.question_text,
                    "solution_text": question.solution_text,
                    "solution_explanation": question.solution_explanation,
                    "frequency_score": question.frequency_score,
                    "source": question.source,
                    "total_attempts": question.total_attempts,
                    "correct_attempts": question.correct_attempts,
                    "avg_difficulty_rating": round(question.avg_difficulty_rating, 1),
                    "detected_topics": json.loads(question.detected_topics) if question.detected_topics else {},
                    "detected_skills": json.loads(question.detected_skills) if question.detected_skills else {},
                    "created_at": question.created_at.isoformat() if question.created_at else None
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving question: {str(e)}",
                "error": "detail_error"
            }
    
    @staticmethod
    def submit_attempt(
        user_id: int,
        question_id: int,
        user_answer: Optional[str] = None,
        is_correct: bool = False,
        difficulty_rating: Optional[int] = None,
        time_spent_seconds: int = 0,
        db: Session = None
    ) -> Dict:
        """
        Record a user's attempt at a question.
        
        Args:
            user_id: User attempting the question
            question_id: Question being attempted
            user_answer: Code/answer provided
            is_correct: Whether the answer is correct
            difficulty_rating: User's difficulty rating 1-10
            time_spent_seconds: Time taken
            db: Database session
            
        Returns:
            {
                'success': bool,
                'attempt_id': int,
                'xp_awarded': int,
                'message': str
            }
        """
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                return {
                    "success": False,
                    "message": "Question not found",
                    "error": "not_found"
                }
            
            # Check previous attempts
            prev_attempts = db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.question_id == question_id,
                    QuestionAttempt.is_correct == True
                )
            ).count()
            
            # Create attempt record
            attempt = QuestionAttempt(
                user_id=user_id,
                question_id=question_id,
                user_answer_text=user_answer,
                is_correct=is_correct,
                user_difficulty_rating=min(difficulty_rating, 10) if difficulty_rating else None,
                time_spent_seconds=time_spent_seconds,
                attempt_number=prev_attempts + 1 if is_correct else 1
            )
            
            if is_correct:
                attempt.completed_at = datetime.utcnow()
                attempt.attempts_before_correct = prev_attempts + 1
            
            db.add(attempt)
            db.flush()
            attempt_id = attempt.id
            
            # Update question stats
            question.total_attempts += 1
            if is_correct:
                question.correct_attempts += 1
            if difficulty_rating:
                # Running average
                old_avg = question.avg_difficulty_rating
                total_ratings = db.query(QuestionAttempt).filter(
                    and_(
                        QuestionAttempt.question_id == question_id,
                        QuestionAttempt.user_difficulty_rating.isnot(None)
                    )
                ).count()
                question.avg_difficulty_rating = (
                    (old_avg * (total_ratings - 1) + difficulty_rating) / total_ratings
                ) if total_ratings > 0 else difficulty_rating
            
            # Award XP
            xp_awarded = 0
            
            # Base XP for attempt
            xp_awarded += QuestionService.QUESTION_ATTEMPT_XP
            
            # Bonus XP for correct answer
            if is_correct:
                xp_awarded += QuestionService.CORRECT_ANSWER_XP
            
            xp_result = GamificationService.add_xp(
                user_id,
                "question_attempted" if not is_correct else "question_answered_correct",
                db
            )
            
            db.commit()
            
            return {
                "success": True,
                "attempt_id": attempt_id,
                "xp_awarded": xp_result.get("xp_gained", 0),
                "message": "Attempt recorded successfully" if not is_correct else "Correct answer! XP awarded."
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error recording attempt: {str(e)}",
                "error": "attempt_error"
            }
    
    @staticmethod
    def verify_question(
        question_id: int,
        admin_id: int,
        verification_status: str = "verified",
        notes: Optional[str] = None,
        detected_topics: Optional[Dict] = None,
        detected_skills: Optional[Dict] = None,
        db: Session = None
    ) -> Dict:
        """
        Admin endpoint to verify/reject a question.
        
        Args:
            question_id: Question to verify
            admin_id: Admin user ID
            verification_status: verified, rejected
            notes: Verification notes
            detected_topics: AI-detected topics
            detected_skills: AI-detected skills
            db: Database session
            
        Returns:
            {
                'success': bool,
                'message': str
            }
        """
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                return {
                    "success": False,
                    "message": "Question not found",
                    "error": "not_found"
                }
            
            # Update verification
            question.verification_status = verification_status
            question.verified_by_admin_id = admin_id
            question.verification_timestamp = datetime.utcnow()
            question.verification_notes = notes
            
            # Update AI categorization
            if detected_topics:
                question.detected_topics = json.dumps(detected_topics)
            if detected_skills:
                question.detected_skills = json.dumps(detected_skills)
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Question {verification_status} successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error verifying question: {str(e)}",
                "error": "verify_error"
            }
            
    @staticmethod
    def update_question(
        question_id: int,
        admin_id: int,
        company: Optional[str] = None,
        difficulty: Optional[str] = None,
        round_type: Optional[str] = None,
        question_text: Optional[str] = None,
        db: Session = None
    ) -> Dict:
        """Update a question."""
        try:
            q = db.query(Question).filter(Question.id == question_id).first()
            if not q:
                return {"success": False, "message": "Not found", "error": "not_found"}
                
            if company: q.company_name = company
            if difficulty: q.difficulty = difficulty
            if round_type: q.round_type = round_type
            if question_text: q.question_text = question_text
            
            db.commit()
            return {"success": True, "message": "Updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e), "error": "update_error"}
    
    @staticmethod
    def get_pending_questions(
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> Dict:
        """
        Get pending questions for admin verification.
        
        Returns:
            {
                'success': bool,
                'questions': [...],
                'count': int,
                'total': int
            }
        """
        try:
            # Get total count
            total = db.query(func.count(Question.id)).filter(
                Question.verification_status == "pending"
            ).scalar() or 0
            
            # Get paginated results
            pending = db.query(Question).filter(
                Question.verification_status == "pending"
            ).order_by(Question.created_at.asc()).limit(limit).offset(offset).all()
            
            questions = []
            for q in pending:
                questions.append({
                    "id": q.id,
                    "company_name": q.company_name,
                    "round_type": q.round_type,
                    "difficulty": q.difficulty,
                    "question_text": q.question_text,
                    "source": q.source,
                    "frequency_score": q.frequency_score,
                    "created_at": q.created_at.isoformat() if q.created_at else None
                })
            
            return {
                "success": True,
                "questions": questions,
                "count": len(questions),
                "total": total
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving pending questions: {str(e)}",
                "error": "pending_error"
            }
    
    @staticmethod
    def generate_study_plan(
        user_id: int,
        target_company: str,
        target_role: Optional[str] = None,
        days_until_interview: int = 30,
        db: Session = None
    ) -> Dict:
        """
        Generate AI-powered personalized study plan.
        
        Args:
            user_id: User to generate plan for
            target_company: Target company
            target_role: Target role
            days_until_interview: Days available to prepare
            db: Database session
            
        Returns:
            {
                'success': bool,
                'plan_id': int,
                'estimated_hours': int,
                'questions_count': int,
                'message': str
            }
        """
        try:
            # Get user's solved questions to avoid duplicates
            solved_questions = db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True
                )
            ).all()
            solved_ids = [qa.question_id for qa in solved_questions]
            
            # Get company's questions by difficulty
            easy_questions = db.query(Question).filter(
                and_(
                    Question.company_name.ilike(f"%{target_company}%"),
                    Question.difficulty == "Easy",
                    Question.verification_status == "verified",
                    ~Question.id.in_(solved_ids) if solved_ids else True
                )
            ).order_by(Question.frequency_score.desc()).limit(5).all()
            
            medium_questions = db.query(Question).filter(
                and_(
                    Question.company_name.ilike(f"%{target_company}%"),
                    Question.difficulty == "Medium",
                    Question.verification_status == "verified",
                    ~Question.id.in_(solved_ids) if solved_ids else True
                )
            ).order_by(Question.frequency_score.desc()).limit(8).all()
            
            hard_questions = db.query(Question).filter(
                and_(
                    Question.company_name.ilike(f"%{target_company}%"),
                    Question.difficulty == "Hard",
                    Question.verification_status == "verified",
                    ~Question.id.in_(solved_ids) if solved_ids else True
                )
            ).order_by(Question.frequency_score.desc()).limit(5).all()
            
            # Build study plan
            questions_plan = []
            hours_needed = 0
            day = 1
            
            # Easy questions: 2 per day for 2-3 days
            for i, q in enumerate(easy_questions):
                day_num = (i // 2) + 1
                time_minutes = QuestionService.DIFFICULTY_TIME["Easy"]
                hours_needed += time_minutes / 60
                questions_plan.append({
                    "day": day_num,
                    "question_id": q.id,
                    "difficulty": "Easy",
                    "estimated_minutes": time_minutes
                })
            
            day = (len(easy_questions) // 2) + 2
            
            # Medium questions: 2-3 per day
            for i, q in enumerate(medium_questions):
                day_num = day + (i // 3)
                time_minutes = QuestionService.DIFFICULTY_TIME["Medium"]
                hours_needed += time_minutes / 60
                questions_plan.append({
                    "day": day_num,
                    "question_id": q.id,
                    "difficulty": "Medium",
                    "estimated_minutes": time_minutes
                })
            
            day = day + (len(medium_questions) // 3) + 2
            
            # Hard questions: 1-2 per day for practice
            for i, q in enumerate(hard_questions):
                day_num = day + i
                time_minutes = QuestionService.DIFFICULTY_TIME["Hard"]
                hours_needed += time_minutes / 60
                questions_plan.append({
                    "day": day_num,
                    "question_id": q.id,
                    "difficulty": "Hard",
                    "estimated_minutes": time_minutes
                })
            
            # Create study plan record
            study_plan = StudyPlan(
                user_id=user_id,
                target_company=target_company,
                target_role=target_role,
                days_until_interview=days_until_interview,
                estimated_hours_needed=int(hours_needed),
                questions_json=json.dumps(questions_plan),
                difficulty_progression=json.dumps({
                    "Days 1-3": "Easy",
                    "Days 4-7": "Medium",
                    "Days 8-10": "Hard"
                })
            )
            
            db.add(study_plan)
            db.flush()
            plan_id = study_plan.id
            db.commit()
            
            return {
                "success": True,
                "plan_id": plan_id,
                "estimated_hours": int(hours_needed),
                "questions_count": len(questions_plan),
                "message": f"Study plan created with {len(questions_plan)} questions across {int(hours_needed)} estimated hours"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error generating study plan: {str(e)}",
                "error": "plan_error"
            }
    
    @staticmethod
    def get_user_stats(user_id: int, db: Session = None) -> Dict:
        """
        Get user's question statistics.
        
        Returns:
            {
                'total_attempts': int,
                'correct_answers': int,
                'accuracy_percentage': float,
                'easy_solved': int,
                'medium_solved': int,
                'hard_solved': int,
                'companies_practiced': [...],
                'total_time_minutes': int
            }
        """
        try:
            # All attempts
            all_attempts = db.query(QuestionAttempt).filter(
                QuestionAttempt.user_id == user_id
            ).all()
            
            total_attempts = len(all_attempts)
            correct_attempts = sum(1 for a in all_attempts if a.is_correct)
            accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # By difficulty
            easy_solved = db.query(func.count(QuestionAttempt.id)).join(
                Question, Question.id == QuestionAttempt.question_id
            ).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True,
                    Question.difficulty == "Easy"
                )
            ).scalar() or 0
            
            medium_solved = db.query(func.count(QuestionAttempt.id)).join(
                Question, Question.id == QuestionAttempt.question_id
            ).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True,
                    Question.difficulty == "Medium"
                )
            ).scalar() or 0
            
            hard_solved = db.query(func.count(QuestionAttempt.id)).join(
                Question, Question.id == QuestionAttempt.question_id
            ).filter(
                and_(
                    QuestionAttempt.user_id == user_id,
                    QuestionAttempt.is_correct == True,
                    Question.difficulty == "Hard"
                )
            ).scalar() or 0
            
            # Companies practiced
            companies = db.query(
                Question.company_name,
                func.count(QuestionAttempt.id).label('count')
            ).join(
                Question, Question.id == QuestionAttempt.question_id
            ).filter(
                QuestionAttempt.user_id == user_id
            ).group_by(
                Question.company_name
            ).order_by(func.count(QuestionAttempt.id).desc()).limit(5).all()
            
            companies_list = [{"company": c, "attempts": count} for c, count in companies]
            
            # Total time
            total_time_minutes = sum(a.time_spent_seconds // 60 for a in all_attempts if a.time_spent_seconds)
            
            return {
                "success": True,
                "total_attempts": total_attempts,
                "correct_answers": correct_attempts,
                "accuracy_percentage": round(accuracy, 1),
                "easy_solved": easy_solved,
                "medium_solved": medium_solved,
                "hard_solved": hard_solved,
                "companies_practiced": companies_list,
                "total_time_minutes": total_time_minutes
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving user stats: {str(e)}",
                "error": "stats_error"
            }
    
    @staticmethod
    def get_analytics(db: Session = None) -> Dict:
        """
        Get comprehensive analytics for admin dashboard.
        
        Returns:
            {
                'success': bool,
                'dashboard': {
                    'total_questions': int,
                    'verified_questions': int,
                    'pending_questions': int,
                    'rejected_questions': int,
                    'questions_by_company': {...},
                    'questions_by_difficulty': {...},
                    'questions_by_round': {...},
                    'questions_by_source': {...},
                    'total_attempts': int,
                    'successful_attempts': int,
                    'overall_accuracy': float,
                    'average_completion_time': int,
                    'top_companies': [...],
                    'top_questions': [...],
                    'user_engagement': {...}
                }
            }
        """
        try:
            # Total questions stats
            total_questions = db.query(func.count(Question.id)).scalar() or 0
            verified = db.query(func.count(Question.id)).filter(
                Question.verification_status == "verified"
            ).scalar() or 0
            pending = db.query(func.count(Question.id)).filter(
                Question.verification_status == "pending"
            ).scalar() or 0
            rejected = db.query(func.count(Question.id)).filter(
                Question.verification_status == "rejected"
            ).scalar() or 0
            
            # Questions by company
            companies = db.query(
                Question.company_name,
                func.count(Question.id).label('count'),
                func.sum(Question.total_attempts).label('total_attempts'),
                func.sum(Question.correct_attempts).label('correct_attempts')
            ).group_by(Question.company_name).order_by(
                func.count(Question.id).desc()
            ).all()
            
            companies_data = {}
            for company, count, attempts, correct in companies:
                companies_data[company] = {
                    "total_questions": count,
                    "total_attempts": attempts or 0,
                    "successful_attempts": correct or 0,
                    "accuracy": round(
                        (correct / attempts * 100) if attempts and attempts > 0 else 0, 1
                    )
                }
            
            # Questions by difficulty
            difficulties = db.query(
                Question.difficulty,
                func.count(Question.id).label('count'),
                func.avg(Question.total_attempts).label('avg_attempts'),
                func.avg(Question.correct_attempts).label('avg_correct')
            ).group_by(Question.difficulty).all()
            
            difficulty_data = {}
            for difficulty, count, avg_attempts, avg_correct in difficulties:
                difficulty_data[difficulty] = {
                    "total_questions": count,
                    "avg_attempts": round(avg_attempts or 0, 1),
                    "avg_successful": round(avg_correct or 0, 1)
                }
            
            # Questions by round type
            rounds = db.query(
                Question.round_type,
                func.count(Question.id).label('count'),
                func.avg(Question.frequency_score).label('avg_frequency')
            ).group_by(Question.round_type).order_by(
                func.count(Question.id).desc()
            ).all()
            
            round_data = {}
            for round_type, count, avg_frequency in rounds:
                round_data[round_type] = {
                    "total_questions": count,
                    "avg_frequency_score": round(avg_frequency or 0, 1)
                }
            
            # Questions by source
            sources = db.query(
                Question.source,
                func.count(Question.id).label('count')
            ).group_by(Question.source).order_by(
                func.count(Question.id).desc()
            ).all()
            
            source_data = {}
            for source, count in sources:
                source_data[source] = {
                    "total_questions": count
                }
            
            # Attempts statistics
            all_attempts = db.query(QuestionAttempt).all()
            total_attempts = len(all_attempts)
            successful_attempts = sum(1 for a in all_attempts if a.is_correct)
            overall_accuracy = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Average completion time
            times = [a.time_spent_seconds for a in all_attempts if a.time_spent_seconds]
            avg_time = int(sum(times) / len(times)) if times else 0
            
            # Top questions by attempts
            top_questions = db.query(
                Question.id,
                Question.company_name,
                Question.question_text,
                Question.total_attempts,
                Question.correct_attempts,
                Question.difficulty
            ).order_by(Question.total_attempts.desc()).limit(10).all()
            
            top_questions_list = []
            for q in top_questions:
                accuracy = (q.correct_attempts / q.total_attempts * 100) if q.total_attempts > 0 else 0
                top_questions_list.append({
                    "id": q.id,
                    "company": q.company_name,
                    "question": q.question_text[:50] + "..." if len(q.question_text) > 50 else q.question_text,
                    "attempts": q.total_attempts,
                    "successful": q.correct_attempts,
                    "accuracy": round(accuracy, 1),
                    "difficulty": q.difficulty
                })
            
            # Top companies by attempts
            top_companies_list = []
            for company, data in sorted(
                companies_data.items(),
                key=lambda x: x[1]["total_attempts"],
                reverse=True
            )[:5]:
                top_companies_list.append({
                    "company": company,
                    "questions": data["total_questions"],
                    "attempts": data["total_attempts"],
                    "accuracy": data["accuracy"]
                })
            
            # User engagement metrics
            unique_users = db.query(func.count(func.distinct(QuestionAttempt.user_id))).scalar() or 0
            users_who_solved = db.query(func.count(func.distinct(QuestionAttempt.user_id))).filter(
                QuestionAttempt.is_correct == True
            ).scalar() or 0
            
            return {
                "success": True,
                "dashboard": {
                    "total_questions": total_questions,
                    "verified_questions": verified,
                    "pending_questions": pending,
                    "rejected_questions": rejected,
                    "questions_by_company": companies_data,
                    "questions_by_difficulty": difficulty_data,
                    "questions_by_round": round_data,
                    "questions_by_source": source_data,
                    "total_attempts": total_attempts,
                    "successful_attempts": successful_attempts,
                    "overall_accuracy": round(overall_accuracy, 1),
                    "average_completion_time_seconds": avg_time,
                    "top_companies": top_companies_list,
                    "top_questions": top_questions_list,
                    "user_engagement": {
                        "total_active_users": unique_users,
                        "users_with_correct_answers": users_who_solved,
                        "engagement_rate": round(
                            (users_who_solved / unique_users * 100) if unique_users > 0 else 0, 1
                        )
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving analytics: {str(e)}",
                "error": "analytics_error"
            }
    
    @staticmethod
    def get_question_analytics_detailed(question_id: int, db: Session = None) -> Dict:
        """
        Get detailed analytics for a specific question.
        
        Returns detailed attempt data, user performance, and difficulty feedback.
        """
        try:
            question = db.query(Question).filter(
                Question.id == question_id
            ).first()
            
            if not question:
                return {
                    "success": False,
                    "message": "Question not found",
                    "error": "not_found"
                }
            
            # Get all attempts for this question
            attempts = db.query(QuestionAttempt).filter(
                QuestionAttempt.question_id == question_id
            ).all()
            
            total_attempts = len(attempts)
            correct_attempts = sum(1 for a in attempts if a.is_correct)
            incorrect_attempts = total_attempts - correct_attempts
            accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Time statistics
            times = [a.time_spent_seconds for a in attempts if a.time_spent_seconds]
            avg_time = int(sum(times) / len(times)) if times else 0
            
            # Unique users who attempted
            unique_users = db.query(func.count(func.distinct(QuestionAttempt.user_id))).filter(
                QuestionAttempt.question_id == question_id
            ).scalar() or 0
            
            # Difficulty ratings
            ratings = [a.user_difficulty_rating for a in attempts if a.user_difficulty_rating]
            avg_difficulty_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
            
            # Users who solved it correctly (for testimonials)
            successful_users = db.query(QuestionAttempt).filter(
                and_(
                    QuestionAttempt.question_id == question_id,
                    QuestionAttempt.is_correct == True
                )
            ).order_by(QuestionAttempt.completed_at.desc()).limit(5).all()
            
            successful_user_data = []
            for attempt in successful_users:
                user = db.query(User).filter(User.id == attempt.user_id).first()
                if user:
                    successful_user_data.append({
                        "user_id": user.id,
                        "user_name": user.name,
                        "attempts_needed": attempt.attempts_before_correct or 1,
                        "time_spent": attempt.time_spent_seconds or 0,
                        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
                    })
            
            return {
                "success": True,
                "question": {
                    "id": question.id,
                    "company": question.company_name,
                    "difficulty": question.difficulty,
                    "question_text": question.question_text
                },
                "analytics": {
                    "total_attempts": total_attempts,
                    "correct_attempts": correct_attempts,
                    "incorrect_attempts": incorrect_attempts,
                    "accuracy_percentage": round(accuracy, 1),
                    "unique_users_attempted": unique_users,
                    "avg_completion_time_seconds": avg_time,
                    "user_difficulty_rating_avg": avg_difficulty_rating,
                    "difficulty_rating_count": len(ratings)
                },
                "successful_users": successful_user_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving question analytics: {str(e)}",
                "error": "detail_error"
            }
    
    @staticmethod
    def export_questions_data(
        filters: Optional[Dict] = None,
        format: str = "json",
        db: Session = None
    ) -> Dict:
        """
        Export questions data in JSON or CSV format.
        
        Args:
            filters: Optional filters (company, difficulty, round, source)
            format: "json" or "csv"
            db: Database session
            
        Returns:
            {
                'success': bool,
                'data': [...],
                'count': int,
                'format': str,
                'message': str
            }
        """
        try:
            # Build query with filters
            query = db.query(Question)
            
            if filters:
                if filters.get('company'):
                    query = query.filter(
                        Question.company_name.ilike(f"%{filters['company']}%")
                    )
                if filters.get('difficulty'):
                    query = query.filter(Question.difficulty == filters['difficulty'])
                if filters.get('round_type'):
                    query = query.filter(
                        Question.round_type.ilike(f"%{filters['round_type']}%")
                    )
                if filters.get('source'):
                    query = query.filter(
                        Question.source.ilike(f"%{filters['source']}%")
                    )
                if filters.get('verification_status'):
                    query = query.filter(
                        Question.verification_status == filters['verification_status']
                    )
            
            questions = query.order_by(Question.created_at.desc()).all()
            
            export_data = []
            for q in questions:
                question_data = {
                    "id": q.id,
                    "company": q.company_name,
                    "round": q.round_type,
                    "difficulty": q.difficulty,
                    "question": q.question_text,
                    "solution": q.solution_text,
                    "explanation": q.solution_explanation,
                    "frequency_score": q.frequency_score,
                    "source": q.source,
                    "total_attempts": q.total_attempts,
                    "correct_attempts": q.correct_attempts,
                    "accuracy": round(
                        (q.correct_attempts / q.total_attempts * 100) if q.total_attempts > 0 else 0, 1
                    ),
                    "verification_status": q.verification_status,
                    "created_at": q.created_at.isoformat() if q.created_at else None
                }
                
                if format == "json":
                    # Include AI categorization for JSON
                    question_data["detected_topics"] = json.loads(q.detected_topics) if q.detected_topics else {}
                    question_data["detected_skills"] = json.loads(q.detected_skills) if q.detected_skills else {}
                
                export_data.append(question_data)
            
            if format == "csv":
                # Convert to CSV format
                if not export_data:
                    csv_content = ""
                else:
                    output = StringIO()
                    writer = csv.DictWriter(output, fieldnames=[
                        "id", "company", "round", "difficulty", "question",
                        "solution", "explanation", "frequency_score", "source",
                        "total_attempts", "correct_attempts", "accuracy",
                        "verification_status", "created_at"
                    ])
                    writer.writeheader()
                    for row in export_data:
                        # Remove JSON fields for CSV
                        row.pop("detected_topics", None)
                        row.pop("detected_skills", None)
                        writer.writerow(row)
                    csv_content = output.getvalue()
                
                return {
                    "success": True,
                    "data": csv_content,
                    "count": len(export_data),
                    "format": "csv",
                    "message": f"Exported {len(export_data)} questions in CSV format"
                }
            
            return {
                "success": True,
                "data": export_data,
                "count": len(export_data),
                "format": "json",
                "message": f"Exported {len(export_data)} questions in JSON format"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error exporting data: {str(e)}",
                "error": "export_error"
            }    
    @staticmethod
    def batch_import_questions(
        questions_data: List[Dict],
        auto_verify: bool = False,
        db: Session = None
    ) -> Dict:
        """
        Batch import multiple questions (from scrapers).
        
        Args:
            questions_data: List of question dictionaries
            auto_verify: If True, set to verified; if False, set to pending
            db: Database session
            
        Returns:
            {
                'success': bool,
                'imported_count': int,
                'failed_count': int,
                'total_count': int,
                'imported_ids': [list of question IDs],
                'errors': [list of error details],
                'message': str
            }
        """
        try:
            imported_ids = []
            errors = []
            
            for idx, q_data in enumerate(questions_data):
                try:
                    # Validate difficulty
                    if q_data.get('difficulty') not in ["Easy", "Medium", "Hard"]:
                        errors.append({
                            "index": idx,
                            "error": "Invalid difficulty. Must be Easy, Medium, or Hard"
                        })
                        continue
                    
                    # Validate required fields
                    required_fields = ['company_name', 'round_type', 'question_text', 'difficulty', 'source']
                    missing_fields = [f for f in required_fields if not q_data.get(f)]
                    if missing_fields:
                        errors.append({
                            "index": idx,
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        })
                        continue
                    
                    # Create question
                    question = Question(
                        company_name=q_data['company_name'].strip(),
                        round_type=q_data['round_type'].strip(),
                        question_text=q_data['question_text'].strip(),
                        difficulty=q_data['difficulty'],
                        source=q_data['source'].strip(),
                        solution_text=q_data.get('solution_text'),
                        solution_explanation=q_data.get('solution_explanation'),
                        frequency_score=min(q_data.get('frequency_score', 1), 10),
                        verification_status="verified" if auto_verify else "pending",
                        detected_topics=json.dumps({})  # To be filled by AI later
                    )
                    
                    db.add(question)
                    db.flush()
                    imported_ids.append(question.id)
                    
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "error": str(e)
                    })
            
            db.commit()
            
            return {
                "success": True,
                "imported_count": len(imported_ids),
                "failed_count": len(errors),
                "total_count": len(questions_data),
                "imported_ids": imported_ids,
                "errors": errors,
                "message": f"Imported {len(imported_ids)} of {len(questions_data)} questions"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "imported_count": 0,
                "failed_count": len(questions_data),
                "total_count": len(questions_data),
                "imported_ids": [],
                "errors": [{"error": str(e)}],
                "message": f"Batch import failed: {str(e)}"
            }
    
    @staticmethod
    def advanced_search(
        search_text: Optional[str] = None,
        company_name: Optional[str] = None,
        round_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        source: Optional[str] = None,
        topics: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
        min_frequency: Optional[int] = None,
        sort_by: str = "frequency",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> Dict:
        """
        Advanced search with full-text and multi-filter support.
        
        Args:
            search_text: Full-text search on question_text
            company_name: Filter by company
            round_type: Filter by round
            difficulty: Filter by difficulty
            source: Filter by source
            topics: Filter by detected topics (any match)
            skills: Filter by detected skills (any match)
            min_frequency: Minimum frequency score
            sort_by: Sort field (frequency, difficulty, attempts, recent)
            sort_order: Sort direction (asc, desc)
            limit: Results per page
            offset: Pagination offset
            db: Database session
            
        Returns:
            {
                'success': bool,
                'questions': [...],
                'count': int,
                'total': int,
                'message': str
            }
        """
        try:
            # Build base query - only verified questions
            query = db.query(Question).filter(
                Question.verification_status == "verified"
            )
            
            # Full-text search
            if search_text:
                query = query.filter(
                    Question.question_text.ilike(f"%{search_text}%")
                )
            
            # Company filter
            if company_name:
                query = query.filter(
                    Question.company_name.ilike(f"%{company_name}%")
                )
            
            # Round type filter
            if round_type:
                query = query.filter(
                    Question.round_type.ilike(f"%{round_type}%")
                )
            
            # Difficulty filter
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            
            # Source filter
            if source:
                query = query.filter(
                    Question.source.ilike(f"%{source}%")
                )
            
            # Frequency filter
            if min_frequency:
                query = query.filter(Question.frequency_score >= min_frequency)
            
            # Topic filter (if detected_topics JSON contains any of the topics)
            if topics:
                topic_conditions = []
                for topic in topics:
                    topic_conditions.append(
                        Question.detected_topics.ilike(f'%"{topic}"%')
                    )
                from sqlalchemy import or_
                query = query.filter(or_(*topic_conditions))
            
            # Skill filter (if detected_skills JSON contains any of the skills)
            if skills:
                skill_conditions = []
                for skill in skills:
                    skill_conditions.append(
                        Question.detected_skills.ilike(f'%{skill}%')
                    )
                from sqlalchemy import or_
                query = query.filter(or_(*skill_conditions))
            
            # Get total count
            total = query.count()
            
            # Sorting
            sort_field_map = {
                "frequency": Question.frequency_score,
                "difficulty": Question.difficulty,
                "attempts": Question.total_attempts,
                "recent": Question.created_at
            }
            
            sort_field = sort_field_map.get(sort_by, Question.frequency_score)
            
            if sort_order.lower() == "asc":
                query = query.order_by(sort_field.asc())
            else:
                query = query.order_by(sort_field.desc())
            
            # Pagination
            questions = query.limit(limit).offset(offset).all()
            
            question_list = []
            for q in questions:
                question_list.append({
                    "id": q.id,
                    "company_name": q.company_name,
                    "round_type": q.round_type,
                    "difficulty": q.difficulty,
                    "question_text": q.question_text,
                    "frequency_score": q.frequency_score,
                    "source": q.source,
                    "total_attempts": q.total_attempts,
                    "correct_attempts": q.correct_attempts,
                    "accuracy": round(
                        (q.correct_attempts / q.total_attempts * 100) if q.total_attempts > 0 else 0, 1
                    ),
                    "created_at": q.created_at.isoformat() if q.created_at else None
                })
            
            return {
                "success": True,
                "questions": question_list,
                "count": len(questions),
                "total": total,
                "message": f"Found {total} questions matching criteria"
            }
            
        except Exception as e:
            return {
                "success": False,
                "questions": [],
                "count": 0,
                "total": 0,
                "message": f"Error in advanced search: {str(e)}"
            }