from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.database.models import Flashcard, User
from typing import Dict, List, Optional
import random
import math


class FlashcardService:
    """
    Service for managing flashcards with spaced repetition (SM-2 algorithm)
    SM-2: https://en.wikipedia.org/wiki/SuperMemo#SM-2_algorithm
    """

    # SM-2 Constants
    INITIAL_INTERVAL = 1  # days
    INITIAL_EASE = 2.5
    MIN_EASE = 1.3

    @staticmethod
    def create_flashcard(
        topic: str,
        question: str,
        answer: str,
        difficulty: str = "medium",
        company: str = None,
        db: Session = None
    ) -> Dict:
        """Create a new flashcard"""
        flashcard = Flashcard(
            topic=topic,
            question=question,
            answer=answer,
            difficulty=difficulty,
            company=company
        )
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)

        return {
            "success": True,
            "flashcard": {
                "id": flashcard.id,
                "topic": flashcard.topic,
                "question": flashcard.question,
                "answer": flashcard.answer,
                "difficulty": flashcard.difficulty,
                "company": flashcard.company,
                "created_at": flashcard.created_at
            }
        }

    @staticmethod
    def generate_from_content(
        user_id: int,
        content: str,
        topic: str,
        company: str = None,
        db: Session = None
    ) -> Dict:
        """
        Auto-generate flashcards from learning content
        In production, use LLM to extract Q&A pairs
        """
        # Placeholder for LLM-based generation
        # In production, call your LLM provider to extract Q&A pairs
        mock_cards = [
            {
                "question": "What are the main data structures in programming?",
                "answer": "Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables",
                "difficulty": "easy"
            },
            {
                "question": "Explain the difference between polymorphism and inheritance",
                "answer": "Inheritance is a mechanism to derive a class from existing classes. Polymorphism allows objects to take multiple forms and enables methods to be overridden.",
                "difficulty": "medium"
            },
            {
                "question": "What is the time complexity of binary search?",
                "answer": "O(log n) - logarithmic time complexity",
                "difficulty": "medium"
            }
        ]

        created_cards = []
        for card_data in mock_cards:
            result = FlashcardService.create_flashcard(
                topic=topic,
                question=card_data["question"],
                answer=card_data["answer"],
                difficulty=card_data["difficulty"],
                company=company,
                db=db
            )
            created_cards.append(result["flashcard"])

        return {
            "success": True,
            "count": len(created_cards),
            "flashcards": created_cards
        }

    @staticmethod
    def get_cards_for_review(
        user_id: int,
        limit: int = 20,
        topic: str = None,
        company: str = None,
        db: Session = None
    ) -> List[Dict]:
        """
        Get cards due for review using SM-2 algorithm
        Returns: cards sorted by priority (due soon first)
        """
        query = db.query(Flashcard)

        if topic:
            query = query.filter(Flashcard.topic == topic)

        if company:
            query = query.filter(Flashcard.company == company)

        # Get all cards (in production, filter by review history)
        cards = query.limit(limit).all()

        return [
            {
                "id": card.id,
                "topic": card.topic,
                "question": card.question,
                "answer": card.answer,
                "difficulty": card.difficulty,
                "company": card.company
            }
            for card in cards
        ]

    @staticmethod
    def record_review(
        user_id: int,
        card_id: int,
        quality: int,
        db: Session
    ) -> Dict:
        """
        Record a review attempt and calculate next review date
        quality: 0-5 (0=complete blackout, 3=correct with difficulty, 5=perfect)
        
        Returns: next_review_date using SM-2 algorithm
        """
        if not 0 <= quality <= 5:
            return {"error": "Quality must be between 0 and 5"}

        card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
        if not card:
            return {"error": "Card not found"}

        # SM-2 Algorithm
        # For initial review, use defaults
        ease_factor = FlashcardService.INITIAL_EASE
        interval = FlashcardService.INITIAL_INTERVAL

        # Calculate next interval based on quality
        if quality < 3:
            # Incorrect or incorrect with difficulty - reset interval
            interval = 1
        else:
            # Correct - increase interval using ease factor
            if interval == 1:
                interval = 3
            else:
                interval = math.ceil(interval * ease_factor)

        # Update ease factor
        ease_factor = max(
            FlashcardService.MIN_EASE,
            ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )

        next_review = datetime.utcnow() + timedelta(days=interval)

        return {
            "success": True,
            "card_id": card_id,
            "quality": quality,
            "next_interval": interval,
            "next_review_date": next_review,
            "ease_factor": round(ease_factor, 2)
        }

    @staticmethod
    def get_stats(
        user_id: int,
        topic: str = None,
        company: str = None,
        db: Session = None
    ) -> Dict:
        """
        Get flashcard learning statistics
        """
        query = db.query(Flashcard)

        if topic:
            query = query.filter(Flashcard.topic == topic)

        if company:
            query = query.filter(Flashcard.company == company)

        total_cards = query.count()

        # Get difficulty distribution
        difficulty_breakdown = db.query(
            Flashcard.difficulty,
            func.count(Flashcard.id).label("count")
        ).group_by(Flashcard.difficulty).all()

        # Get topic breakdown
        topic_breakdown = db.query(
            Flashcard.topic,
            func.count(Flashcard.id).label("count")
        ).group_by(Flashcard.topic).all()

        return {
            "total_cards": total_cards,
            "difficulty_breakdown": {
                d[0]: d[1] for d in difficulty_breakdown
            },
            "topics": {
                t[0]: t[1] for t in topic_breakdown
            },
            "companies": [
                company_name for company_name, _ in
                db.query(Flashcard.company, func.count(Flashcard.id)).group_by(
                    Flashcard.company
                ).filter(Flashcard.company != None).all()
            ]
        }

    @staticmethod
    def search_cards(
        query_text: str,
        limit: int = 20,
        db: Session = None
    ) -> List[Dict]:
        """Search flashcards by question or topic"""
        cards = db.query(Flashcard).filter(
            or_(
                Flashcard.question.ilike(f"%{query_text}%"),
                Flashcard.topic.ilike(f"%{query_text}%")
            )
        ).limit(limit).all()

        return [
            {
                "id": card.id,
                "topic": card.topic,
                "question": card.question,
                "difficulty": card.difficulty,
                "company": card.company
            }
            for card in cards
        ]

    @staticmethod
    def get_learning_plan(
        user_id: int,
        company: str,
        role: str,
        db: Session
    ) -> Dict:
        """
        Get personalized learning plan with flashcard topics
        Based on company and role requirements
        """
        # Get relevant cards for company/role
        company_cards = db.query(
            Flashcard.topic,
            func.count(Flashcard.id).label("count")
        ).filter(
            Flashcard.company == company
        ).group_by(Flashcard.topic).all()

        topics_by_difficulty = db.query(
            Flashcard.topic,
            Flashcard.difficulty,
            func.count(Flashcard.id).label("count")
        ).group_by(
            Flashcard.topic,
            Flashcard.difficulty
        ).all()

        # Create learning path
        learning_path = {
            "company": company,
            "role": role,
            "total_topics": len(company_cards),
            "recommended_order": [
                {
                    "order": idx + 1,
                    "topic": topic,
                    "cards": count,
                    "estimated_hours": max(count / 10, 1)
                }
                for idx, (topic, count) in enumerate(company_cards)
            ],
            "daily_goal": {
                "cards": 20,
                "minutes": 30
            },
            "estimated_completion_days": sum(count for _, count in company_cards) / 20
        }

        return {
            "success": True,
            "learning_plan": learning_path
        }

    @staticmethod
    def batch_create_from_list(
        cards_list: List[Dict],
        topic: str,
        company: str = None,
        db: Session = None
    ) -> Dict:
        """
        Create multiple flashcards from a list
        cards_list: [{"question": "...", "answer": "...", "difficulty": "..."}]
        """
        created = []

        for card_data in cards_list:
            result = FlashcardService.create_flashcard(
                topic=topic,
                question=card_data.get("question", ""),
                answer=card_data.get("answer", ""),
                difficulty=card_data.get("difficulty", "medium"),
                company=company,
                db=db
            )
            created.append(result["flashcard"])

        return {
            "success": True,
            "count": len(created),
            "flashcards": created
        }

    @staticmethod
    def get_review_session(
        user_id: int,
        session_size: int = 20,
        topic: str = None,
        company: str = None,
        db: Session = None
    ) -> Dict:
        """
        Start a new review session with cards due for review
        """
        cards = FlashcardService.get_cards_for_review(
            user_id=user_id,
            limit=session_size,
            topic=topic,
            company=company,
            db=db
        )

        # Shuffle cards for variety
        random.shuffle(cards)

        return {
            "success": True,
            "session_size": len(cards),
            "topic": topic,
            "company": company,
            "cards": cards,
            "estimated_duration_minutes": len(cards) * 1.5  # ~1.5 min per card
        }

    @staticmethod
    def end_review_session(
        user_id: int,
        session_data: Dict,
        db: Session
    ) -> Dict:
        """
        End a review session and update user's progress
        """
        results = session_data.get("results", [])  # [{card_id, quality}]
        
        total_cards = len(results)
        correct_count = sum(1 for r in results if r.get("quality", 0) >= 3)
        accuracy = (correct_count / total_cards * 100) if total_cards > 0 else 0

        # Record each review
        for result in results:
            FlashcardService.record_review(
                user_id=user_id,
                card_id=result["card_id"],
                quality=result["quality"],
                db=db
            )

        return {
            "success": True,
            "total_reviewed": total_cards,
            "correct": correct_count,
            "accuracy": round(accuracy, 1),
            "next_review_count": len([r for r in results if r.get("quality", 0) < 3])
        }
