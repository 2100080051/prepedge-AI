"""
Placement Tracking API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.modules.placements.service import PlacementTracker


# ===== SCHEMAS =====

class LogPlacementRequest(BaseModel):
    """Schema for logging a placement"""
    company_name: str
    salary_lpa: Optional[float] = None
    offer_letter_url: Optional[str] = None
    round_type: Optional[str] = None
    total_rounds: Optional[int] = None


class LogPlacementResponse(BaseModel):
    """Response schema for placement logging"""
    success: bool
    placement_id: Optional[int] = None
    message: str
    verification_status: Optional[str] = None
    xp_awarded: Optional[int] = None
    error: Optional[str] = None


class VerifyPlacementRequest(BaseModel):
    """Schema for verifying a placement"""
    placement_id: int


class VerifyPlacementResponse(BaseModel):
    """Response schema for placement verification"""
    success: bool
    message: str
    placement_id: Optional[int] = None
    verified_at: Optional[str] = None
    xp_awarded: Optional[int] = None
    error: Optional[str] = None


class PlacementStatsResponse(BaseModel):
    """Response schema for placement statistics"""
    success: bool
    total_placements: int
    verified_placements: int
    average_salary_lpa: float
    highest_salary_lpa: float
    top_companies: Dict[str, int]
    cached: bool
    last_updated: str


class LeaderboardEntry(BaseModel):
    """Single leaderboard entry"""
    rank: int
    user_id: int
    username: str
    placements: int
    verified_placements: int
    average_salary_lpa: float
    highest_salary_lpa: float


class LeaderboardResponse(BaseModel):
    """Response schema for placement leaderboard"""
    success: bool
    leaderboard: List[LeaderboardEntry]
    count: int


class UserPlacementResponse(BaseModel):
    """Response schema for user's placements"""
    success: bool
    placements: List[dict]
    count: int


class PendingPlacementResponse(BaseModel):
    """Response schema for pending placements"""
    success: bool
    placements: List[dict]
    count: int
    total: int


class DeletePlacementResponse(BaseModel):
    """Response schema for deleting a placement"""
    success: bool
    message: str


# ===== ROUTES =====

router = APIRouter(prefix="/placements", tags=["Placements"])


