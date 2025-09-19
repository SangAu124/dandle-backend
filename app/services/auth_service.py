from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.domain.user import User
from app.domain.auth import AuthResponse, SessionData
from app.infra.user_repository import UserRepository
from app.infra.auth_repository import AuthRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token
)
from app.core.config import settings


class AuthService:
    """인증 서비스"""

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.auth_repository = AuthRepository()

    async def login(self, email: str, password: str,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> Dict[str, Any]:
        """사용자 로그인

        Args:
            email: 사용자 이메일
            password: 비밀번호
            ip_address: 클라이언트 IP 주소
            user_agent: 클라이언트 User-Agent

        Returns:
            인증 토큰과 사용자 정보

        Raises:
            HTTPException: 인증 실패 시
        """
        # 사용자 확인
        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # 비밀번호 검증
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # 계정 활성화 상태 확인
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(user.id)

        # Redis에 세션 저장
        session_id = await self.auth_repository.store_session(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_minutes * 60,
            "user_id": user.id,
            "session_id": session_id
        }

    async def logout(self, access_token: str) -> None:
        """사용자 로그아웃

        Args:
            access_token: 액세스 토큰

        Raises:
            HTTPException: 토큰이 유효하지 않을 시
        """
        # 토큰 블랙리스트 확인
        if await self.auth_repository.is_token_blacklisted(access_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is already invalidated"
            )

        # 토큰 검증
        try:
            payload = verify_token(access_token)
            user_id = int(payload.get("sub"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Redis에서 세션 제거
        await self.auth_repository.invalidate_session(user_id, access_token)

    async def logout_all_sessions(self, user_id: int) -> None:
        """사용자의 모든 세션 로그아웃

        Args:
            user_id: 사용자 ID
        """
        await self.auth_repository.invalidate_all_sessions(user_id)

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """토큰 갱신

        Args:
            refresh_token: 리프레시 토큰

        Returns:
            새로운 액세스 토큰과 리프레시 토큰

        Raises:
            HTTPException: 토큰이 유효하지 않을 시
        """
        # 리프레시 토큰 검증
        try:
            payload = verify_refresh_token(refresh_token)
            user_id = int(payload.get("sub"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # 사용자 확인
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # 새 토큰 생성
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(user.id)

        # Redis 세션 업데이트
        session_id = await self.auth_repository.update_session(
            user_id=user.id,
            old_refresh_token=refresh_token,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired"
            )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_minutes * 60,
            "user_id": user.id,
            "session_id": session_id
        }

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """현재 인증된 사용자 정보 조회

        Args:
            access_token: 액세스 토큰

        Returns:
            사용자 정보

        Raises:
            HTTPException: 토큰이 유효하지 않을 시
        """
        # 토큰 블랙리스트 확인
        if await self.auth_repository.is_token_blacklisted(access_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalidated"
            )

        # 토큰 검증
        try:
            payload = verify_token(access_token)
            user_id = int(payload.get("sub"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # 세션 확인
        session = await self.auth_repository.get_session_by_token(access_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired"
            )

        # 사용자 정보 조회
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "profile_image_url": user.profile_image_url,
            "created_at": user.created_at,
            "session_info": {
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent
            }
        }

    async def validate_token(self, access_token: str) -> bool:
        """토큰 유효성 검사

        Args:
            access_token: 액세스 토큰

        Returns:
            토큰 유효성 여부
        """
        try:
            # 블랙리스트 확인
            if await self.auth_repository.is_token_blacklisted(access_token):
                return False

            # 토큰 검증
            payload = verify_token(access_token)
            user_id = int(payload.get("sub"))

            # 세션 확인
            session = await self.auth_repository.get_session_by_token(access_token)
            if not session:
                return False

            # 사용자 활성 상태 확인
            user = self.user_repository.get_by_id(user_id)
            return user is not None and user.is_active

        except Exception:
            return False

    async def get_user_sessions(self, user_id: int) -> list:
        """사용자의 모든 활성 세션 조회

        Args:
            user_id: 사용자 ID

        Returns:
            활성 세션 목록
        """
        sessions = await self.auth_repository.get_user_sessions(user_id)
        return [
            {
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "is_current": False  # 현재 세션 여부는 클라이언트에서 판단
            }
            for session in sessions
        ]

    async def revoke_session(self, user_id: int, access_token: str) -> None:
        """특정 세션 취소

        Args:
            user_id: 사용자 ID
            access_token: 취소할 세션의 액세스 토큰
        """
        await self.auth_repository.invalidate_session(user_id, access_token)

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """비밀번호 변경 (모든 세션 무효화)

        Args:
            user_id: 사용자 ID
            current_password: 현재 비밀번호
            new_password: 새 비밀번호

        Raises:
            HTTPException: 현재 비밀번호가 틀릴 시
        """
        # 사용자 확인
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 현재 비밀번호 확인
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # 비밀번호 업데이트
        from app.core.security import get_password_hash
        hashed_new_password = get_password_hash(new_password)
        self.user_repository.update(user_id, {"hashed_password": hashed_new_password})

        # 모든 세션 무효화 (보안상 이유)
        await self.logout_all_sessions(user_id)

    async def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리

        Returns:
            정리된 세션 수
        """
        return await self.auth_repository.cleanup_expired_sessions()

    async def close(self) -> None:
        """서비스 종료 시 리소스 정리"""
        await self.auth_repository.close()