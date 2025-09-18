from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.domain.face import Face, FaceCollection, FaceMatch


class FaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_face(self, face_data: dict) -> Face:
        """새로운 얼굴 생성"""
        face = Face(**face_data)
        self.db.add(face)
        self.db.commit()
        self.db.refresh(face)
        return face

    def get_face_by_id(self, face_id: int) -> Optional[Face]:
        """ID로 얼굴 조회"""
        return (
            self.db.query(Face)
            .filter(and_(Face.id == face_id, Face.is_active == True))
            .first()
        )

    def get_face_by_face_id(self, face_id: str) -> Optional[Face]:
        """Face ID로 얼굴 조회"""
        return (
            self.db.query(Face)
            .filter(and_(Face.face_id == face_id, Face.is_active == True))
            .first()
        )

    def get_faces_by_photo(self, photo_id: int) -> List[Face]:
        """사진의 얼굴 목록 조회"""
        return (
            self.db.query(Face)
            .filter(and_(Face.photo_id == photo_id, Face.is_active == True))
            .order_by(Face.confidence.desc())
            .all()
        )

    def get_faces_by_user(self, user_id: int) -> List[Face]:
        """특정 사용자로 태깅된 얼굴 목록 조회"""
        return (
            self.db.query(Face)
            .filter(
                and_(
                    Face.identified_user_id == user_id,
                    Face.is_active == True
                )
            )
            .order_by(Face.created_at.desc())
            .all()
        )

    def get_unidentified_faces(self, skip: int = 0, limit: int = 50) -> List[Face]:
        """미식별 얼굴 목록 조회"""
        return (
            self.db.query(Face)
            .filter(
                and_(
                    Face.identified_user_id.is_(None),
                    Face.is_active == True
                )
            )
            .order_by(Face.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_face(self, face_id: int, update_data: dict) -> Optional[Face]:
        """얼굴 정보 수정"""
        face = self.get_face_by_id(face_id)
        if not face:
            return None

        for key, value in update_data.items():
            if hasattr(face, key):
                if value == "NOW()":
                    setattr(face, key, func.now())
                else:
                    setattr(face, key, value)

        self.db.commit()
        self.db.refresh(face)
        return face

    def delete_face(self, face_id: int) -> bool:
        """얼굴 삭제 (소프트 삭제)"""
        face = self.get_face_by_id(face_id)
        if not face:
            return False

        face.is_active = False
        self.db.commit()
        return True

    def create_collection(self, collection_data: dict) -> FaceCollection:
        """얼굴 컬렉션 생성"""
        collection = FaceCollection(**collection_data)
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return collection

    def get_collection_by_id(self, collection_id: int) -> Optional[FaceCollection]:
        """ID로 컬렉션 조회"""
        return (
            self.db.query(FaceCollection)
            .filter(and_(FaceCollection.id == collection_id, FaceCollection.is_active == True))
            .first()
        )

    def get_collection_by_collection_id(self, collection_id: str) -> Optional[FaceCollection]:
        """Collection ID로 컬렉션 조회"""
        return (
            self.db.query(FaceCollection)
            .filter(
                and_(
                    FaceCollection.collection_id == collection_id,
                    FaceCollection.is_active == True
                )
            )
            .first()
        )

    def get_collections_by_owner(self, owner_type: str, owner_id: int) -> List[FaceCollection]:
        """소유자별 컬렉션 목록 조회"""
        return (
            self.db.query(FaceCollection)
            .filter(
                and_(
                    FaceCollection.owner_type == owner_type,
                    FaceCollection.owner_id == owner_id,
                    FaceCollection.is_active == True
                )
            )
            .order_by(FaceCollection.created_at.desc())
            .all()
        )

    def create_face_match(self, match_data: dict) -> FaceMatch:
        """얼굴 매칭 생성"""
        match = FaceMatch(**match_data)
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_face_matches(self, face_id: int, threshold: float = 0.8) -> List[FaceMatch]:
        """얼굴의 매칭 목록 조회"""
        return (
            self.db.query(FaceMatch)
            .filter(
                and_(
                    or_(
                        FaceMatch.face1_id == face_id,
                        FaceMatch.face2_id == face_id
                    ),
                    FaceMatch.similarity >= threshold,
                    FaceMatch.is_active == True
                )
            )
            .order_by(FaceMatch.similarity.desc())
            .all()
        )

    def get_face_match_by_id(self, match_id: int) -> Optional[FaceMatch]:
        """ID로 얼굴 매칭 조회"""
        return (
            self.db.query(FaceMatch)
            .filter(and_(FaceMatch.id == match_id, FaceMatch.is_active == True))
            .first()
        )

    def update_face_match(self, match_id: int, update_data: dict) -> Optional[FaceMatch]:
        """얼굴 매칭 정보 수정"""
        match = self.get_face_match_by_id(match_id)
        if not match:
            return None

        for key, value in update_data.items():
            if hasattr(match, key):
                if value == "NOW()":
                    setattr(match, key, func.now())
                else:
                    setattr(match, key, value)

        self.db.commit()
        self.db.refresh(match)
        return match

    def get_unconfirmed_matches(self, skip: int = 0, limit: int = 50) -> List[FaceMatch]:
        """미확인 얼굴 매칭 목록 조회"""
        return (
            self.db.query(FaceMatch)
            .filter(
                and_(
                    FaceMatch.is_confirmed == False,
                    FaceMatch.is_active == True
                )
            )
            .order_by(FaceMatch.similarity.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_faces_by_similarity(
        self,
        target_face_id: int,
        threshold: float = 0.8,
        limit: int = 50
    ) -> List[Face]:
        """유사도 기준으로 얼굴 검색"""
        # 서브쿼리로 매칭된 얼굴 ID들 가져오기
        matched_face_ids = (
            self.db.query(
                func.case(
                    (FaceMatch.face1_id == target_face_id, FaceMatch.face2_id),
                    else_=FaceMatch.face1_id
                ).label("matched_face_id")
            )
            .filter(
                and_(
                    or_(
                        FaceMatch.face1_id == target_face_id,
                        FaceMatch.face2_id == target_face_id
                    ),
                    FaceMatch.similarity >= threshold,
                    FaceMatch.is_active == True
                )
            )
            .subquery()
        )

        return (
            self.db.query(Face)
            .filter(
                and_(
                    Face.id.in_(matched_face_ids),
                    Face.is_active == True
                )
            )
            .limit(limit)
            .all()
        )

    def get_face_count_by_user(self, user_id: int) -> int:
        """사용자별 얼굴 개수 조회"""
        return (
            self.db.query(func.count(Face.id))
            .filter(
                and_(
                    Face.identified_user_id == user_id,
                    Face.is_active == True
                )
            )
            .scalar()
        )

    def get_face_count_by_photo(self, photo_id: int) -> int:
        """사진별 얼굴 개수 조회"""
        return (
            self.db.query(func.count(Face.id))
            .filter(
                and_(
                    Face.photo_id == photo_id,
                    Face.is_active == True
                )
            )
            .scalar()
        )