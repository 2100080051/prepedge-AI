"""
PlacementTracker Service - Manages placement tracking and verification
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from app.database.models import PlacementRecord, PlacementStats, User
from app.modules.gamification.service import GamificationService
from typing import Dict, List, Optional
import json


class PlacementTracker:
    """Service for managing placement tracking and statistics"""
    
    # XP reward for successful placement logging
    PLACEMENT_XP_REWARD = 50
    VERIFIED_PLACEMENT_XP_REWARD = 50
    
    @staticmethod
    def log_placement(
        user_id: int,
        company_name: str,
        salary_lpa: Optional[float] = None,
        offer_letter_url: Optional[str] = None,
        round_type: Optional[str] = None,
        total_rounds: Optional[int] = None,
        db: Session = None
    ) -> Dict:
        """
        Log a new placement for a user.
        
        Returns:
            {
                'success': bool,
                'placement_id': int,
                'message': str,
                'verification_status': str,
                'xp_awarded': int
            }
        """
        try:
            # Check for duplicates - same user, same company within 30 days
            existing = db.query(PlacementRecord).filter(
                PlacementRecord.user_id == user_id,
                PlacementRecord.company_name == company_name.strip(),
                PlacementRecord.created_at >= datetime.utcnow() - timedelta(days=30)
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "message": f"Placement already logged for {company_name} within the last 30 days",
                    "error": "duplicate_placement"
                }
            
            # Create new placement record
            placement = PlacementRecord(
                user_id=user_id,
                company_name=company_name.strip(),
                salary_lpa=salary_lpa,
                offer_letter_url=offer_letter_url,
                round_type=round_type,
                total_rounds=total_rounds,
                verification_status="pending"
            )
            
            db.add(placement)
            db.flush()  # Flush to get the placement ID
            placement_id = placement.id
            
            # Award initial XP for logging placement
            xp_result = GamificationService.add_xp(
                user_id,
                "placement_logged",
                db
            )
            
            # Notify admins (would send notification service in real implementation)
            # For now, just mark in logs
            
            db.commit()
            
            return {
                "success": True,
                "placement_id": placement_id,
                "message": "Placement logged successfully. Awaiting admin verification.",
                "verification_status": "pending",
                "xp_awarded": xp_result.get("xp_gained", 0)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error logging placement: {str(e)}",
                "error": "log_placement_error"
            }
    
    @staticmethod
    def verify_placement(
        placement_id: int,
        admin_id: int,
        db: Session = None
    ) -> Dict:
        """
        Verify a placement record by admin.
        
        Returns:
            {
                'success': bool,
                'message': str,
                'verified_at': str,
                'xp_awarded': int
            }
        """
        try:
            placement = db.query(PlacementRecord).filter(
                PlacementRecord.id == placement_id
            ).first()
            
            if not placement:
                return {
                    "success": False,
                    "message": "Placement record not found",
                    "error": "not_found"
                }
            
            if placement.verification_status == "verified":
                return {
                    "success": False,
                    "message": "Placement already verified",
                    "error": "already_verified"
                }
            
            # Update verification status
            placement.verification_status = "verified"
            placement.verified_by_admin = True
            placement.verified_at = datetime.utcnow()
            
            # Award bonus XP for verified placement
            xp_result = GamificationService.add_xp(
                placement.user_id,
                "placement_verified",
                db
            )
            
            # Update stats cache
            PlacementTracker._update_placement_stats(db)
            
            db.commit()
            
            return {
                "success": True,
                "message": "Placement verified successfully",
                "verified_at": placement.verified_at.isoformat(),
                "placement_id": placement_id,
                "xp_awarded": xp_result.get("xp_gained", 0)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error verifying placement: {str(e)}",
                "error": "verify_placement_error"
            }
    
    @staticmethod
    def get_placement_stats(db: Session = None) -> Dict:
        """
        Get overall placement statistics.
        
        Returns:
            {
                'total_placements': int,
                'verified_placements': int,
                'average_salary': float,
                'highest_salary': float,
                'top_companies': dict,
                'last_updated': str
            }
        """
        try:
            # Try to get cached stats
            stats = db.query(PlacementStats).filter(PlacementStats.id == 1).first()
            
            if stats:
                # Check if cache is still valid
                time_since_update = datetime.utcnow() - stats.last_updated
                if time_since_update.total_seconds() < stats.cache_ttl_seconds:
                    # Cache is still valid
                    top_companies = json.loads(stats.top_companies) if stats.top_companies else {}
                    return {
                        "success": True,
                        "total_placements": stats.total_placements,
                        "verified_placements": stats.total_verified_placements,
                        "average_salary_lpa": round(stats.average_salary_lpa, 2),
                        "highest_salary_lpa": stats.highest_salary_lpa,
                        "top_companies": top_companies,
                        "cached": True,
                        "last_updated": stats.last_updated.isoformat()
                    }
            
            # If cache is expired or doesn't exist, recalculate
            PlacementTracker._update_placement_stats(db)
            
            # Get the updated stats
            stats = db.query(PlacementStats).filter(PlacementStats.id == 1).first()
            top_companies = json.loads(stats.top_companies) if stats.top_companies else {}
            
            return {
                "success": True,
                "total_placements": stats.total_placements,
                "verified_placements": stats.total_verified_placements,
                "average_salary_lpa": round(stats.average_salary_lpa, 2),
                "highest_salary_lpa": stats.highest_salary_lpa,
                "top_companies": top_companies,
                "cached": False,
                "last_updated": stats.last_updated.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving stats: {str(e)}",
                "error": "stats_error"
            }
    
    @staticmethod
    def get_leaderboard(limit: int = 10, db: Session = None) -> Dict:
        """
        Get placement leaderboard - users with most placements.
        
        Returns:
            {
                'success': bool,
                'leaderboard': [
                    {
                        'rank': int,
                        'user_id': int,
                        'username': str,
                        'placements': int,
                        'verified_placements': int,
                        'average_salary': float,
                        'highest_salary': float
                    }
                ]
            }
        """
        try:
            # Query to get users with most placements (verified only)
            leaderboard_data = db.query(
                PlacementRecord.user_id,
                User.username,
                func.count(PlacementRecord.id).label('total_placements'),
                func.sum(
                    cast(PlacementRecord.verification_status == "verified", Integer)
                ).label('verified_placements'),
                func.avg(PlacementRecord.salary_lpa).label('average_salary'),
                func.max(PlacementRecord.salary_lpa).label('highest_salary')
            ).join(User, User.id == PlacementRecord.user_id).filter(
                PlacementRecord.verification_status == "verified"
            ).group_by(
                PlacementRecord.user_id,
                User.username
            ).order_by(
                func.count(PlacementRecord.id).desc()
            ).limit(limit).all()
            
            leaderboard = []
            for rank, (user_id, username, total, verified, avg_sal, max_sal) in enumerate(leaderboard_data, 1):
                leaderboard.append({
                    "rank": rank,
                    "user_id": user_id,
                    "username": username,
                    "placements": total or 0,
                    "verified_placements": verified or 0,
                    "average_salary_lpa": round(avg_sal, 2) if avg_sal else 0,
                    "highest_salary_lpa": max_sal or 0
                })
            
            return {
                "success": True,
                "leaderboard": leaderboard,
                "count": len(leaderboard)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving leaderboard: {str(e)}",
                "error": "leaderboard_error"
            }
    
    @staticmethod
    def _update_placement_stats(db: Session) -> None:
        """
        Internal method to update cached placement statistics.
        Called whenever a placement is verified or stats are stale.
        """
        try:
            # Calculate stats from database
            total_placements = db.query(func.count(PlacementRecord.id)).scalar() or 0
            verified_placements = db.query(func.count(PlacementRecord.id)).filter(
                PlacementRecord.verification_status == "verified"
            ).scalar() or 0
            
            avg_salary = db.query(func.avg(PlacementRecord.salary_lpa)).filter(
                PlacementRecord.verification_status == "verified",
                PlacementRecord.salary_lpa.isnot(None)
            ).scalar() or 0.0
            
            max_salary = db.query(func.max(PlacementRecord.salary_lpa)).filter(
                PlacementRecord.verification_status == "verified",
                PlacementRecord.salary_lpa.isnot(None)
            ).scalar() or 0.0
            
            # Get top 5 companies
            top_companies_query = db.query(
                PlacementRecord.company_name,
                func.count(PlacementRecord.id).label('count')
            ).filter(
                PlacementRecord.verification_status == "verified"
            ).group_by(
                PlacementRecord.company_name
            ).order_by(
                func.count(PlacementRecord.id).desc()
            ).limit(5).all()
            
            top_companies = {
                company: count for company, count in top_companies_query
            }
            
            # Update or create stats record
            stats = db.query(PlacementStats).filter(PlacementStats.id == 1).first()
            
            if stats:
                stats.total_placements = total_placements
                stats.total_verified_placements = verified_placements
                stats.average_salary_lpa = avg_salary
                stats.highest_salary_lpa = max_salary
                stats.top_companies = json.dumps(top_companies)
                stats.last_updated = datetime.utcnow()
            else:
                stats = PlacementStats(
                    id=1,
                    total_placements=total_placements,
                    total_verified_placements=verified_placements,
                    average_salary_lpa=avg_salary,
                    highest_salary_lpa=max_salary,
                    top_companies=json.dumps(top_companies)
                )
                db.add(stats)
            
            db.commit()
            
        except Exception as e:
            print(f"Error updating placement stats: {str(e)}")
            db.rollback()
    
    @staticmethod
    def get_user_placements(user_id: int, db: Session = None) -> Dict:
        """
        Get all placements for a specific user.
        
        Args:
            user_id: User ID to fetch placements for
            db: Database session
            
        Returns:
            {
                'success': bool,
                'placements': [
                    {
                        'id': int,
                        'company_name': str,
                        'salary_lpa': float,
                        'verification_status': str,
                        'created_at': str,
                        'verified_at': str (optional)
                    }
                ],
                'count': int
            }
        """
        try:
            placements = db.query(PlacementRecord).filter(
                PlacementRecord.user_id == user_id
            ).order_by(PlacementRecord.created_at.desc()).all()
            
            placement_list = []
            for p in placements:
                placement_list.append({
                    "id": p.id,
                    "company_name": p.company_name,
                    "salary_lpa": p.salary_lpa,
                    "verification_status": p.verification_status,
                    "round_type": p.round_type,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "verified_at": p.verified_at.isoformat() if p.verified_at else None
                })
            
            return {
                "success": True,
                "placements": placement_list,
                "count": len(placement_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving user placements: {str(e)}",
                "error": "user_placements_error"
            }
    
    @staticmethod
    def get_pending_placements(limit: int = 50, offset: int = 0, db: Session = None) -> Dict:
        """
        Get all pending placements (admin only).
        
        Args:
            limit: Number of results to return (default 50, max 100)
            offset: Number of results to skip (for pagination)
            db: Database session
            
        Returns:
            {
                'success': bool,
                'placements': [
                    {
                        'id': int,
                        'user_id': int,
                        'username': str,
                        'company_name': str,
                        'salary_lpa': float,
                        'offer_letter_url': str,
                        'created_at': str,
                        'round_type': str
                    }
                ],
                'count': int,
                'total': int
            }
        """
        try:
            limit = min(limit, 100)  # Cap at 100
            
            # Get total count
            total = db.query(func.count(PlacementRecord.id)).filter(
                PlacementRecord.verification_status == "pending"
            ).scalar() or 0
            
            # Get paginated results
            pending = db.query(PlacementRecord, User).join(
                User, User.id == PlacementRecord.user_id
            ).filter(
                PlacementRecord.verification_status == "pending"
            ).order_by(PlacementRecord.created_at.asc()).limit(limit).offset(offset).all()
            
            placements = []
            for placement, user in pending:
                placements.append({
                    "id": placement.id,
                    "user_id": placement.user_id,
                    "username": user.username,
                    "email": user.email,
                    "company_name": placement.company_name,
                    "salary_lpa": placement.salary_lpa,
                    "offer_letter_url": placement.offer_letter_url,
                    "round_type": placement.round_type,
                    "total_rounds": placement.total_rounds,
                    "created_at": placement.created_at.isoformat() if placement.created_at else None
                })
            
            return {
                "success": True,
                "placements": placements,
                "count": len(placements),
                "total": total
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving pending placements: {str(e)}",
                "error": "pending_placements_error"
            }
    
    @staticmethod
    def delete_placement(placement_id: int, user_id: int, db: Session = None) -> Dict:
        """
        Delete a placement record (user can only delete their own pending placements).
        
        Args:
            placement_id: ID of placement to delete
            user_id: ID of user attempting to delete
            db: Database session
            
        Returns:
            {
                'success': bool,
                'message': str
            }
        """
        try:
            placement = db.query(PlacementRecord).filter(
                PlacementRecord.id == placement_id
            ).first()
            
            if not placement:
                return {
                    "success": False,
                    "message": "Placement not found",
                    "error": "not_found"
                }
            
            # Can only delete own pending placements
            if placement.user_id != user_id:
                return {
                    "success": False,
                    "message": "Cannot delete placements of other users",
                    "error": "unauthorized"
                }
            
            if placement.verification_status != "pending":
                return {
                    "success": False,
                    "message": f"Cannot delete {placement.verification_status} placements",
                    "error": "invalid_status"
                }
            
            # Delete the placement
            db.delete(placement)
            db.commit()
            
            # Invalidate stats cache
            stats = db.query(PlacementStats).filter(PlacementStats.id == 1).first()
            if stats:
                stats.cache_ttl_seconds = 0
                db.commit()
            
            return {
                "success": True,
                "message": "Placement deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Error deleting placement: {str(e)}",
                "error": "delete_error"
            }
