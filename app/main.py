from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables

# API 라우터 import
from app.api.user_router import router as user_router
from app.api.group_router import router as group_router
from app.api.photo_router import router as photo_router
from app.api.album_router import router as album_router
from app.api.face_router import router as face_router

app = FastAPI(
    title=settings.app_name,
    description="AI 기반 자동 얼굴 인식 및 사진 정리 서비스 백엔드",
    version=settings.app_version,
    debug=settings.debug
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(user_router, prefix="/api/v1")
app.include_router(group_router, prefix="/api/v1")
app.include_router(photo_router, prefix="/api/v1")
app.include_router(album_router, prefix="/api/v1")
app.include_router(face_router, prefix="/api/v1")


# 애플리케이션 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    # 데이터베이스 테이블 생성
    create_tables()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }