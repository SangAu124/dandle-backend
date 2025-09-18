import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_docs_endpoints(client: TestClient):
    """API 문서 엔드포인트 테스트"""
    # OpenAPI JSON
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200

    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200


def test_user_endpoints_exist(client: TestClient):
    """사용자 API 엔드포인트 존재 확인"""
    # 사용자 생성 엔드포인트 (구현되지 않았으므로 501 에러 예상)
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 501  # Not Implemented


def test_group_endpoints_exist(client: TestClient):
    """그룹 API 엔드포인트 존재 확인"""
    # 그룹 생성 엔드포인트 (구현되지 않았으므로 501 에러 예상)
    response = client.post("/api/v1/groups/", json={
        "name": "Test Group",
        "group_type": "class"
    })
    assert response.status_code == 501  # Not Implemented


def test_photo_endpoints_exist(client: TestClient):
    """사진 API 엔드포인트 존재 확인"""
    # 사진 목록 조회 엔드포인트 (구현되지 않았으므로 501 에러 예상)
    response = client.get("/api/v1/photos/")
    assert response.status_code == 501  # Not Implemented


def test_album_endpoints_exist(client: TestClient):
    """앨범 API 엔드포인트 존재 확인"""
    # 앨범 목록 조회 엔드포인트 (구현되지 않았으므로 501 에러 예상)
    response = client.get("/api/v1/albums/")
    assert response.status_code == 501  # Not Implemented


def test_face_endpoints_exist(client: TestClient):
    """얼굴 인식 API 엔드포인트 존재 확인"""
    # 미식별 얼굴 목록 조회 엔드포인트 (구현되지 않았으므로 501 에러 예상)
    response = client.get("/api/v1/faces/unidentified")
    assert response.status_code == 501  # Not Implemented


def test_cors_headers(client: TestClient):
    """CORS 헤더 테스트"""
    response = client.options("/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })

    # CORS가 올바르게 설정되었는지 확인
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers