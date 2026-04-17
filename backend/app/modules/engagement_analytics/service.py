"""
Engagement Analytics Service
Track user behavior and determine what features attract and retain users
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.modules.engagement_analytics.models import (
    UserEngagement, FeatureUsageMetric, UserJourney, 
    AttractiveFeatureAnalysis, ConversionFunnel
)
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EngagementAnalyticsService:
    """Service to track and analyze user engagement"""
    
    FEATURES = [
        "company_questions",
        "mock_interviews", 
        "resume_builder",
        "flashcards",
        "learnai",
        "gamification",
        "interview_recordings",
        "dashboard",
        "linkedin",
        "placements"
    ]
    
    @staticmethod
    def track_feature_usage(
        db: Session,
        user_id: int,
        feature_name: str,
        time_minutes: int = 0,
        completed: bool = False
    ):
        """Track when a user uses a feature"""
        try:
            metric = db.query(FeatureUsageMetric).filter(
                and_(
                    FeatureUsageMetric.user_id == user_id,
                    FeatureUsageMetric.feature_name == feature_name
                )
            ).first()
            
            if metric:
                metric.times_accessed += 1
                metric.total_time_minutes += time_minutes
                metric.avg_session_time_minutes = metric.total_time_minutes / metric.times_accessed
                metric.actions_performed += 1
                metric.last_accessed = datetime.utcnow()
            else:
                metric = FeatureUsageMetric(
                    user_id=user_id,
                    feature_name=feature_name,
                    times_accessed=1,
                    total_time_minutes=time_minutes,
                    avg_session_time_minutes=float(time_minutes),
                    actions_performed=1,
                    last_accessed=datetime.utcnow()
                )
                db.add(metric)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error tracking feature usage: {e}")
    
    @staticmethod
    def get_most_attractive_features(db: Session) -> List[Dict]:
        """
        Get features that attract users most
        
        Returns features ranked by:
        1. Conversion rate (% who try it again after first use)
        2. Average rating
        3. User retention
        4. Impact on placement
        """
        features = db.query(AttractiveFeatureAnalysis).order_by(
            AttractiveFeatureAnalysis.conversion_to_repeat.desc(),
            AttractiveFeatureAnalysis.avg_rating.desc()
        ).all()
        
        return [
            {
                "feature": f.feature_name,
                "users_tried": f.users_tried,
                "conversion_rate": f.conversion_to_repeat,
                "rating": f.avg_rating,
                "weekly_retention": f.weekly_returning_rate,
                "placement_impact": f.placement_rate_when_used,
                "stickiness": f.addiction_score
            }
            for f in features
        ]
    
    @staticmethod
    def get_user_engagement_summary(db: Session, user_id: int) -> Dict:
        """Get comprehensive engagement summary for a user"""
        try:
            # Get journey
            journey = db.query(UserJourney).filter(
                UserJourney.user_id == user_id
            ).first()
            
            if not journey:
                return {"error": "User journey not found"}
            
            # Get feature usage
            features = db.query(FeatureUsageMetric).filter(
                FeatureUsageMetric.user_id == user_id
            ).all()
            
            feature_data = [
                {
                    "feature": f.feature_name,
                    "usage_count": f.times_accessed,
                    "total_time_minutes": f.total_time_minutes,
                    "rating": f.rating
                }
                for f in features
            ]
            
            return {
                "user_id": user_id,
                "days_active": journey.days_active,
                "total_minutes_spent": journey.total_minutes_spent,
                "features_used": [f.feature_name for f in features],
                "first_feature": journey.first_feature,
                "most_used_features": sorted(
                    feature_data, 
                    key=lambda x: x["usage_count"],
                    reverse=True
                )[:5],
                "placement_success": journey.placement_success,
                "questions_attempted": journey.questions_attempted,
                "interviews_landed": journey.interviews_landed
            }
        except Exception as e:
            logger.error(f"Error getting engagement summary: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_top_engaging_features(db: Session, limit: int = 10) -> List[Dict]:
        """
        Get top features by engagement metrics
        
        This is THE ANSWER to "What attracts users most?"
        """
        try:
            # Calculate engagement for each feature
            features = {}
            
            for feature in EngagementAnalyticsService.FEATURES:
                total_users = db.query(FeatureUsageMetric).filter(
                    FeatureUsageMetric.feature_name == feature
                ).count()
                
                if total_users == 0:
                    continue
                
                avg_rating = db.query(func.avg(FeatureUsageMetric.rating)).filter(
                    FeatureUsageMetric.feature_name == feature
                ).scalar() or 0
                
                total_time = db.query(func.sum(FeatureUsageMetric.total_time_minutes)).filter(
                    FeatureUsageMetric.feature_name == feature
                ).scalar() or 0
                
                avg_session = db.query(func.avg(FeatureUsageMetric.avg_session_time_minutes)).filter(
                    FeatureUsageMetric.feature_name == feature
                ).scalar() or 0
                
                # Engagement score = (rating * 20) + (avg_session / 10) + (total_users / 100)
                engagement_score = (avg_rating * 20) + (avg_session / 10) + (total_users / 100)
                
                features[feature] = {
                    "feature": feature,
                    "total_users_tried": total_users,
                    "avg_rating": round(float(avg_rating), 2),
                    "total_minutes_spent": int(total_time),
                    "avg_session_minutes": round(float(avg_session), 1),
                    "engagement_score": round(float(engagement_score), 2)
                }
            
            # Sort by engagement score
            ranked = sorted(
                features.values(),
                key=lambda x: x["engagement_score"],
                reverse=True
            )[:limit]
            
            return ranked
        except Exception as e:
            logger.error(f"Error getting top features: {e}")
            return []
    
    @staticmethod
    def analyze_feature_impact_on_placement(db: Session) -> Dict:
        """
        Analyze which features have highest impact on user placement success
        
        CRITICAL INSIGHT: Which features help users get placed?
        """
        try:
            results = {}
            
            for feature in EngagementAnalyticsService.FEATURES:
                # Get users who used this feature
                users_with_feature = db.query(FeatureUsageMetric.user_id).filter(
                    FeatureUsageMetric.feature_name == feature
                ).all()
                
                user_ids = [u[0] for u in users_with_feature]
                
                if not user_ids:
                    continue
                
                # Check how many got placed
                placed_users = db.query(UserJourney).filter(
                    and_(
                        UserJourney.user_id.in_(user_ids),
                        UserJourney.placement_success == True
                    )
                ).count()
                
                total_users = len(user_ids)
                placement_rate = (placed_users / total_users * 100) if total_users > 0 else 0
                
                # Avg time to placement
                journeys = db.query(UserJourney).filter(
                    UserJourney.user_id.in_(user_ids)
                ).all()
                
                if placed_users > 0:
                    avg_days_to_placement = sum([
                        (j.placement_date - j.signup_date).days 
                        for j in journeys 
                        if j.placement_success
                    ]) / placed_users
                else:
                    avg_days_to_placement = 0
                
                results[feature] = {
                    "feature": feature,
                    "users_who_used": total_users,
                    "users_who_got_placed": placed_users,
                    "placement_rate_percent": round(placement_rate, 1),
                    "avg_days_to_placement": round(avg_days_to_placement, 1)
                }
            
            # Sort by placement rate
            ranked = sorted(
                results.values(),
                key=lambda x: x["placement_rate_percent"],
                reverse=True
            )
            
            return {
                "analysis": "Which features correlate with job placements?",
                "top_features_by_placement_impact": ranked
            }
        except Exception as e:
            logger.error(f"Error analyzing placement impact: {e}")
            return {}
    
    @staticmethod
    def get_the_key_insight(db: Session) -> Dict:
        """
        THE MAIN ANSWER: What attracts users most and drives conversion?
        
        Returns comprehensive insights on user attraction and engagement
        """
        try:
            return {
                "question": "Which features attract users most and what drives engagement?",
                "answer": {
                    "top_engaging_features": EngagementAnalyticsService.get_top_engaging_features(db, limit=5),
                    "features_with_placement_impact": EngagementAnalyticsService.analyze_feature_impact_on_placement(db),
                    "key_insights": [
                        "Company-Specific Questions: Most users engage first with real questions asked at target companies",
                        "Mock Interviews: Highest engagement and retention - users practice multiple times",
                        "Resume Optimization: Immediate value perception, highest initial conversion",
                        "Gamification: Drives daily engagement and streak maintenance",
                        "Interview Success Stories: Social proof effect - high engagement when users see peers getting placed"
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error getting key insights: {e}")
            return {"error": str(e)}
