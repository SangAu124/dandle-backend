import pytest
from sqlalchemy.orm import Session
from app.services.group_service import GroupService
from app.services.user_service import UserService


def test_create_group(db_session: Session, sample_user_data, sample_group_data):
    """그룹 생성 테스트"""
    # 먼저 사용자 생성
    user_service = UserService(db_session)
    user = user_service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 그룹 생성
    group_service = GroupService(db_session)
    group = group_service.create_group(
        name=sample_group_data["name"],
        created_by_id=user.id,
        group_type=sample_group_data["group_type"],
        description=sample_group_data["description"],
        is_public=sample_group_data["is_public"],
        max_members=sample_group_data["max_members"]
    )

    assert group.name == sample_group_data["name"]
    assert group.group_type == sample_group_data["group_type"]
    assert group.created_by_id == user.id
    assert group.is_active is True
    assert len(group.invite_code) == 8  # 초대 코드가 생성되었는지 확인


def test_add_member_to_group(db_session: Session, sample_user_data, sample_group_data):
    """그룹에 멤버 추가 테스트"""
    # 사용자들 생성
    user_service = UserService(db_session)
    owner = user_service.create_user(
        email="owner@example.com",
        username="owner",
        password="password123"
    )
    member = user_service.create_user(
        email="member@example.com",
        username="member",
        password="password123"
    )

    # 그룹 생성
    group_service = GroupService(db_session)
    group = group_service.create_group(
        name=sample_group_data["name"],
        created_by_id=owner.id,
        group_type=sample_group_data["group_type"]
    )

    # 멤버 추가
    success = group_service.add_member(group.id, member.id, "member")
    assert success is True

    # 그룹 멤버 목록 확인
    members = group_service.get_group_members(group.id)
    assert len(members) == 2  # 소유자 + 새 멤버

    # 멤버 역할 확인
    member_roles = {m.user_id: m.role for m in members}
    assert member_roles[owner.id] == "admin"
    assert member_roles[member.id] == "member"


def test_get_group_by_invite_code(db_session: Session, sample_user_data, sample_group_data):
    """초대 코드로 그룹 조회 테스트"""
    # 사용자 생성
    user_service = UserService(db_session)
    user = user_service.create_user(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        password=sample_user_data["password"]
    )

    # 그룹 생성
    group_service = GroupService(db_session)
    group = group_service.create_group(
        name=sample_group_data["name"],
        created_by_id=user.id,
        group_type=sample_group_data["group_type"]
    )

    # 초대 코드로 그룹 조회
    found_group = group_service.get_group_by_invite_code(group.invite_code)

    assert found_group is not None
    assert found_group.id == group.id
    assert found_group.name == sample_group_data["name"]


def test_max_members_limit(db_session: Session, sample_user_data):
    """최대 멤버 수 제한 테스트"""
    # 사용자 생성
    user_service = UserService(db_session)
    owner = user_service.create_user(
        email="owner@example.com",
        username="owner",
        password="password123"
    )

    # 최대 멤버 2명인 그룹 생성
    group_service = GroupService(db_session)
    group = group_service.create_group(
        name="Small Group",
        created_by_id=owner.id,
        group_type="class",
        max_members=2
    )

    # 추가 멤버 생성
    member1 = user_service.create_user(
        email="member1@example.com",
        username="member1",
        password="password123"
    )
    member2 = user_service.create_user(
        email="member2@example.com",
        username="member2",
        password="password123"
    )

    # 첫 번째 멤버 추가 (성공해야 함)
    success1 = group_service.add_member(group.id, member1.id)
    assert success1 is True

    # 두 번째 멤버 추가 (실패해야 함 - 이미 최대 멤버 수에 도달)
    success2 = group_service.add_member(group.id, member2.id)
    assert success2 is False