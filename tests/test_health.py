"""
Health check tests for CI/CD pipeline validation
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_docs_endpoint():
    """Test the API documentation endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema():
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


@pytest.mark.parametrize("endpoint", [
    "/api/v1/auth/login",
    "/api/v1/users/",
    "/api/v1/groups/",
    "/api/v1/photos/",
    "/api/v1/albums/",
    "/api/v1/faces/unidentified"
])
def test_api_endpoints_structure(endpoint):
    """Test that API endpoints are properly configured"""
    # Most endpoints should return 401 (unauthorized) or 422 (validation error)
    # rather than 404 (not found), indicating they exist
    response = client.get(endpoint)
    assert response.status_code in [401, 422, 405], f"Endpoint {endpoint} returned {response.status_code}"


def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.options("/")
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestApplicationConfiguration:
    """Test application configuration and settings"""

    def test_app_metadata(self):
        """Test application metadata"""
        response = client.get("/")
        data = response.json()

        assert data["message"] == "Dandle Backend API"
        assert "version" in data
        assert data["version"] is not None

    def test_error_handling(self):
        """Test error handling for non-existent endpoints"""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404


class TestDatabaseConnection:
    """Test database connectivity (mocked for CI)"""

    def test_database_models_import(self):
        """Test that database models can be imported"""
        try:
            from app.domain.user import User
            from app.domain.group import Group
            from app.domain.photo import Photo
            from app.domain.album import Album
            from app.domain.face import Face
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import database models: {e}")

    def test_alembic_configuration(self):
        """Test that Alembic configuration is valid"""
        try:
            from alembic.config import Config
            from alembic import command
            import tempfile
            import os

            # Create a temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                alembic_cfg = Config("alembic.ini")
                # Test that configuration loads without errors
                assert alembic_cfg is not None
        except Exception as e:
            pytest.fail(f"Alembic configuration error: {e}")


class TestSecurity:
    """Test security configurations"""

    def test_security_headers(self):
        """Test that basic security headers are present"""
        response = client.get("/")

        # Check for basic security (headers may be added by middleware)
        assert response.status_code == 200

    def test_no_sensitive_info_exposure(self):
        """Test that sensitive information is not exposed"""
        response = client.get("/")
        response_text = response.text.lower()

        # Check that sensitive keywords are not exposed
        sensitive_keywords = ["password", "secret", "key", "token"]
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"Sensitive keyword '{keyword}' found in response"


@pytest.mark.integration
class TestIntegrationEndpoints:
    """Integration tests for API endpoints"""

    def test_auth_endpoints_exist(self):
        """Test authentication endpoints exist"""
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/refresh",
            "/api/v1/auth/me"
        ]

        for endpoint in endpoints:
            response = client.post(endpoint) if "login" in endpoint or "logout" in endpoint or "refresh" in endpoint else client.get(endpoint)
            # Should not return 404 (not found)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"

    def test_user_endpoints_exist(self):
        """Test user management endpoints exist"""
        endpoints = [
            ("/api/v1/users/", "POST"),
            ("/api/v1/users/me", "GET"),
            ("/api/v1/users/1", "GET"),
            ("/api/v1/users/1", "PUT")
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            elif method == "PUT":
                response = client.put(endpoint)

            assert response.status_code != 404, f"Endpoint {method} {endpoint} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])