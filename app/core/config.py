from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 애플리케이션 기본 설정
    app_name: str = "Dandle Backend API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 데이터베이스 설정
    database_url: str = "sqlite:///./dandle_dev.db"

    # Redis 설정
    redis_url: str = "redis://localhost:6379/0"

    # JWT 설정
    jwt_secret: str  # 환경 변수에서 필수로 설정해야 함
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7일

    # AWS 설정
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "dandle-photos"

    # OAuth 설정
    apple_client_id: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_private_key: Optional[str] = None

    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Email 설정
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # CORS 설정
    cors_origins: str = "http://localhost:3000,http://localhost:8080"  # 개발환경용, 운영환경에서는 실제 도메인으로 설정

    # 파일 업로드 설정
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = ["image/jpeg", "image/png", "image/heic", "image/webp"]

    # 페이지네이션 설정
    default_page_size: int = 50
    max_page_size: int = 100

    # 얼굴 인식 설정
    face_similarity_threshold: float = 0.8
    face_confidence_threshold: float = 0.8

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()