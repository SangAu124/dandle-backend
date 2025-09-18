from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: dict) -> User:
        """새로운 사용자 생성"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_apple_id(self, apple_id: str) -> Optional[User]:
        """Apple ID로 사용자 조회"""
        return self.db.query(User).filter(User.apple_id == apple_id).first()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Google ID로 사용자 조회"""
        return self.db.query(User).filter(User.google_id == google_id).first()

    def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """사용자 정보 수정"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """사용자 삭제 (소프트 삭제)"""
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.db.commit()
        return True

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[User]:
        """활성 사용자 목록 조회"""
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )