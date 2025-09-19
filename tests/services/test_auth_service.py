import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.domain.user import User
from app.domain.auth import SessionData


class TestAuthService:
    """AuthService 테스트 클래스"""

    @pytest.fixture
    def mock_db(self):
        """Mock 데이터베이스 세션"""
        return Mock()

    @pytest.fixture
    def mock_user(self):
        """Mock 사용자 객체"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.hashed_password = "hashed_password"
        user.is_active = True
        user.is_verified = True
        user.role = "user"
        user.profile_image_url = None
        user.created_at = datetime.utcnow()
        return user

    @pytest.fixture
    def auth_service(self, mock_db):
        """AuthService 인스턴스"""
        service = AuthService(mock_db)
        service.auth_repository = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user):
        """로그인 성공 테스트"""
        # Mock repository 설정
        auth_service.user_repository.get_by_email = Mock(return_value=mock_user)
        auth_service.auth_repository.store_session = AsyncMock(return_value="session_123")

        # Mock 비밀번호 검증 및 토큰 생성
        with patch('app.services.auth_service.verify_password', return_value=True), \
             patch('app.services.auth_service.create_access_token', return_value="access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"):

            result = await auth_service.login("test@example.com", "password")

        # 검증
        assert result["access_token"] == "access_token"
        assert result["refresh_token"] == "refresh_token"
        assert result["token_type"] == "bearer"
        assert result["user_id"] == 1
        assert result["session_id"] == "session_123"
        auth_service.auth_repository.store_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service):
        """존재하지 않는 사용자로 로그인 시도 테스트"""
        auth_service.user_repository.get_by_email = Mock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login("nonexistent@example.com", "password")

        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_service, mock_user):
        """잘못된 비밀번호로 로그인 시도 테스트"""
        auth_service.user_repository.get_by_email = Mock(return_value=mock_user)

        with patch('app.services.auth_service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.login("test@example.com", "wrong_password")

        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, auth_service, mock_user):
        """비활성화된 사용자 로그인 시도 테스트"""
        mock_user.is_active = False
        auth_service.user_repository.get_by_email = Mock(return_value=mock_user)

        with patch('app.services.auth_service.verify_password', return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.login("test@example.com", "password")

        assert exc_info.value.status_code == 403
        assert "User account is disabled" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service):
        """로그아웃 성공 테스트"""
        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=False)
        auth_service.auth_repository.invalidate_session = AsyncMock()

        with patch('app.services.auth_service.verify_token', return_value={"sub": "1"}):
            await auth_service.logout("valid_token")

        auth_service.auth_repository.invalidate_session.assert_called_once_with(1, "valid_token")

    @pytest.mark.asyncio
    async def test_logout_blacklisted_token(self, auth_service):
        """블랙리스트된 토큰으로 로그아웃 시도 테스트"""
        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=True)

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.logout("blacklisted_token")

        assert exc_info.value.status_code == 401
        assert "Token is already invalidated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, auth_service):
        """유효하지 않은 토큰으로 로그아웃 시도 테스트"""
        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=False)

        with patch('app.services.auth_service.verify_token', side_effect=Exception("Invalid token")):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.logout("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, mock_user):
        """토큰 갱신 성공 테스트"""
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)
        auth_service.auth_repository.update_session = AsyncMock(return_value="new_session_123")

        with patch('app.services.auth_service.verify_refresh_token', return_value={"sub": "1"}), \
             patch('app.services.auth_service.create_access_token', return_value="new_access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="new_refresh_token"):

            result = await auth_service.refresh_token("refresh_token")

        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"
        assert result["user_id"] == 1
        assert result["session_id"] == "new_session_123"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(self, auth_service):
        """유효하지 않은 리프레시 토큰으로 갱신 시도 테스트"""
        with patch('app.services.auth_service.verify_refresh_token', side_effect=Exception("Invalid token")):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.refresh_token("invalid_refresh_token")

        assert exc_info.value.status_code == 401
        assert "Invalid refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(self, auth_service):
        """사용자를 찾을 수 없을 때 토큰 갱신 시도 테스트"""
        auth_service.user_repository.get_by_id = Mock(return_value=None)

        with patch('app.services.auth_service.verify_refresh_token', return_value={"sub": "999"}):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.refresh_token("refresh_token")

        assert exc_info.value.status_code == 401
        assert "User not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_session_not_found(self, auth_service, mock_user):
        """세션을 찾을 수 없을 때 토큰 갱신 시도 테스트"""
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)
        auth_service.auth_repository.update_session = AsyncMock(return_value=None)

        with patch('app.services.auth_service.verify_refresh_token', return_value={"sub": "1"}), \
             patch('app.services.auth_service.create_access_token', return_value="new_access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="new_refresh_token"):

            with pytest.raises(HTTPException) as exc_info:
                await auth_service.refresh_token("refresh_token")

        assert exc_info.value.status_code == 401
        assert "Session not found or expired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, auth_service, mock_user):
        """현재 사용자 정보 조회 성공 테스트"""
        mock_session = SessionData(
            user_id=1,
            access_token="access_token",
            refresh_token="refresh_token",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            ip_address="127.0.0.1",
            user_agent="test-agent"
        )

        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=False)
        auth_service.auth_repository.get_session_by_token = AsyncMock(return_value=mock_session)
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)

        with patch('app.services.auth_service.verify_token', return_value={"sub": "1"}):
            result = await auth_service.get_current_user("access_token")

        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["username"] == "testuser"
        assert result["role"] == "user"
        assert "session_info" in result

    @pytest.mark.asyncio
    async def test_get_current_user_blacklisted_token(self, auth_service):
        """블랙리스트된 토큰으로 현재 사용자 조회 시도 테스트"""
        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=True)

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user("blacklisted_token")

        assert exc_info.value.status_code == 401
        assert "Token is invalidated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_validate_token_success(self, auth_service, mock_user):
        """토큰 유효성 검사 성공 테스트"""
        mock_session = SessionData(
            user_id=1,
            access_token="access_token",
            refresh_token="refresh_token",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=False)
        auth_service.auth_repository.get_session_by_token = AsyncMock(return_value=mock_session)
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)

        with patch('app.services.auth_service.verify_token', return_value={"sub": "1"}):
            result = await auth_service.validate_token("valid_token")

        assert result is True

    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, auth_service):
        """토큰 유효성 검사 실패 테스트"""
        auth_service.auth_repository.is_token_blacklisted = AsyncMock(return_value=False)

        with patch('app.services.auth_service.verify_token', side_effect=Exception("Invalid token")):
            result = await auth_service.validate_token("invalid_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_logout_all_sessions(self, auth_service):
        """모든 세션 로그아웃 테스트"""
        auth_service.auth_repository.invalidate_all_sessions = AsyncMock()

        await auth_service.logout_all_sessions(1)

        auth_service.auth_repository.invalidate_all_sessions.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, auth_service):
        """사용자 세션 목록 조회 테스트"""
        mock_sessions = [
            SessionData(
                user_id=1,
                access_token="token1",
                refresh_token="refresh1",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=1),
                ip_address="127.0.0.1",
                user_agent="agent1"
            ),
            SessionData(
                user_id=1,
                access_token="token2",
                refresh_token="refresh2",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=1),
                ip_address="192.168.1.1",
                user_agent="agent2"
            )
        ]

        auth_service.auth_repository.get_user_sessions = AsyncMock(return_value=mock_sessions)

        result = await auth_service.get_user_sessions(1)

        assert len(result) == 2
        assert result[0]["ip_address"] == "127.0.0.1"
        assert result[1]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, mock_user):
        """비밀번호 변경 성공 테스트"""
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)
        auth_service.user_repository.update = Mock()
        auth_service.auth_repository.invalidate_all_sessions = AsyncMock()

        with patch('app.services.auth_service.verify_password', return_value=True), \
             patch('app.core.security.get_password_hash', return_value="new_hashed_password"):

            await auth_service.change_password(1, "current_password", "new_password")

        auth_service.user_repository.update.assert_called_once()
        auth_service.auth_repository.invalidate_all_sessions.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(self, auth_service, mock_user):
        """잘못된 현재 비밀번호로 변경 시도 테스트"""
        auth_service.user_repository.get_by_id = Mock(return_value=mock_user)

        with patch('app.services.auth_service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.change_password(1, "wrong_password", "new_password")

        assert exc_info.value.status_code == 400
        assert "Incorrect current password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, auth_service):
        """만료된 세션 정리 테스트"""
        auth_service.auth_repository.cleanup_expired_sessions = AsyncMock(return_value=5)

        result = await auth_service.cleanup_expired_sessions()

        assert result == 5
        auth_service.auth_repository.cleanup_expired_sessions.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_close(self, auth_service):
        """서비스 종료 테스트"""
        auth_service.auth_repository.close = AsyncMock()

        await auth_service.close()

        auth_service.auth_repository.close.assert_called_once()