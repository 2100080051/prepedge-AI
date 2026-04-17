from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database.models import User
from app.llm.circuit_breaker import get_llm_breaker_manager
from typing import Dict

router = APIRouter(prefix="/llm", tags=["LLM Monitoring"])


@router.get("/health")
async def get_llm_health(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get health status of all LLM providers
    Shows circuit breaker state for each provider
    """
    manager = get_llm_breaker_manager()
    states = manager.get_all_states()

    # Determine overall health
    all_closed = all(s["state"] == "closed" for s in states.values())
    any_open = any(s["state"] == "open" for s in states.values())

    overall_status = "healthy" if all_closed else ("degraded" if not any_open else "unhealthy")

    return {
        "success": True,
        "overall_status": overall_status,
        "providers": states,
        "message": {
            "healthy": "All LLM providers are operational",
            "degraded": "Some providers may be experiencing issues",
            "unhealthy": "LLM providers are down. Using fallbacks."
        }.get(overall_status)
    }


@router.get("/provider/{provider_name}")
async def get_provider_status(
    provider_name: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get detailed status of a specific LLM provider
    """
    manager = get_llm_breaker_manager()

    if provider_name not in manager.circuit_breakers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {provider_name}. Available: openrouter, groq, nvidia"
        )

    state = manager.circuit_breakers[provider_name].get_state()

    return {
        "success": True,
        "provider": provider_name,
        "status": state
    }


@router.post("/reset/{provider_name}")
async def reset_provider(
    provider_name: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Manually reset circuit breaker for a provider
    Admin only
    """
    manager = get_llm_breaker_manager()

    if provider_name not in manager.circuit_breakers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {provider_name}"
        )

    try:
        manager.reset_provider(provider_name)
        return {
            "success": True,
            "message": f"Circuit breaker reset for {provider_name}",
            "status": manager.circuit_breakers[provider_name].get_state()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-all")
async def reset_all(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Manually reset all circuit breakers
    Admin only
    """
    manager = get_llm_breaker_manager()
    manager.reset_all()

    return {
        "success": True,
        "message": "All circuit breakers reset",
        "providers": manager.get_all_states()
    }


@router.get("/stats")
async def get_llm_stats(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get LLM provider statistics and performance metrics
    """
    manager = get_llm_breaker_manager()
    states = manager.get_all_states()

    stats = {
        "total_providers": len(states),
        "healthy_providers": sum(1 for s in states.values() if s["state"] == "closed"),
        "degraded_providers": sum(1 for s in states.values() if s["state"] == "half_open"),
        "down_providers": sum(1 for s in states.values() if s["state"] == "open"),
        "providers": states
    }

    return {
        "success": True,
        "stats": stats
    }
