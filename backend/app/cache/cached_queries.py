"""
Database query layer with intelligent caching.
Implements cache-aside pattern for common queries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.cache.redis_cache import get_cache, CACHE_KEYS
from app.models.company import Company
from app.models.job import Job
from app.models.user import User
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CachedQueries:
    """Database queries with built-in caching."""
    
    @staticmethod
    async def get_trending_companies(
        session: AsyncSession,
        limit: int = 10,
        cache_ttl: int = 3600
    ) -> List[Company]:
        """Get trending companies with caching."""
        cache = get_cache()
        cache_key = f"trending:companies:{limit}"
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached
        
        # Query database
        logger.info(f"Cache MISS: {cache_key} - querying database")
        query = select(Company).order_by(
            Company.view_count.desc()
        ).limit(limit)
        
        result = await session.execute(query)
        companies = result.scalars().unique().all()
        
        # Cache result
        cache.set(cache_key, companies, cache_ttl)
        return companies
    
    @staticmethod
    async def get_company_with_jobs(
        session: AsyncSession,
        company_id: int,
        cache_ttl: int = 3600
    ) -> Optional[dict]:
        """Get company with all its jobs."""
        cache = get_cache()
        cache_key = f"company:full:{company_id}"
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached
        
        # Query company
        logger.info(f"Cache MISS: {cache_key} - querying database")
        query = select(Company).where(Company.id == company_id)
        result = await session.execute(query)
        company = result.scalar_one_or_none()
        
        if not company:
            return None
        
        # Get jobs
        jobs_query = select(Job).where(Job.company_id == company_id)
        jobs_result = await session.execute(jobs_query)
        jobs = jobs_result.scalars().all()
        
        # Build result
        result_data = {
            "company": company.to_dict(),
            "jobs": [job.to_dict() for job in jobs],
            "job_count": len(jobs)
        }
        
        # Cache result
        cache.set(cache_key, result_data, cache_ttl)
        return result_data
    
    @staticmethod
    async def get_user_recommendations(
        session: AsyncSession,
        user_id: int,
        limit: int = 20,
        cache_ttl: int = 1800  # 30 minutes - shorter TTL for recommendations
    ) -> List[dict]:
        """Get personalized job recommendations for user."""
        cache = get_cache()
        cache_key = f"recommendations:{user_id}:{limit}"
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached
        
        # Query recommendations from database
        logger.info(f"Cache MISS: {cache_key} - computing recommendations")
        
        # Get user
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return []
        
        # Simple recommendation: match jobs to user skills
        # In production, use ML model
        jobs_query = select(Job).limit(limit)
        jobs_result = await session.execute(jobs_query)
        jobs = jobs_result.scalars().all()
        
        recommendations = [job.to_dict() for job in jobs]
        
        # Cache result
        cache.set(cache_key, recommendations, cache_ttl)
        return recommendations
    
    @staticmethod
    async def get_company_stats(
        session: AsyncSession,
        company_id: int,
        cache_ttl: int = 7200  # 2 hours
    ) -> dict:
        """Get company statistics."""
        cache = get_cache()
        cache_key = f"stats:company:{company_id}"
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached
        
        # Query stats
        logger.info(f"Cache MISS: {cache_key} - computing stats")
        
        company_query = select(Company).where(Company.id == company_id)
        company_result = await session.execute(company_query)
        company = company_result.scalar_one_or_none()
        
        if not company:
            return {}
        
        # Get job count
        jobs_query = select(Job).where(Job.company_id == company_id)
        jobs_result = await session.execute(jobs_query)
        jobs = jobs_result.scalars().all()
        
        stats = {
            "company_id": company_id,
            "company_name": company.name,
            "view_count": company.view_count,
            "job_count": len(jobs),
            "avg_salary": sum(job.salary_max or 0 for job in jobs) / len(jobs) if jobs else 0
        }
        
        # Cache result
        cache.set(cache_key, stats, cache_ttl)
        return stats


async def clear_company_cache(company_id: int):
    """Clear all cached data for a company."""
    cache = get_cache()
    cache.delete(f"company:full:{company_id}")
    cache.delete(f"stats:company:{company_id}")
    cache.delete("trending:companies:*")
    logger.info(f"Cleared cache for company {company_id}")
