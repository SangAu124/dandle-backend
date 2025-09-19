from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from app.services.auth_service import AuthService
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int


class RefreshRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: str


class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """사용자 로그인

    Args:
        login_data: 이메일과 비밀번호
        db: 데이터베이스 세션

    Returns:
        JWT 액세스 토큰과 리프레시 토큰

    Raises:
        HTTPException: 인증 실패 시
    """
    auth_service = AuthService(db)
    return await auth_service.login(login_data.email, login_data.password)


@router.post("/logout", response_model=LogoutResponse)
async def logout(token: str = Depends(security), db: Session = Depends(get_db)):
    """사용자 로그아웃

    Args:
        token: Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        로그아웃 성공 메시지
    """
    auth_service = AuthService(db)
    await auth_service.logout(token.credentials)
    return LogoutResponse(message="Successfully logged out")


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    """토큰 갱신

    Args:
        refresh_data: 리프레시 토큰
        db: 데이터베이스 세션

    Returns:
        새로운 액세스 토큰과 리프레시 토큰

    Raises:
        HTTPException: 토큰이 유효하지 않을 시
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.get("/me")
async def get_current_user_profile(token: str = Depends(security), db: Session = Depends(get_db)):
    """현재 인증된 사용자 프로필 조회

    Args:
        token: Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        사용자 프로필 정보
    """
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token.credentials)