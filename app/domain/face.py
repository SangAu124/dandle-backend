from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Face(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)

    # 얼굴 인식 결과
    face_id = Column(String, unique=True, nullable=False, index=True)  # AWS Rekognition Face ID
    confidence = Column(Float, nullable=False)  # 얼굴 인식 신뢰도

    # 얼굴 위치 정보 (사진 내에서의 좌표)
    bounding_box = Column(JSON, nullable=False)  # {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4}
    landmarks = Column(JSON, nullable=True)  # 얼굴 특징점 좌표

    # 얼굴 특성
    age_range = Column(JSON, nullable=True)  # {"low": 20, "high": 30}
    gender = Column(String, nullable=True)  # "Male", "Female"
    emotions = Column(JSON, nullable=True)  # [{"type": "HAPPY", "confidence": 0.95}]

    # 사진 연결
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    photo = relationship("Photo", back_populates="faces")

    # 사용자 식별 (수동 태깅 또는 자동 인식)
    identified_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    identified_user = relationship("User", back_populates="face_identifications", foreign_keys=[identified_user_id])
    identified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 누가 태깅했는지
    identified_at = Column(DateTime(timezone=True), nullable=True)

    # AWS Rekognition 전용 필드
    external_image_id = Column(String, nullable=True)  # AWS Collection 내 이미지 ID

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FaceCollection(Base):
    __tablename__ = "face_collections"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String, unique=True, nullable=False)  # AWS Rekognition Collection ID
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # 컬렉션 소유자 (그룹 또는 사용자)
    owner_type = Column(String, nullable=False)  # "user", "group"
    owner_id = Column(Integer, nullable=False)  # user_id 또는 group_id

    # AWS 설정
    region = Column(String, default="us-east-1")

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FaceMatch(Base):
    __tablename__ = "face_matches"

    id = Column(Integer, primary_key=True, index=True)

    # 매칭된 얼굴들
    face1_id = Column(Integer, ForeignKey("faces.id"), nullable=False)
    face2_id = Column(Integer, ForeignKey("faces.id"), nullable=False)

    # 매칭 신뢰도
    similarity = Column(Float, nullable=False)  # 0.0 ~ 1.0

    # 매칭 방법
    match_method = Column(String, nullable=False)  # "aws_rekognition", "manual", "facenet"

    # 상태
    is_confirmed = Column(Boolean, default=False)  # 사용자가 확인했는지
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    face1 = relationship("Face", foreign_keys=[face1_id])
    face2 = relationship("Face", foreign_keys=[face2_id])
    confirmed_by = relationship("User")