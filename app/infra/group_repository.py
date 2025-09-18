from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.domain.group import Group, GroupMembership


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, group_data: dict) -> Group:
        """새로운 그룹 생성"""
        group = Group(**group_data)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """ID로 그룹 조회"""
        return self.db.query(Group).filter(Group.id == group_id).first()

    def get_by_invite_code(self, invite_code: str) -> Optional[Group]:
        """초대 코드로 그룹 조회"""
        return (
            self.db.query(Group)
            .filter(Group.invite_code == invite_code)
            .filter(Group.is_active == True)
            .first()
        )

    def update(self, group_id: int, update_data: dict) -> Optional[Group]:
        """그룹 정보 수정"""
        group = self.get_by_id(group_id)
        if not group:
            return None

        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)

        self.db.commit()
        self.db.refresh(group)
        return group

    def delete(self, group_id: int) -> bool:
        """그룹 삭제 (소프트 삭제)"""
        group = self.get_by_id(group_id)
        if not group:
            return False

        group.is_active = False
        self.db.commit()
        return True

    def create_membership(self, membership_data: dict) -> Optional[GroupMembership]:
        """그룹 멤버십 생성"""
        membership = GroupMembership(**membership_data)
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def get_membership(self, group_id: int, user_id: int) -> Optional[GroupMembership]:
        """특정 사용자의 그룹 멤버십 조회"""
        return (
            self.db.query(GroupMembership)
            .filter(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.user_id == user_id
                )
            )
            .first()
        )

    def get_active_memberships(self, group_id: int) -> List[GroupMembership]:
        """그룹의 활성 멤버십 목록 조회"""
        return (
            self.db.query(GroupMembership)
            .filter(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.is_active == True
                )
            )
            .all()
        )

    def get_active_member_count(self, group_id: int) -> int:
        """그룹의 활성 멤버 수 조회"""
        return (
            self.db.query(GroupMembership)
            .filter(
                and_(
                    GroupMembership.group_id == group_id,
                    GroupMembership.is_active == True
                )
            )
            .count()
        )

    def deactivate_membership(self, group_id: int, user_id: int) -> bool:
        """멤버십 비활성화 (그룹 탈퇴)"""
        membership = self.get_membership(group_id, user_id)
        if not membership or not membership.is_active:
            return False

        membership.is_active = False
        self.db.commit()
        return True

    def get_user_groups(self, user_id: int) -> List[Group]:
        """사용자가 가입한 활성 그룹 목록 조회"""
        return (
            self.db.query(Group)
            .join(GroupMembership)
            .filter(
                and_(
                    GroupMembership.user_id == user_id,
                    GroupMembership.is_active == True,
                    Group.is_active == True
                )
            )
            .all()
        )

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Group]:
        """활성 그룹 목록 조회"""
        return (
            self.db.query(Group)
            .filter(Group.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )