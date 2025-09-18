from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_image_url = Column(String, nullable=True)

    # OAuth fields
    apple_id = Column(String, unique=True, nullable=True)
    google_id = Column(String, unique=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    group_memberships = relationship("GroupMembership", back_populates="user")
    created_groups = relationship("Group", back_populates="created_by")
    uploaded_photos = relationship("Photo", back_populates="uploaded_by")
    created_albums = relationship("Album", back_populates="created_by")
    shared_albums = relationship("AlbumShare", back_populates="shared_with")
    face_identifications = relationship("Face", back_populates="identified_user", foreign_keys="Face.identified_user_id")