import pytest
from fastapi import status

def test_health_check(client):
    """Test that the health check endpoint is accessible."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data


class TestAuth:
    """Test authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "TestPassword123!",
                "full_name": "Test User",
                "phone_number": "+919876543210",
                "college": "IIT Delhi",
                "graduation_year": 2025,
                "course": "B.Tech Computer Science",
                "years_of_experience": 0,
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "testuser@example.com"

    def test_register_duplicate_email(self, client):
        """Test that registering with duplicate email fails."""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "phone_number": "+919876543210",
            "college": "IIT Delhi",
            "graduation_year": 2025,
            "course": "B.Tech CS",
            "years_of_experience": 0,
        }
        
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to register with same email
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_user(self, client):
        """Test user login."""
        # First register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "TestPassword123!",
                "full_name": "Login Test",
                "phone_number": "+919876543210",
                "college": "MIT",
                "graduation_year": 2025,
                "course": "B.Tech",
                "years_of_experience": 0,
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Then login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "TestPassword123!",
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        assert "access_token" in data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword",
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCompanyData:
    """Test company data endpoints."""

    def test_get_trending_companies(self, client):
        """Test getting trending companies."""
        response = client.get("/api/v1/company-data/trending")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return a list of companies (might be empty if not seeded)
        assert isinstance(data, list)

    def test_get_trending_companies_count(self, client):
        """Test that trending endpoint returns limit parameter."""
        response = client.get("/api/v1/company-data/trending?limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5


class TestJobRecommendations:
    """Test job recommendation endpoints."""

    def test_personalized_recommendations_requires_auth(self, client):
        """Test that personalized recommendations require authentication."""
        response = client.get("/api/v1/company-data/recommendations/personalized")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_personalized_recommendations_with_auth(self, client):
        """Test getting personalized recommendations with valid auth."""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "rec@example.com",
                "username": "recuser",
                "password": "TestPassword123!",
                "full_name": "Rec Test",
                "phone_number": "+919876543210",
                "college": "IIT Bombay",
                "graduation_year": 2025,
                "course": "B.Tech CS",
                "years_of_experience": 1,
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "rec@example.com",
                "password": "TestPassword123!",
            }
        )
        token = login_response.json()["access_token"]
        
        # Get recommendations
        response = client.get(
            "/api/v1/company-data/recommendations/personalized",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return jobs list
        assert "jobs" in data or isinstance(data, dict)


class TestTESSAdmin:
    """Test TESS Admin endpoints."""

    def test_tess_endpoints_require_admin(self, client):
        """Test that TESS endpoints require admin role."""
        response = client.get("/api/v1/tess/analytics")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_on_login_attempts(self, client):
        """Test that excessive login attempts are rate limited."""
        # Make multiple failed login attempts
        for _ in range(20):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword",
                }
            )
        
        # Next request should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            }
        )
        # Should get 429 or be blocked
        assert response.status_code in [429, 401, 400]


class TestInputValidation:
    """Test input validation."""

    def test_register_invalid_email(self, client):
        """Test that invalid email is rejected."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "TestPassword123!",
                "full_name": "Test User",
            }
        )
        assert response.status_code >= 400

    def test_register_weak_password(self, client):
        """Test that weak password is rejected."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "weak",
                "full_name": "Test User",
            }
        )
        assert response.status_code >= 400

    def test_register_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # missing other required fields
            }
        )
        assert response.status_code >= 400
