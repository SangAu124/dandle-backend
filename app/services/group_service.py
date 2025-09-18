from typing import Optional, List
import secrets
import string
from sqlalchemy.orm import Session
from app.domain.group import Group, GroupMembership
from app.infra.group_repository import GroupRepository


class GroupService:
    def __init__(self, db: Session):
        self.repository = GroupRepository(db)

    def create_group(
        self,
        name: str,
        created_by_id: int,
        group_type: str,
        description: Optional[str] = None,
        is_public: bool = False,
        max_members: int = 100
    ) -> Group:
        """새로운 그룹 생성"""
        # 초대 코드 생성
        invite_code = self._generate_invite_code()

        # 중복 검사
        while self.repository.get_by_invite_code(invite_code):
            invite_code = self._generate_invite_code()

        group_data = {
            "name": name,
            "description": description,
            "group_type": group_type,
            "invite_code": invite_code,
            "is_public": is_public,
            "max_members": max_members,
            "created_by_id": created_by_id,
            "is_active": True
        }

        group = self.repository.create(group_data)

        # 생성자를 관리자로 자동 가입
        self.add_member(group.id, created_by_id, role="admin")

        return group

    def get_group_by_id(self, group_id: int) -> Optional[Group]:
        """ID로 그룹 조회"""
        return self.repository.get_by_id(group_id)

    def get_group_by_invite_code(self, invite_code: str) -> Optional[Group]:
        """초대 코드로 그룹 조회"""
        return self.repository.get_by_invite_code(invite_code)

    def update_group(self, group_id: int, update_data: dict) -> Optional[Group]:
        """그룹 정보 수정"""
        return self.repository.update(group_id, update_data)

    def add_member(self, group_id: int, user_id: int, role: str = "member") -> bool:
        """그룹에 멤버 추가"""
        # 그룹 존재 확인
        group = self.repository.get_by_id(group_id)
        if not group or not group.is_active:
            return False

        # 이미 가입된 멤버인지 확인
        existing_membership = self.repository.get_membership(group_id, user_id)
        if existing_membership and existing_membership.is_active:
            return False

        # 최대 멤버 수 확인
        current_member_count = self.repository.get_active_member_count(group_id)
        if current_member_count >= group.max_members:
            return False

        # 멤버십 생성
        membership_data = {
            "group_id": group_id,
            "user_id": user_id,
            "role": role,
            "is_active": True
        }

        return self.repository.create_membership(membership_data) is not None

    def remove_member(self, group_id: int, user_id: int) -> bool:
        """그룹에서 멤버 제거"""
        return self.repository.deactivate_membership(group_id, user_id)

    def get_group_members(self, group_id: int) -> List[GroupMembership]:
        """그룹 멤버 목록 조회"""
        return self.repository.get_active_memberships(group_id)

    def get_user_groups(self, user_id: int) -> List[Group]:
        """사용자가 가입한 그룹 목록 조회"""
        return self.repository.get_user_groups(user_id)

    def _generate_invite_code(self, length: int = 8) -> str:
        """초대 코드 생성"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))