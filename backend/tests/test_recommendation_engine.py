import pytest
from backend.app.modules.company_data.job_recommendation import JobRecommendationService
from backend.app.database.models import User


class TestJobRecommendationService:
    """Test the job recommendation engine."""

    def test_get_seniority_level_fresher(self):
        """Test seniority level calculation for fresher."""
        service = JobRecommendationService()
        level = service._get_seniority_level(0)
        assert level == "Fresher"

    def test_get_seniority_level_junior(self):
        """Test seniority level calculation for junior."""
        service = JobRecommendationService()
        level = service._get_seniority_level(2)
        assert level == "Junior"

    def test_get_seniority_level_senior(self):
        """Test seniority level calculation for senior."""
        service = JobRecommendationService()
        level = service._get_seniority_level(5)
        assert level == "Senior"

    def test_get_seniority_level_lead(self):
        """Test seniority level calculation for lead."""
        service = JobRecommendationService()
        level = service._get_seniority_level(10)
        assert level == "Lead"

    def test_get_roles_from_course(self):
        """Test role extraction from course name."""
        service = JobRecommendationService()
        
        # Test CS course
        roles = service._get_roles_from_course("B.Tech Computer Science")
        assert "SDE" in roles or "Software Engineer" in roles
        
        # Test Electronics course
        roles = service._get_roles_from_course("B.E. Electronics")
        assert len(roles) > 0

    def test_calculate_match_score(self):
        """Test match score calculation."""
        service = JobRecommendationService()
        
        # Perfect match
        score = service._calculate_match_score(
            user_seniority="Senior",
            job_seniority="Senior",
            user_role="SDE",
            job_role="SDE",
            placement_rate=95,
            avg_salary=20,
        )
        
        # Should be high score for perfect match
        assert score > 80

    def test_match_score_is_percentage(self):
        """Test that match score is between 0 and 100."""
        service = JobRecommendationService()
        
        score = service._calculate_match_score(
            user_seniority="Junior",
            job_seniority="Senior",
            user_role="SDE",
            job_role="QA",
            placement_rate=90,
            avg_salary=15,
        )
        
        assert 0 <= score <= 100


class TestDatabaseIntegration:
    """Test database integration for recommendations."""

    def test_recommendation_with_real_user(self, db):
        """Test getting recommendations for a real user."""
        # This would require seeded companies in test DB
        # Skipping for now as it requires full data setup
        pass
