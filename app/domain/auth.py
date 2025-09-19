from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SessionData(BaseModel):
    """Redis 세션 데이터 모델"""
    user_id: int
    access_token: str
    refresh_token: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드 모델"""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: Optional[str] = "access"
    jti: Optional[str] = None  # JWT ID for token tracking


class AuthCredentials(BaseModel):
    """인증 자격증명 모델"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """인증 응답 모델"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    issued_at: datetime


class UserSession(BaseModel):
    """사용자 세션 모델"""
    session_id: str
    user_id: int
    access_token: str
    refresh_token: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True
    device_info: Optional[dict] = None


class TokenBlacklist(BaseModel):
    """토큰 블랙리스트 모델"""
    token: str
    user_id: int
    blacklisted_at: datetime
    reason: str = "logout"
    expires_at: datetime