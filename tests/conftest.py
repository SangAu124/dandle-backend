import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.domain.user import User
from app.domain.group import Group, GroupMembership
from app.domain.photo import Photo, PhotoTag
from app.domain.album import Album, AlbumShare
from app.domain.face import Face, FaceCollection, FaceMatch

# 테스트용 임시 SQLite 데이터베이스
@pytest.fixture(scope="session")
def temp_db():
    """Create a temporary database file for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    yield db_path
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="session")
def engine(temp_db):
    """Create test database engine"""
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    """Create test session local"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(TestingSessionLocal, tables):
    """데이터베이스 세션 픽스처"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Clear all data from tables to ensure test isolation
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()


@pytest.fixture
def override_get_db(db_session):
    """테스트용 데이터베이스 세션 오버라이드"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    return _override_get_db


@pytest.fixture
def client(override_get_db):
    """테스트 클라이언트 픽스처"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """샘플 사용자 데이터"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_group_data():
    """샘플 그룹 데이터"""
    return {
        "name": "Test Group",
        "description": "Test group description",
        "group_type": "class",
        "is_public": False,
        "max_members": 50
    }


@pytest.fixture
def sample_photo_data():
    """샘플 사진 데이터"""
    return {
        "filename": "test_photo.jpg",
        "original_filename": "test_photo.jpg",
        "file_path": "https://test-bucket.s3.amazonaws.com/test_photo.jpg",
        "file_size": 1024000,
        "width": 1920,
        "height": 1080,
        "format": "JPEG",
        "s3_bucket": "test-bucket",
        "s3_key": "photos/1/test_photo.jpg",
        "s3_url": "https://test-bucket.s3.amazonaws.com/test_photo.jpg",
        "uploaded_by_id": 1,
        "is_processed": False,
        "is_active": True
    }


@pytest.fixture
def sample_album_data():
    """샘플 앨범 데이터"""
    return {
        "name": "Test Album",
        "description": "Test album description",
        "album_type": "personal",
        "is_public": False,
        "created_by_id": 1,
        "is_active": True
    }


@pytest.fixture
def created_user(db_session, sample_user_data):
    """실제로 생성된 테스트 사용자"""
    from app.services.user_service import UserService

    service = UserService(db_session)
    user = service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"],
        full_name=sample_user_data["full_name"]
    )
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(created_user):
    """인증 헤더 생성"""
    from app.core.security import create_access_token

    token = create_access_token(data={"sub": str(created_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_face_data():
    """샘플 얼굴 데이터"""
    return {
        "face_id": "test_face_123",
        "confidence": 0.95,
        "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
        "landmarks": {"left_eye": {"x": 0.2, "y": 0.3}},
        "age_range": {"low": 25, "high": 35},
        "gender": "Male",
        "emotions": [{"type": "HAPPY", "confidence": 0.8}],
        "photo_id": 1,
        "is_active": True
    }