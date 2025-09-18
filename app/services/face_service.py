from typing import Optional, List, Dict, Any
import boto3
from sqlalchemy.orm import Session
from app.domain.face import Face, FaceCollection, FaceMatch
from app.infra.face_repository import FaceRepository


class FaceService:
    def __init__(self, db: Session, aws_region: str = "us-east-1"):
        self.repository = FaceRepository(db)
        self.aws_region = aws_region
        self.rekognition_client = boto3.client('rekognition', region_name=aws_region)

    def process_photo_faces(self, photo_id: int, s3_bucket: str, s3_key: str) -> List[Face]:
        """사진에서 얼굴 인식 처리"""
        try:
            # 1. AWS Rekognition으로 얼굴 감지
            detect_response = self.rekognition_client.detect_faces(
                Image={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                Attributes=['ALL']  # 나이, 성별, 감정 등 모든 속성 포함
            )

            faces = []
            for face_detail in detect_response['FaceDetails']:
                # 2. 얼굴 정보를 DB에 저장
                face_data = {
                    "photo_id": photo_id,
                    "face_id": f"photo_{photo_id}_face_{len(faces)}",
                    "confidence": face_detail['Confidence'],
                    "bounding_box": {
                        "left": face_detail['BoundingBox']['Left'],
                        "top": face_detail['BoundingBox']['Top'],
                        "width": face_detail['BoundingBox']['Width'],
                        "height": face_detail['BoundingBox']['Height']
                    },
                    "landmarks": self._extract_landmarks(face_detail.get('Landmarks', [])),
                    "age_range": {
                        "low": face_detail.get('AgeRange', {}).get('Low'),
                        "high": face_detail.get('AgeRange', {}).get('High')
                    } if face_detail.get('AgeRange') else None,
                    "gender": face_detail.get('Gender', {}).get('Value'),
                    "emotions": self._extract_emotions(face_detail.get('Emotions', [])),
                    "is_active": True
                }

                face = self.repository.create_face(face_data)
                faces.append(face)

                # 3. 기존 얼굴과 비교하여 매칭 검사
                self._find_and_create_matches(face)

            return faces

        except Exception as e:
            # TODO: 로깅 추가
            raise ValueError(f"Face processing failed: {str(e)}")

    def create_face_collection(
        self,
        name: str,
        owner_type: str,
        owner_id: int,
        description: Optional[str] = None
    ) -> FaceCollection:
        """AWS Rekognition 얼굴 컬렉션 생성"""
        # AWS Collection ID 생성
        collection_id = f"{owner_type}_{owner_id}_{name}".replace(" ", "_").lower()

        try:
            # AWS Rekognition 컬렉션 생성
            self.rekognition_client.create_collection(CollectionId=collection_id)

            # DB에 컬렉션 정보 저장
            collection_data = {
                "collection_id": collection_id,
                "name": name,
                "description": description,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "region": self.aws_region,
                "is_active": True
            }

            return self.repository.create_collection(collection_data)

        except Exception as e:
            raise ValueError(f"Collection creation failed: {str(e)}")

    def search_faces_by_image(
        self,
        collection_id: str,
        s3_bucket: str,
        s3_key: str,
        threshold: float = 0.8
    ) -> List[Dict]:
        """이미지로 컬렉션에서 얼굴 검색"""
        try:
            response = self.rekognition_client.search_faces_by_image(
                CollectionId=collection_id,
                Image={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                FaceMatchThreshold=threshold * 100,  # AWS는 퍼센트 사용
                MaxFaces=10
            )

            return response['FaceMatches']

        except Exception as e:
            raise ValueError(f"Face search failed: {str(e)}")

    def identify_face(self, face_id: int, user_id: int, identified_by_id: int) -> bool:
        """얼굴에 사용자 태깅"""
        face = self.repository.get_face_by_id(face_id)
        if not face:
            return False

        update_data = {
            "identified_user_id": user_id,
            "identified_by_id": identified_by_id,
            "identified_at": "NOW()"
        }

        return self.repository.update_face(face_id, update_data) is not None

    def get_user_faces(self, user_id: int) -> List[Face]:
        """특정 사용자로 태깅된 얼굴 목록 조회"""
        return self.repository.get_faces_by_user(user_id)

    def get_photo_faces(self, photo_id: int) -> List[Face]:
        """사진의 얼굴 목록 조회"""
        return self.repository.get_faces_by_photo(photo_id)

    def find_similar_faces(self, face_id: int, threshold: float = 0.8) -> List[FaceMatch]:
        """유사한 얼굴 검색"""
        return self.repository.get_face_matches(face_id, threshold)

    def get_unidentified_faces(self, skip: int = 0, limit: int = 50) -> List[Face]:
        """미식별 얼굴 목록 조회"""
        return self.repository.get_unidentified_faces(skip, limit)

    def confirm_face_match(self, match_id: int, confirmed_by_id: int) -> bool:
        """얼굴 매칭 결과 확인"""
        update_data = {
            "is_confirmed": True,
            "confirmed_by_id": confirmed_by_id,
            "confirmed_at": "NOW()"
        }

        return self.repository.update_face_match(match_id, update_data) is not None

    def _extract_landmarks(self, landmarks: List[Dict]) -> Dict[str, Any]:
        """얼굴 특징점 추출"""
        landmark_dict = {}
        for landmark in landmarks:
            landmark_dict[landmark['Type']] = {
                'x': landmark['X'],
                'y': landmark['Y']
            }
        return landmark_dict

    def _extract_emotions(self, emotions: List[Dict]) -> List[Dict[str, Any]]:
        """감정 정보 추출"""
        return [
            {
                "type": emotion['Type'],
                "confidence": emotion['Confidence']
            }
            for emotion in emotions
        ]

    def _find_and_create_matches(self, face: Face):
        """기존 얼굴과 비교하여 매칭 생성"""
        # TODO: 실제 얼굴 비교 로직 구현
        # 1. 같은 사용자/그룹의 다른 얼굴들과 비교
        # 2. 유사도가 임계값 이상이면 FaceMatch 생성
        # 3. AWS Rekognition의 compare_faces API 사용 가능
        pass

    def add_face_to_collection(
        self,
        collection_id: str,
        s3_bucket: str,
        s3_key: str,
        external_image_id: str
    ) -> str:
        """컬렉션에 얼굴 추가"""
        try:
            response = self.rekognition_client.index_faces(
                CollectionId=collection_id,
                Image={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                ExternalImageId=external_image_id,
                MaxFaces=10
            )

            if response['FaceRecords']:
                return response['FaceRecords'][0]['Face']['FaceId']
            else:
                raise ValueError("No faces found in image")

        except Exception as e:
            raise ValueError(f"Add face to collection failed: {str(e)}")

    def delete_face_from_collection(self, collection_id: str, face_id: str) -> bool:
        """컬렉션에서 얼굴 삭제"""
        try:
            self.rekognition_client.delete_faces(
                CollectionId=collection_id,
                FaceIds=[face_id]
            )
            return True

        except Exception as e:
            # TODO: 로깅 추가
            return False