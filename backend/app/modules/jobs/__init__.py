"""
Jobs Module - Phase 4b Implementation

Sub-modules:
- job_scrapers: Scrape jobs from company websites (FREE)
- job_matcher: Match users with jobs using scoring algorithm
- scheduler: Daily job digest/scraping scheduler
- router: API endpoints for job recommendations
"""

from app.modules.jobs.job_scrapers import JobScraperManager
from app.modules.jobs.job_matcher import JobMatcher, SmartJobRecommendation
from app.modules.jobs.scheduler import init_job_scheduler

__all__ = ['JobScraperManager', 'JobMatcher', 'SmartJobRecommendation', 'init_job_scheduler']
