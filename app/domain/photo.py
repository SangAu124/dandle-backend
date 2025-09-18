from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # S3 경로
    file_size = Column(Integer, nullable=False)  # bytes

    # 이미지 메타데이터
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String, nullable=True)  # JPEG, PNG, etc.

    # EXIF 데이터
    taken_at = Column(DateTime(timezone=True), nullable=True)  # 촬영 시간
    camera_make = Column(String, nullable=True)
    camera_model = Column(String, nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)

    # AWS S3 정보
    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)

    # 업로드 정보
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_by = relationship("User", back_populates="uploaded_photos")

    # 그룹 정보 (선택적)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="photos")

    # 상태
    is_processed = Column(Boolean, default=False)  # 얼굴 인식 처리 완료 여부
    is_active = Column(Boolean, default=True)

    # 해시 (중복 방지용)
    file_hash = Column(String, nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional relationships
    tags = relationship("PhotoTag", back_populates="photo")
    faces = relationship("Face", back_populates="photo")
    albums = relationship("Album", secondary="album_photos", back_populates="photos")


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    tag_name = Column(String, nullable=False, index=True)
    confidence = Column(Float, default=1.0)  # AI 태그의 신뢰도

    photo = relationship("Photo", back_populates="tags")

    created_at = Column(DateTime(timezone=True), server_default=func.now())