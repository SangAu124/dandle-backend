import pytest
from sqlalchemy.orm import Session
from app.infra.group_repository import GroupRepository
from app.domain.group import Group


class TestGroupRepository:
    """GroupRepository 테스트"""

    def test_create(self, db_session: Session):
        """그룹 생성 테스트"""
        repo = GroupRepository(db_session)
        group_data = {
            "name": "Test Group",
            "description": "Test Description",
            "group_type": "class",
            "invite_code": "TEST123",
            "created_by_id": 1,
            "is_public": False,
            "max_members": 50
        }

        group = repo.create(group_data)

        assert group.id is not None
        assert group.name == "Test Group"
        assert group.description == "Test Description"
        assert group.group_type == "class"
        assert group.invite_code == "TEST123"
        assert group.created_by_id == 1
        assert group.is_public is False
        assert group.max_members == 50
        assert group.is_active is True

    def test_get_by_id_existing(self, db_session: Session):
        """ID로 기존 그룹 조회 테스트"""
        repo = GroupRepository(db_session)

        # 먼저 그룹 생성
        group = repo.create({
            "name": "Test Group",
            "group_type": "class",
            "invite_code": "TEST123",
            "created_by_id": 1
        })
        db_session.commit()

        # ID로 조회
        found_group = repo.get_by_id(group.id)

        assert found_group is not None
        assert found_group.id == group.id
        assert found_group.name == "Test Group"

    def test_get_by_id_non_existing(self, db_session: Session):
        """ID로 존재하지 않는 그룹 조회 테스트"""
        repo = GroupRepository(db_session)

        group = repo.get_by_id(999)

        assert group is None

    def test_get_by_invite_code_existing(self, db_session: Session):
        """초대 코드로 기존 그룹 조회 테스트"""
        repo = GroupRepository(db_session)

        # 활성 그룹 생성
        group = repo.create({
            "name": "Test Group",
            "group_type": "class",
            "invite_code": "ACTIVE123",
            "created_by_id": 1,
            "is_active": True
        })
        db_session.commit()

        # 초대 코드로 조회
        found_group = repo.get_by_invite_code("ACTIVE123")

        assert found_group is not None
        assert found_group.id == group.id
        assert found_group.invite_code == "ACTIVE123"

    def test_get_by_invite_code_inactive_group(self, db_session: Session):
        """비활성 그룹의 초대 코드로 조회 테스트 (조회되지 않아야 함)"""
        repo = GroupRepository(db_session)

        # 비활성 그룹 생성
        group = repo.create({
            "name": "Inactive Group",
            "group_type": "class",
            "invite_code": "INACTIVE123",
            "created_by_id": 1,
            "is_active": False
        })
        db_session.commit()

        # 초대 코드로 조회 (비활성이므로 조회되지 않아야 함)
        found_group = repo.get_by_invite_code("INACTIVE123")

        assert found_group is None

    def test_get_by_invite_code_non_existing(self, db_session: Session):
        """존재하지 않는 초대 코드로 그룹 조회 테스트"""
        repo = GroupRepository(db_session)

        group = repo.get_by_invite_code("NONEXISTENT")

        assert group is None