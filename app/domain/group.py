from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    group_type = Column(String, nullable=False)  # 'class', 'trip', 'event'
    invite_code = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    # 그룹 생성자
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", back_populates="created_groups")

    # 그룹 설정
    is_public = Column(Boolean, default=False)  # 공개/비공개
    max_members = Column(Integer, default=100)  # 최대 멤버 수

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    memberships = relationship("GroupMembership", back_populates="group")
    photos = relationship("Photo", back_populates="group")
    albums = relationship("Album", back_populates="group")


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # 'admin', 'member'
    is_active = Column(Boolean, default=True)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="group_memberships")