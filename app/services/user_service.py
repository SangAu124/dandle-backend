from typing import Optional
from sqlalchemy.orm import Session
from app.domain.user import User
from app.infra.user_repository import UserRepository
from passlib.context import CryptContext


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_user(self, email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        """새로운 사용자 생성"""
        # 이메일 중복 검사
        existing_user = self.repository.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        # 사용자명 중복 검사
        existing_username = self.repository.get_by_username(username)
        if existing_username:
            raise ValueError("Username already taken")

        # 비밀번호 해싱
        hashed_password = self._hash_password(password)

        # 사용자 생성
        user_data = {
            "email": email,
            "username": username,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False
        }

        return self.repository.create(user_data)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.repository.get_by_email(email)

    def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """사용자 정보 수정"""
        return self.repository.update(user_id, update_data)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return self.pwd_context.hash(password)