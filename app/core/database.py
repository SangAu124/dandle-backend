from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from typing import Generator

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dandle_dev.db"
)

# SQLAlchemy 엔진 생성
if DATABASE_URL.startswith("sqlite"):
    # SQLite용 설정
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL용 설정
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 (모든 ORM 모델의 기본 클래스)
Base = declarative_base()


def get_db() -> Generator:
    """
    데이터베이스 세션 의존성 주입용 함수
    FastAPI의 Depends에서 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    모든 테이블 생성
    애플리케이션 시작 시 호출
    """
    # 모든 모델 import (테이블 생성을 위해)
    from app.domain.user import User
    from app.domain.group import Group, GroupMembership
    from app.domain.photo import Photo, PhotoTag
    from app.domain.album import Album, AlbumShare
    from app.domain.face import Face, FaceCollection, FaceMatch

    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    모든 테이블 삭제
    테스트 환경에서 사용
    """
    Base.metadata.drop_all(bind=engine)