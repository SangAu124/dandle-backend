import pytest
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.domain.user import User


def test_create_user(db_session: Session, sample_user_data):
    """사용자 생성 테스트"""
    service = UserService(db_session)

    user = service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"],
        full_name=sample_user_data["full_name"]
    )

    assert user.email == sample_user_data["email"]
    assert user.username == sample_user_data["username"]
    assert user.full_name == sample_user_data["full_name"]
    assert user.is_active is True
    assert user.is_verified is False
    assert user.hashed_password != sample_user_data["password"]  # 비밀번호가 해싱되었는지 확인


def test_create_user_duplicate_email(db_session: Session, sample_user_data):
    """중복 이메일로 사용자 생성 시 에러 테스트"""
    service = UserService(db_session)

    # 첫 번째 사용자 생성
    service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 같은 이메일로 두 번째 사용자 생성 시도
    with pytest.raises(ValueError, match="Email already registered"):
        service.create_user(
            email=sample_user_data["email"],
            username="different_username",
            password=sample_user_data["password"]
        )


def test_get_user_by_email(db_session: Session, sample_user_data):
    """이메일로 사용자 조회 테스트"""
    service = UserService(db_session)

    # 사용자 생성
    created_user = service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 이메일로 조회
    found_user = service.get_user_by_email(sample_user_data["email"])

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == sample_user_data["email"]


def test_verify_password(db_session: Session, sample_user_data):
    """비밀번호 검증 테스트"""
    service = UserService(db_session)

    user = service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 올바른 비밀번호 검증
    assert service.verify_password(sample_user_data["password"], user.hashed_password) is True

    # 틀린 비밀번호 검증
    assert service.verify_password("wrong_password", user.hashed_password) is False


def test_update_user(db_session: Session, sample_user_data):
    """사용자 정보 수정 테스트"""
    service = UserService(db_session)

    user = service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 사용자 정보 수정
    update_data = {"full_name": "Updated Name"}
    updated_user = service.update_user(user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == sample_user_data["email"]  # 다른 필드는 변경되지 않음