@router.post("/log", response_model=LogPlacementResponse)
async def log_placement(
    request: LogPlacementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Log a placement for the current user.
    
    Args:
        request: Placement details (company, salary, offer letter URL, etc.)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Placement record with verification status and XP awarded
    
    Example:
        POST /api/v1/placements/log
        {
            "company_name": "TCS",
            "salary_lpa": 15.5,
            "offer_letter_url": "https://...",
            "round_type": "Technical + HR",
            "total_rounds": 3
        }
    """
    try:
        result = PlacementTracker.log_placement(
            user_id=current_user.id,
            company_name=request.company_name,
            salary_lpa=request.salary_lpa,
            offer_letter_url=request.offer_letter_url,
            round_type=request.round_type,
            total_rounds=request.total_rounds,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error logging placement: {str(e)}"
        )


@router.post("/verify/{placement_id}", response_model=VerifyPlacementResponse)
async def verify_placement(
    placement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Verify a placement record (Admin only).
    
    Args:
        placement_id: ID of the placement to verify
        current_user: Authenticated user (must be admin)
        db: Database session
    
    Returns:
        Verification result with timestamp and XP awarded
    
    NOTE: This endpoint should be restricted to admins only.
    Currently relies on authentication layer for access control.
    """
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = PlacementTracker.verify_placement(
            placement_id=placement_id,
            admin_id=current_user.id,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error verifying placement: {str(e)}"
        )


@router.get("/stats", response_model=PlacementStatsResponse)
async def get_stats(db: Session = Depends(get_db)) -> Dict:
    """
    Get overall placement statistics.
    
    Returns:
        Placement statistics including:
        - Total number of placements
        - Verified placements count
        - Average salary
        - Highest salary
        - Top 5 companies by placement count
        
    Caching:
        Results are cached for 1 hour (3600 seconds) for performance.
        If cache expires, stats are recalculated from database.
    
    Example response:
        {
            "success": true,
            "total_placements": 47,
            "verified_placements": 45,
            "average_salary_lpa": 14.8,
            "highest_salary_lpa": 22.5,
            "top_companies": {
                "TCS": 12,
                "Infosys": 10,
                "Wipro": 8,
                "Amazon": 5,
                "Google": 3
            },
            "cached": true,
            "last_updated": "2026-03-29T10:30:00"
        }
    """
    try:
        result = PlacementTracker.get_placement_stats(db=db)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Error retrieving stats")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving stats: {str(e)}"
        )


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get the placement leaderboard - top users by verified placements.
    
    Args:
        limit: Number of top users to return (default 10, max 100)
        db: Database session
    
    Returns:
        Leaderboard with users ranked by number of verified placements.
        Shows placement count, salary information, etc.
    
    Example response:
        {
            "success": true,
            "leaderboard": [
                {
                    "rank": 1,
                    "user_id": 5,
                    "username": "priya_sharma",
                    "placements": 3,
                    "verified_placements": 3,
                    "average_salary_lpa": 18.5,
                    "highest_salary_lpa": 22.5
                },
                {
                    "rank": 2,
                    "user_id": 8,
                    "username": "arjun_patel",
                    "placements": 2,
                    "verified_placements": 2,
                    "average_salary_lpa": 15.0,
                    "highest_salary_lpa": 16.0
                }
            ],
            "count": 2
        }
    """
    try:
        # Limit the request to prevent abuse
        limit = min(limit, 100)
        
        result = PlacementTracker.get_leaderboard(limit=limit, db=db)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Error retrieving leaderboard")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving leaderboard: {str(e)}"
        )


@router.get("/user/me", response_model=UserPlacementResponse)
async def get_user_placements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get all placements logged by the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of all placements for the user with their status
    
    Example response:
        {
            "success": true,
            "placements": [
                {
                    "id": 5,
                    "company_name": "TCS",
                    "salary_lpa": 15.5,
                    "verification_status": "verified",
                    "round_type": "Technical + HR",
                    "created_at": "2026-03-30T10:00:00",
                    "verified_at": "2026-03-30T11:30:00"
                },
                {
                    "id": 6,
                    "company_name": "Infosys",
                    "salary_lpa": null,
                    "verification_status": "pending",
                    "round_type": "Online Test",
                    "created_at": "2026-03-30T12:00:00",
                    "verified_at": null
                }
            ],
            "count": 2
        }
    """
    try:
        result = PlacementTracker.get_user_placements(
            user_id=current_user.id,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Error retrieving placements")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving user placements: {str(e)}"
        )


@router.get("/pending", response_model=PendingPlacementResponse)
async def get_pending_placements(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get all pending placements for verification (Admin only).
    
    Args:
        limit: Number of results per page (default 50, max 100)
        offset: Number of results to skip (for pagination)
        current_user: Authenticated user (must be admin)
        db: Database session
    
    Returns:
        List of pending placements with user details for admin verification
    
    Example response:
        {
            "success": true,
            "placements": [
                {
                    "id": 3,
                    "user_id": 7,
                    "username": "raj_kumar",
                    "email": "raj@example.com",
                    "company_name": "Wipro",
                    "salary_lpa": 14.0,
                    "offer_letter_url": "https://...",
                    "round_type": "Technical + HR",
                    "total_rounds": 3,
                    "created_at": "2026-03-30T14:00:00"
                }
            ],
            "count": 1,
            "total": 8
        }
    """
    try:
        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = PlacementTracker.get_pending_placements(
            limit=limit,
            offset=offset,
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Error retrieving pending placements")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving pending placements: {str(e)}"
        )


@router.delete("/{placement_id}", response_model=DeletePlacementResponse)
async def delete_placement(
    placement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Delete a placement record (users can only delete their own pending placements).
    
    Args:
        placement_id: ID of the placement to delete
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success/failure message
    
    Example:
        DELETE /api/v1/placements/5
        
        Response:
        {
            "success": true,
            "message": "Placement deleted successfully"
        }
    """
    try:
        result = PlacementTracker.delete_placement(
            placement_id=placement_id,
            user_id=current_user.id,
            db=db
        )
        
        if not result.get("success"):
            # Map error codes to HTTP status codes
            error_code = result.get("error", "")
            if error_code == "not_found":
                status_code = 404
            elif error_code == "unauthorized":
                status_code = 403
            else:
                status_code = 400
            
            raise HTTPException(
                status_code=status_code,
                detail=result.get("message", "Error deleting placement")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error deleting placement: {str(e)}"
        )
