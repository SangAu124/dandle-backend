import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, AsyncMock, patch
from jose import jwt

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    create_refresh_token,
    verify_refresh_token,
    PermissionChecker,
    require_admin,
    require_user
)
from app.core.config import settings
from app.domain.user import User


class TestPasswordFunctions:
    """비밀번호 관련 함수 테스트"""

    def test_get_password_hash(self):
        """비밀번호 해싱 테스트"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_password(self):
        """비밀번호 검증 테스트"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        # 올바른 비밀번호
        assert verify_password(password, hashed) is True

        # 잘못된 비밀번호
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """JWT 토큰 관련 함수 테스트"""

    def test_create_access_token_default_expiry(self):
        """기본 만료 시간으로 액세스 토큰 생성"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # 토큰 디코딩 테스트
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """커스텀 만료 시간으로 액세스 토큰 생성"""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "123"
        assert "exp" in payload

        # 간단히 만료 시간이 미래인지만 확인
        exp_time = datetime.fromtimestamp(payload["exp"])
        assert exp_time > datetime.utcnow()

    def test_verify_token_valid(self):
        """유효한 토큰 검증"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"

    def test_verify_token_invalid(self):
        """무효한 토큰 검증"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_token")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_verify_token_expired(self):
        """만료된 토큰 검증"""
        data = {"sub": "123"}
        expires_delta = timedelta(seconds=-1)  # 이미 만료된 토큰
        token = create_access_token(data, expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshTokens:
    """리프레시 토큰 관련 함수 테스트"""

    def test_create_refresh_token(self):
        """리프레시 토큰 생성"""
        user_id = 123
        token = create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"

    def test_verify_refresh_token_valid(self):
        """유효한 리프레시 토큰 검증"""
        user_id = 123
        token = create_refresh_token(user_id)

        payload = verify_refresh_token(token)
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"

    def test_verify_refresh_token_wrong_type(self):
        """잘못된 타입의 토큰으로 리프레시 토큰 검증"""
        data = {"sub": "123", "type": "access"}  # access 타입
        token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token type" in str(exc_info.value.detail)

    def test_verify_refresh_token_no_type(self):
        """타입이 없는 토큰으로 리프레시 토큰 검증"""
        data = {"sub": "123"}  # type 필드 없음
        token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestUserAuthentication:
    """사용자 인증 관련 함수 테스트"""

    async def test_get_current_user_valid(self):
        """유효한 토큰으로 현재 사용자 조회"""
        # Mock 설정
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = create_access_token({"sub": "1"})

        mock_db = Mock()
        mock_user_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.is_active = True

        mock_user_repo.get_by_id.return_value = mock_user

        # UserRepository를 mock으로 패치
        with patch('app.core.security.UserRepository', return_value=mock_user_repo):
            user = await get_current_user(mock_credentials, mock_db)

        assert user == mock_user
        mock_user_repo.get_by_id.assert_called_once_with(1)

    async def test_get_current_user_invalid_token(self):
        """무효한 토큰으로 현재 사용자 조회"""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "invalid_token"
        mock_db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_no_sub(self):
        """sub가 없는 토큰으로 현재 사용자 조회"""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = create_access_token({"username": "test"})  # sub 없음
        mock_db = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    async def test_get_current_user_user_not_found(self):
        """존재하지 않는 사용자로 현재 사용자 조회"""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = create_access_token({"sub": "999"})

        mock_db = Mock()
        mock_user_repo = Mock()
        mock_user_repo.get_by_id.return_value = None  # 사용자 없음

        with patch('app.core.security.UserRepository', return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in str(exc_info.value.detail)

    async def test_get_current_user_inactive_user(self):
        """비활성 사용자로 현재 사용자 조회"""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = create_access_token({"sub": "1"})

        mock_db = Mock()
        mock_user_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.is_active = False  # 비활성 사용자

        mock_user_repo.get_by_id.return_value = mock_user

        with patch('app.core.security.UserRepository', return_value=mock_user_repo):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "User account is disabled" in str(exc_info.value.detail)

    async def test_get_current_active_user_active(self):
        """활성 사용자로 현재 활성 사용자 조회"""
        mock_user = Mock(spec=User)
        mock_user.is_active = True

        result = await get_current_active_user(mock_user)
        assert result == mock_user

    async def test_get_current_active_user_inactive(self):
        """비활성 사용자로 현재 활성 사용자 조회"""
        mock_user = Mock(spec=User)
        mock_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(mock_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Inactive user" in str(exc_info.value.detail)


class TestPermissionChecker:
    """권한 검사 클래스 테스트"""

    def test_permission_checker_init(self):
        """PermissionChecker 초기화"""
        checker = PermissionChecker("admin")
        assert checker.required_permission == "admin"

    def test_permission_checker_call(self):
        """PermissionChecker 호출 (현재는 단순히 사용자 반환)"""
        checker = PermissionChecker("admin")
        mock_user = Mock(spec=User)

        result = checker(mock_user)
        assert result == mock_user

    def test_require_admin_instance(self):
        """require_admin 인스턴스 테스트"""
        assert isinstance(require_admin, PermissionChecker)
        assert require_admin.required_permission == "admin"

    def test_require_user_instance(self):
        """require_user 인스턴스 테스트"""
        assert isinstance(require_user, PermissionChecker)
        assert require_user.required_permission == "user"