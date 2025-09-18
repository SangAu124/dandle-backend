from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Many-to-Many 관계를 위한 연결 테이블
album_photos = Table(
    'album_photos',
    Base.metadata,
    Column('album_id', Integer, ForeignKey('albums.id'), primary_key=True),
    Column('photo_id', Integer, ForeignKey('photos.id'), primary_key=True),
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    album_type = Column(String, nullable=False)  # 'personal', 'group', 'auto'

    # 자동 생성 앨범의 경우
    auto_criteria = Column(String, nullable=True)  # 'face_recognition', 'date', 'location'

    # 앨범 설정
    is_public = Column(Boolean, default=False)
    cover_photo_id = Column(Integer, ForeignKey("photos.id"), nullable=True)

    # 소유자 정보
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", back_populates="created_albums")

    # 그룹 앨범인 경우
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="albums")

    # 상태
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    photos = relationship("Photo", secondary=album_photos, back_populates="albums")
    cover_photo = relationship("Photo", foreign_keys=[cover_photo_id])
    shares = relationship("AlbumShare", back_populates="album")


class AlbumShare(Base):
    __tablename__ = "album_shares"

    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    shared_with_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(String, default="view")  # 'view', 'edit', 'admin'
    is_active = Column(Boolean, default=True)

    shared_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    album = relationship("Album", back_populates="shares")
    shared_with = relationship("User", back_populates="shared_albums")