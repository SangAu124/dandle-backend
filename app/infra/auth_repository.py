import redis.asyncio as redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from app.core.config import settings
from app.domain.auth import SessionData, TokenBlacklist, UserSession


class AuthRepository:
    """인증 관련 Redis 저장소"""

    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    async def store_session(self, user_id: int, access_token: str, refresh_token: str,
                           ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Redis에 사용자 세션 저장

        Args:
            user_id: 사용자 ID
            access_token: 액세스 토큰
            refresh_token: 리프레시 토큰
            ip_address: 클라이언트 IP 주소
            user_agent: 클라이언트 User-Agent

        Returns:
            세션 ID
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

        session_data = SessionData(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 사용자별 세션 키
        session_key = f"session:user:{user_id}:{session_id}"
        user_sessions_key = f"user_sessions:{user_id}"

        # Redis 파이프라인으로 원자적 저장
        pipe = self.redis_client.pipeline()

        # 세션 데이터 저장
        pipe.setex(
            session_key,
            timedelta(minutes=settings.jwt_expire_minutes),
            session_data.model_dump_json()
        )

        # 사용자의 활성 세션 목록에 추가
        pipe.sadd(user_sessions_key, session_id)
        pipe.expire(user_sessions_key, timedelta(minutes=settings.jwt_expire_minutes))

        # 액세스 토큰 매핑 저장 (빠른 검증용)
        token_key = f"token:{access_token}"
        pipe.setex(
            token_key,
            timedelta(minutes=settings.jwt_expire_minutes),
            json.dumps({"user_id": user_id, "session_id": session_id})
        )

        # 리프레시 토큰 매핑 저장 (빠른 세션 업데이트용)
        refresh_token_key = f"refresh_token:{refresh_token}"
        pipe.setex(
            refresh_token_key,
            timedelta(days=30),  # 리프레시 토큰 만료 시간과 동일
            json.dumps({"user_id": user_id, "session_id": session_id})
        )

        await pipe.execute()
        return session_id

    async def get_session(self, user_id: int, session_id: str) -> Optional[SessionData]:
        """사용자 세션 조회

        Args:
            user_id: 사용자 ID
            session_id: 세션 ID

        Returns:
            세션 데이터 또는 None
        """
        session_key = f"session:user:{user_id}:{session_id}"
        session_data = await self.redis_client.get(session_key)

        if session_data:
            return SessionData.model_validate_json(session_data)
        return None

    async def get_session_by_token(self, access_token: str) -> Optional[SessionData]:
        """액세스 토큰으로 세션 조회

        Args:
            access_token: 액세스 토큰

        Returns:
            세션 데이터 또는 None
        """
        token_key = f"token:{access_token}"
        token_data = await self.redis_client.get(token_key)

        if token_data:
            token_info = json.loads(token_data)
            return await self.get_session(token_info["user_id"], token_info["session_id"])
        return None

    async def invalidate_session(self, user_id: int, access_token: str) -> None:
        """세션 무효화 (로그아웃)

        Args:
            user_id: 사용자 ID
            access_token: 액세스 토큰
        """
        # 토큰으로 세션 정보 찾기
        token_key = f"token:{access_token}"
        token_data = await self.redis_client.get(token_key)

        if token_data:
            token_info = json.loads(token_data)
            session_id = token_info["session_id"]

            # 세션 데이터 조회하여 리프레시 토큰 추출
            session = await self.get_session(user_id, session_id)

            # Redis 파이프라인으로 원자적 삭제
            pipe = self.redis_client.pipeline()

            # 세션 데이터 삭제
            session_key = f"session:user:{user_id}:{session_id}"
            pipe.delete(session_key)

            # 토큰 매핑 삭제
            pipe.delete(token_key)

            # 리프레시 토큰 매핑 삭제 (세션이 존재하는 경우)
            if session:
                refresh_token_key = f"refresh_token:{session.refresh_token}"
                pipe.delete(refresh_token_key)

            # 사용자 세션 목록에서 제거
            user_sessions_key = f"user_sessions:{user_id}"
            pipe.srem(user_sessions_key, session_id)

            # 토큰 블랙리스트에 추가 (파이프라인 내에서 원자적 처리)
            blacklist_key = f"blacklist:{access_token}"
            blacklist_data = TokenBlacklist(
                token=access_token,
                user_id=user_id,
                blacklisted_at=datetime.utcnow(),
                reason="logout",
                expires_at=datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
            )
            pipe.setex(
                blacklist_key,
                timedelta(minutes=settings.jwt_expire_minutes),
                blacklist_data.model_dump_json()
            )

            await pipe.execute()

    async def _invalidate_session_with_refresh_token(self, user_id: int, access_token: str, refresh_token: str) -> None:
        """세션 무효화 (리프레시 토큰 매핑 포함)

        Args:
            user_id: 사용자 ID
            access_token: 액세스 토큰
            refresh_token: 리프레시 토큰
        """
        # 토큰으로 세션 정보 찾기
        token_key = f"token:{access_token}"
        token_data = await self.redis_client.get(token_key)

        if token_data:
            token_info = json.loads(token_data)
            session_id = token_info["session_id"]

            # Redis 파이프라인으로 원자적 삭제
            pipe = self.redis_client.pipeline()

            # 세션 데이터 삭제
            session_key = f"session:user:{user_id}:{session_id}"
            pipe.delete(session_key)

            # 토큰 매핑 삭제
            pipe.delete(token_key)

            # 리프레시 토큰 매핑 삭제
            refresh_token_key = f"refresh_token:{refresh_token}"
            pipe.delete(refresh_token_key)

            # 사용자 세션 목록에서 제거
            user_sessions_key = f"user_sessions:{user_id}"
            pipe.srem(user_sessions_key, session_id)

            # 토큰 블랙리스트에 추가 (파이프라인 내에서 원자적 처리)
            blacklist_key = f"blacklist:{access_token}"
            blacklist_data = TokenBlacklist(
                token=access_token,
                user_id=user_id,
                blacklisted_at=datetime.utcnow(),
                reason="logout",
                expires_at=datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
            )
            pipe.setex(
                blacklist_key,
                timedelta(minutes=settings.jwt_expire_minutes),
                blacklist_data.model_dump_json()
            )

            await pipe.execute()

    async def invalidate_all_sessions(self, user_id: int) -> None:
        """사용자의 모든 세션 무효화

        Args:
            user_id: 사용자 ID
        """
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis_client.smembers(user_sessions_key)

        if session_ids:
            pipe = self.redis_client.pipeline()

            for session_id in session_ids:
                session_key = f"session:user:{user_id}:{session_id}"
                pipe.delete(session_key)

            # 사용자 세션 목록 삭제
            pipe.delete(user_sessions_key)

            await pipe.execute()

    async def update_session(self, user_id: int, old_refresh_token: str,
                           access_token: str, refresh_token: str) -> Optional[str]:
        """세션 업데이트 (토큰 갱신)

        Args:
            user_id: 사용자 ID
            old_refresh_token: 기존 리프레시 토큰
            access_token: 새 액세스 토큰
            refresh_token: 새 리프레시 토큰

        Returns:
            새 세션 ID 또는 None
        """
        # 기존 세션 찾기 (리프레시 토큰 매핑으로 O(1) 조회)
        refresh_token_key = f"refresh_token:{old_refresh_token}"
        refresh_token_data = await self.redis_client.get(refresh_token_key)

        if refresh_token_data:
            token_info = json.loads(refresh_token_data)
            session_id = token_info["session_id"]

            # 기존 세션 데이터 조회
            session = await self.get_session(user_id, session_id)
            if session:
                # 기존 세션 삭제 (리프레시 토큰 매핑도 삭제됨)
                await self._invalidate_session_with_refresh_token(user_id, session.access_token, old_refresh_token)

                # 새 세션 생성
                return await self.store_session(
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent
                )

        return None

    async def is_token_blacklisted(self, access_token: str) -> bool:
        """토큰 블랙리스트 확인

        Args:
            access_token: 액세스 토큰

        Returns:
            블랙리스트 여부
        """
        blacklist_key = f"blacklist:{access_token}"
        return await self.redis_client.exists(blacklist_key) > 0

    async def add_to_blacklist(self, access_token: str, user_id: int, reason: str = "logout") -> None:
        """토큰을 블랙리스트에 추가

        Args:
            access_token: 액세스 토큰
            user_id: 사용자 ID
            reason: 블랙리스트 추가 이유
        """
        blacklist_key = f"blacklist:{access_token}"
        blacklist_data = TokenBlacklist(
            token=access_token,
            user_id=user_id,
            blacklisted_at=datetime.utcnow(),
            reason=reason,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        )

        await self.redis_client.setex(
            blacklist_key,
            timedelta(minutes=settings.jwt_expire_minutes),
            blacklist_data.model_dump_json()
        )

    async def get_user_sessions(self, user_id: int) -> List[SessionData]:
        """사용자의 모든 활성 세션 조회

        Args:
            user_id: 사용자 ID

        Returns:
            활성 세션 목록
        """
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis_client.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session = await self.get_session(user_id, session_id)
            if session:
                sessions.append(session)

        return sessions

    async def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리

        Returns:
            정리된 세션 수
        """
        # 이 메서드는 주기적으로 실행하여 만료된 세션을 정리
        # Redis TTL을 사용하므로 자동으로 만료되지만, 명시적 정리도 가능
        current_time = datetime.utcnow()
        cleaned_count = 0

        # 패턴 매칭으로 모든 세션 키 찾기
        pattern = "session:user:*"
        async for key in self.redis_client.scan_iter(match=pattern):
            session_data = await self.redis_client.get(key)
            if session_data:
                session = SessionData.model_validate_json(session_data)
                if session.expires_at < current_time:
                    await self.redis_client.delete(key)
                    cleaned_count += 1

        return cleaned_count

    async def close(self) -> None:
        """Redis 연결 종료"""
        await self.redis_client.close()