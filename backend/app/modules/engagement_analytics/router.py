"""
Engagement Analytics Router
REST API endpoints for tracking and analyzing user engagement
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.modules.engagement_analytics.service import EngagementAnalyticsService
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/engagement",
    tags=["engagement-analytics"]
)


class FeatureTracking(BaseModel):
    feature_name: str
    time_minutes: int = 0
    completed: bool = False


class FeedbackSubmission(BaseModel):
    feature_name: str
    feedback_type: str  # bug, suggestion, compliment, complaint
    rating: int  # 1-5
    comment: str


@router.post("/track-feature", response_model=dict)
async def track_feature_usage(
    tracking: FeatureTracking,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track when a user engages with a feature
    
    This endpoint records:
    - Feature name
    - Time spent
    - Whether they completed an action
    
    Used to answer: "Which features attract users?"
    """
    try:
        EngagementAnalyticsService.track_feature_usage(
            db=db,
            user_id=current_user.id,
            feature_name=tracking.feature_name,
            time_minutes=tracking.time_minutes,
            completed=tracking.completed
        )
        
        return {
            "status": "success",
            "message": f"Tracked usage of {tracking.feature_name}",
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"Error tracking feature: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/my-analytics", response_model=dict)
async def get_my_engagement_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized engagement analytics for the current user
    
    Shows:
    - Features used
    - Time spent
    - Engagement progress
    - Path to placement
    """
    try:
        summary = EngagementAnalyticsService.get_user_engagement_summary(db, current_user.id)
        
        return {
            "status": "success",
            "user_analytics": summary
        }
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/most-attractive-features", response_model=dict)
async def get_most_attractive_features(
    db: Session = Depends(get_db)
):
    """
    Get features that attract and retain users most
    
    ANSWER TO: "Which features attract users more?"
    
    Returns features ranked by:
    - Repeat usage rate (conversion to re-engagement)
    - User rating
    - Retention rate
    - Impact on placement success
    """
    try:
        features = EngagementAnalyticsService.get_most_attractive_features(db)
        
        return {
            "status": "success",
            "question": "Which features attract and retain users most?",
            "insight": "Higher conversion_to_repeat + rating = strongest user attraction",
            "top_features": features
        }
    except Exception as e:
        logger.error(f"Error getting attractive features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/top-engaging", response_model=dict)
async def get_top_engaging_features(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get top features by overall engagement metrics
    
    Engagement Score = (Rating × 20) + (Avg Session Time / 10) + (Total Users / 100)
    
    Tells us which features users spend most time on and rate highest
    """
    try:
        features = EngagementAnalyticsService.get_top_engaging_features(db, limit)
        
        return {
            "status": "success",
            "insight": "Features ranked by engagement (rating, session time, user adoption)",
            "methodology": "engagement_score = (rating * 20) + (avg_session / 10) + (users / 100)",
            "top_features": features
        }
    except Exception as e:
        logger.error(f"Error getting engaging features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/placement-impact", response_model=dict)
async def get_feature_placement_impact(
    db: Session = Depends(get_db)
):
    """
    CRITICAL INSIGHT: Which features correlate with successful job placement?
    
    This analysis shows:
    - Placement rate for users who used each feature
    - Average time from signup to placement
    - Which features actually help users get jobs
    
    The question: "Company questions, mock interviews, or resume builder - which helps most?"
    """
    try:
        impact = EngagementAnalyticsService.analyze_feature_impact_on_placement(db)
        
        return {
            "status": "success",
            "insight": "Features ranked by their correlation with job placement success",
            "interpretation": "High placement_rate = feature is most helpful for actually getting jobs",
            "analysis": impact
        }
    except Exception as e:
        logger.error(f"Error analyzing placement impact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/the-key-insight", response_model=dict)
async def get_the_key_insight(
    db: Session = Depends(get_db)
):
    """
    THE MAIN ANSWER TO THE USER'S CRITICAL QUESTION:
    
    "Which thing attracts user more? I need to know"
    "What's present going on outside? These LLMs are not new, trained years ago.
     We should have real time data."
    
    This endpoint combines all analytics to return:
    1. Top engaging features
    2. Features that drive placement
    3. Key insights on user attraction
    
    INTERPRETATION:
    - Company-Specific Questions fetch real interview data → Users want CURRENT data, not LLM
    - Mock Interviews keep users engaged → Practice = confidence = placement
    - Resume Optimization shows immediate value → Quick wins build momentum
    - Gamification = daily engagement → Keeps users coming back
    - Success Stories = social proof → "If they can, so can I"
    """
    try:
        insight = EngagementAnalyticsService.get_the_key_insight(db)
        
        return {
            "status": "success",
            "analysis": insight
        }
    except Exception as e:
        logger.error(f"Error getting key insight: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/feedback", response_model=dict)
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a feature
    
    Helps us understand:
    - What's working (compliments)
    - What's broken (bugs)
    - What users want (suggestions)
    - What frustrates them (complaints)
    """
    try:
        # Log feedback for analysis
        logger.info(
            f"Feedback from user {current_user.id} on {feedback.feature_name}: "
            f"[{feedback.feedback_type}] Rating: {feedback.rating}/5 - {feedback.comment}"
        )
        
        return {
            "status": "success",
            "message": f"Thank you for your feedback on {feedback.feature_name}",
            "feedback_type": feedback.feedback_type,
            "rating": feedback.rating
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health", response_model=dict)
async def engagement_analytics_health(db: Session = Depends(get_db)):
    """Health check for engagement analytics module"""
    try:
        return {
            "status": "healthy",
            "module": "engagement_analytics",
            "features": [
                "track-feature",
                "my-analytics",
                "most-attractive-features",
                "top-engaging",
                "placement-impact",
                "the-key-insight",
                "feedback"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
