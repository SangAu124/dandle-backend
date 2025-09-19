import pytest
from sqlalchemy.orm import Session
from app.infra.face_repository import FaceRepository
from app.domain.face import Face, FaceCollection, FaceMatch
from app.domain.user import User
from app.domain.photo import Photo


class TestFaceRepository:
    """FaceRepository 테스트"""

    @pytest.fixture
    def repo(self, db_session: Session):
        """Repository fixture"""
        return FaceRepository(db_session)

    @pytest.fixture
    def test_user(self, db_session: Session):
        """Test user fixture"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def test_photo(self, db_session: Session, test_user):
        """Test photo fixture"""
        photo = Photo(
            filename="test.jpg",
            file_path="/test/path",
            file_size=1024,
            width=800,
            height=600,
            uploaded_by_id=test_user.id
        )
        db_session.add(photo)
        db_session.commit()
        db_session.refresh(photo)
        return photo

    def test_create_face(self, repo: FaceRepository, test_photo: Photo):
        """얼굴 생성 테스트"""
        face_data = {
            "face_id": "test-face-id-123",
            "confidence": 0.95,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "landmarks": {"eye_left": {"x": 0.2, "y": 0.3}},
            "age_range": {"low": 20, "high": 30},
            "gender": "Male",
            "emotions": [{"type": "HAPPY", "confidence": 0.9}],
            "photo_id": test_photo.id
        }

        face = repo.create_face(face_data)

        assert face.id is not None
        assert face.face_id == "test-face-id-123"
        assert face.confidence == 0.95
        assert face.bounding_box == {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4}
        assert face.photo_id == test_photo.id
        assert face.is_active is True

    def test_get_face_by_id_existing(self, repo: FaceRepository, test_photo: Photo):
        """ID로 기존 얼굴 조회 테스트"""
        face = repo.create_face({
            "face_id": "test-face-id",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        found_face = repo.get_face_by_id(face.id)

        assert found_face is not None
        assert found_face.id == face.id
        assert found_face.face_id == "test-face-id"

    def test_get_face_by_id_non_existing(self, repo: FaceRepository):
        """존재하지 않는 얼굴 조회 테스트"""
        found_face = repo.get_face_by_id(999)
        assert found_face is None

    def test_get_face_by_id_inactive(self, repo: FaceRepository, test_photo: Photo):
        """비활성화된 얼굴 조회 테스트"""
        face = repo.create_face({
            "face_id": "test-face-id",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        # 얼굴 비활성화
        face.is_active = False
        repo.db.commit()

        found_face = repo.get_face_by_id(face.id)
        assert found_face is None

    def test_get_face_by_face_id(self, repo: FaceRepository, test_photo: Photo):
        """Face ID로 얼굴 조회 테스트"""
        face = repo.create_face({
            "face_id": "unique-face-id-123",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        found_face = repo.get_face_by_face_id("unique-face-id-123")

        assert found_face is not None
        assert found_face.id == face.id
        assert found_face.face_id == "unique-face-id-123"

    def test_get_face_by_face_id_non_existing(self, repo: FaceRepository):
        """존재하지 않는 Face ID로 얼굴 조회 테스트"""
        found_face = repo.get_face_by_face_id("non-existing-face-id")
        assert found_face is None

    def test_get_faces_by_photo(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """사진의 얼굴 목록 조회 테스트"""
        # 다른 사진 생성
        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        # 여러 얼굴 생성
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })
        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": test_photo.id
        })
        # 다른 사진의 얼굴
        repo.create_face({
            "face_id": "face-3",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": other_photo.id
        })

        faces = repo.get_faces_by_photo(test_photo.id)

        assert len(faces) == 2
        assert face1 in faces
        assert face2 in faces
        # 신뢰도 순으로 정렬되어야 함
        assert faces[0].confidence >= faces[1].confidence

    def test_get_faces_by_user(self, repo: FaceRepository, test_photo: Photo, test_user: User, db_session: Session):
        """특정 사용자로 태깅된 얼굴 목록 조회 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 얼굴 생성 및 사용자 태깅
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id,
            "identified_user_id": test_user.id
        })
        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": test_photo.id,
            "identified_user_id": test_user.id
        })
        # 다른 사용자로 태깅된 얼굴
        repo.create_face({
            "face_id": "face-3",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": test_photo.id,
            "identified_user_id": other_user.id
        })

        faces = repo.get_faces_by_user(test_user.id)

        assert len(faces) == 2
        assert face1 in faces
        assert face2 in faces

    def test_get_unidentified_faces(self, repo: FaceRepository, test_photo: Photo, test_user: User):
        """미식별 얼굴 목록 조회 테스트"""
        # 식별된 얼굴
        repo.create_face({
            "face_id": "identified-face",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id,
            "identified_user_id": test_user.id
        })

        # 미식별 얼굴들
        unidentified1 = repo.create_face({
            "face_id": "unidentified-1",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": test_photo.id
        })
        unidentified2 = repo.create_face({
            "face_id": "unidentified-2",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": test_photo.id
        })

        faces = repo.get_unidentified_faces()

        assert len(faces) == 2
        assert unidentified1 in faces
        assert unidentified2 in faces

    def test_get_unidentified_faces_pagination(self, repo: FaceRepository, test_photo: Photo):
        """미식별 얼굴 목록 페이지네이션 테스트"""
        # 여러 미식별 얼굴 생성
        for i in range(5):
            repo.create_face({
                "face_id": f"unidentified-{i}",
                "confidence": 0.8,
                "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
                "photo_id": test_photo.id
            })

        faces_page1 = repo.get_unidentified_faces(skip=0, limit=2)
        faces_page2 = repo.get_unidentified_faces(skip=2, limit=2)

        assert len(faces_page1) == 2
        assert len(faces_page2) == 2
        assert faces_page1[0] != faces_page2[0]

    def test_update_face(self, repo: FaceRepository, test_photo: Photo, test_user: User):
        """얼굴 정보 수정 테스트"""
        face = repo.create_face({
            "face_id": "test-face",
            "confidence": 0.8,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        update_data = {
            "identified_user_id": test_user.id,
            "identified_by_id": test_user.id,
            "confidence": 0.9
        }

        updated_face = repo.update_face(face.id, update_data)

        assert updated_face is not None
        assert updated_face.identified_user_id == test_user.id
        assert updated_face.identified_by_id == test_user.id
        assert updated_face.confidence == 0.9

    def test_update_face_non_existing(self, repo: FaceRepository):
        """존재하지 않는 얼굴 수정 테스트"""
        updated_face = repo.update_face(999, {"confidence": 0.9})
        assert updated_face is None

    def test_delete_face(self, repo: FaceRepository, test_photo: Photo):
        """얼굴 삭제 테스트"""
        face = repo.create_face({
            "face_id": "test-face",
            "confidence": 0.8,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        result = repo.delete_face(face.id)

        assert result is True
        # 소프트 삭제 확인
        deleted_face = repo.get_face_by_id(face.id)
        assert deleted_face is None

    def test_delete_face_non_existing(self, repo: FaceRepository):
        """존재하지 않는 얼굴 삭제 테스트"""
        result = repo.delete_face(999)
        assert result is False

    def test_create_collection(self, repo: FaceRepository):
        """얼굴 컬렉션 생성 테스트"""
        collection_data = {
            "collection_id": "test-collection-123",
            "name": "Test Collection",
            "description": "Test Description",
            "owner_type": "user",
            "owner_id": 1,
            "region": "us-east-1"
        }

        collection = repo.create_collection(collection_data)

        assert collection.id is not None
        assert collection.collection_id == "test-collection-123"
        assert collection.name == "Test Collection"
        assert collection.owner_type == "user"
        assert collection.owner_id == 1
        assert collection.is_active is True

    def test_get_collection_by_id(self, repo: FaceRepository):
        """ID로 컬렉션 조회 테스트"""
        collection = repo.create_collection({
            "collection_id": "test-collection",
            "name": "Test Collection",
            "owner_type": "user",
            "owner_id": 1
        })

        found_collection = repo.get_collection_by_id(collection.id)

        assert found_collection is not None
        assert found_collection.id == collection.id
        assert found_collection.collection_id == "test-collection"

    def test_get_collection_by_id_non_existing(self, repo: FaceRepository):
        """존재하지 않는 컬렉션 조회 테스트"""
        found_collection = repo.get_collection_by_id(999)
        assert found_collection is None

    def test_get_collection_by_collection_id(self, repo: FaceRepository):
        """Collection ID로 컬렉션 조회 테스트"""
        collection = repo.create_collection({
            "collection_id": "unique-collection-id",
            "name": "Test Collection",
            "owner_type": "user",
            "owner_id": 1
        })

        found_collection = repo.get_collection_by_collection_id("unique-collection-id")

        assert found_collection is not None
        assert found_collection.id == collection.id
        assert found_collection.collection_id == "unique-collection-id"

    def test_get_collections_by_owner(self, repo: FaceRepository):
        """소유자별 컬렉션 목록 조회 테스트"""
        # 사용자 1의 컬렉션들
        collection1 = repo.create_collection({
            "collection_id": "user1-collection1",
            "name": "User 1 Collection 1",
            "owner_type": "user",
            "owner_id": 1
        })
        collection2 = repo.create_collection({
            "collection_id": "user1-collection2",
            "name": "User 1 Collection 2",
            "owner_type": "user",
            "owner_id": 1
        })

        # 사용자 2의 컬렉션
        repo.create_collection({
            "collection_id": "user2-collection1",
            "name": "User 2 Collection 1",
            "owner_type": "user",
            "owner_id": 2
        })

        collections = repo.get_collections_by_owner("user", 1)

        assert len(collections) == 2
        assert collection1 in collections
        assert collection2 in collections

    def test_create_face_match(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """얼굴 매칭 생성 테스트"""
        # 두 개의 얼굴 생성
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        match_data = {
            "face1_id": face1.id,
            "face2_id": face2.id,
            "similarity": 0.85,
            "match_method": "aws_rekognition"
        }

        match = repo.create_face_match(match_data)

        assert match.id is not None
        assert match.face1_id == face1.id
        assert match.face2_id == face2.id
        assert match.similarity == 0.85
        assert match.match_method == "aws_rekognition"
        assert match.is_confirmed is False
        assert match.is_active is True

    def test_get_face_matches(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """얼굴의 매칭 목록 조회 테스트"""
        # 세 개의 얼굴 생성
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        face3 = repo.create_face({
            "face_id": "face-3",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": other_photo.id
        })

        # 매칭 생성
        match1 = repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face2.id,
            "similarity": 0.9,
            "match_method": "aws_rekognition"
        })

        match2 = repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face3.id,
            "similarity": 0.7,  # 임계값 미만
            "match_method": "aws_rekognition"
        })

        # 임계값 0.8 이상인 매칭만 조회
        matches = repo.get_face_matches(face1.id, threshold=0.8)

        assert len(matches) == 1
        assert match1 in matches
        assert match2 not in matches

    def test_get_face_match_by_id(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """ID로 얼굴 매칭 조회 테스트"""
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        match = repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face2.id,
            "similarity": 0.85,
            "match_method": "aws_rekognition"
        })

        found_match = repo.get_face_match_by_id(match.id)

        assert found_match is not None
        assert found_match.id == match.id
        assert found_match.similarity == 0.85

    def test_update_face_match(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """얼굴 매칭 정보 수정 테스트"""
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        match = repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face2.id,
            "similarity": 0.85,
            "match_method": "aws_rekognition"
        })

        update_data = {
            "is_confirmed": True,
            "confirmed_by_id": test_user.id
        }

        updated_match = repo.update_face_match(match.id, update_data)

        assert updated_match is not None
        assert updated_match.is_confirmed is True
        assert updated_match.confirmed_by_id == test_user.id

    def test_get_unconfirmed_matches(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """미확인 얼굴 매칭 목록 조회 테스트"""
        face1 = repo.create_face({
            "face_id": "face-1",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        face2 = repo.create_face({
            "face_id": "face-2",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        face3 = repo.create_face({
            "face_id": "face-3",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": other_photo.id
        })

        # 확인된 매칭
        repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face2.id,
            "similarity": 0.9,
            "match_method": "aws_rekognition",
            "is_confirmed": True
        })

        # 미확인 매칭
        unconfirmed_match = repo.create_face_match({
            "face1_id": face1.id,
            "face2_id": face3.id,
            "similarity": 0.8,
            "match_method": "aws_rekognition",
            "is_confirmed": False
        })

        matches = repo.get_unconfirmed_matches()

        assert len(matches) == 1
        assert unconfirmed_match in matches

    def test_get_face_count_by_user(self, repo: FaceRepository, test_photo: Photo, test_user: User, db_session: Session):
        """사용자별 얼굴 개수 조회 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # test_user로 태깅된 얼굴들
        for i in range(3):
            repo.create_face({
                "face_id": f"test-user-face-{i}",
                "confidence": 0.9,
                "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
                "photo_id": test_photo.id,
                "identified_user_id": test_user.id
            })

        # other_user로 태깅된 얼굴
        repo.create_face({
            "face_id": "other-user-face",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": test_photo.id,
            "identified_user_id": other_user.id
        })

        count = repo.get_face_count_by_user(test_user.id)
        assert count == 3

        other_count = repo.get_face_count_by_user(other_user.id)
        assert other_count == 1

    def test_get_face_count_by_photo(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """사진별 얼굴 개수 조회 테스트"""
        # 다른 사진 생성
        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        # test_photo의 얼굴들
        for i in range(3):
            repo.create_face({
                "face_id": f"test-photo-face-{i}",
                "confidence": 0.9,
                "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
                "photo_id": test_photo.id
            })

        # other_photo의 얼굴
        repo.create_face({
            "face_id": "other-photo-face",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        count = repo.get_face_count_by_photo(test_photo.id)
        assert count == 3

        other_count = repo.get_face_count_by_photo(other_photo.id)
        assert other_count == 1

    def test_get_faces_by_similarity(self, repo: FaceRepository, test_photo: Photo, db_session: Session, test_user: User):
        """유사도 기준으로 얼굴 검색 테스트"""
        # 기준 얼굴
        target_face = repo.create_face({
            "face_id": "target-face",
            "confidence": 0.9,
            "bounding_box": {"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4},
            "photo_id": test_photo.id
        })

        other_photo = Photo(
            filename="other.jpg",
            file_path="/other/path",
            file_size=2048,
            width=1024,
            height=768,
            uploaded_by_id=test_user.id
        )
        db_session.add(other_photo)
        db_session.commit()
        db_session.refresh(other_photo)

        # 유사한 얼굴들
        similar_face1 = repo.create_face({
            "face_id": "similar-face-1",
            "confidence": 0.8,
            "bounding_box": {"left": 0.5, "top": 0.6, "width": 0.2, "height": 0.3},
            "photo_id": other_photo.id
        })

        similar_face2 = repo.create_face({
            "face_id": "similar-face-2",
            "confidence": 0.7,
            "bounding_box": {"left": 0.1, "top": 0.1, "width": 0.2, "height": 0.2},
            "photo_id": other_photo.id
        })

        # 유사하지 않은 얼굴
        different_face = repo.create_face({
            "face_id": "different-face",
            "confidence": 0.6,
            "bounding_box": {"left": 0.7, "top": 0.8, "width": 0.1, "height": 0.1},
            "photo_id": other_photo.id
        })

        # 매칭 생성
        repo.create_face_match({
            "face1_id": target_face.id,
            "face2_id": similar_face1.id,
            "similarity": 0.9,
            "match_method": "aws_rekognition"
        })

        repo.create_face_match({
            "face1_id": target_face.id,
            "face2_id": similar_face2.id,
            "similarity": 0.85,
            "match_method": "aws_rekognition"
        })

        repo.create_face_match({
            "face1_id": target_face.id,
            "face2_id": different_face.id,
            "similarity": 0.7,  # 임계값 미만
            "match_method": "aws_rekognition"
        })

        # 임계값 0.8 이상인 유사한 얼굴들 검색
        similar_faces = repo.get_faces_by_similarity(target_face.id, threshold=0.8)

        assert len(similar_faces) == 2
        assert similar_face1 in similar_faces
        assert similar_face2 in similar_faces
        assert different_face not in similar_faces