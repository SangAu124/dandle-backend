# DANDEL Backend

AI 기반 자동 얼굴 인식 및 사진 정리 서비스를 제공하는 **DANDEL**의 백엔드 프로젝트입니다.  
FastAPI 기반 REST API 서버로, 사용자 인증, 사진 업로드, 얼굴 인식 및 앨범 관리 기능을 제공합니다.

## 🚀 Features
- 사용자 인증 (이메일 / 소셜 로그인: Apple, Google)
- 그룹 관리 (학급, 여행, 이벤트 단위)
- 사진 업로드 (AWS S3 저장)
- 얼굴 인식 (AWS Rekognition API 연동)
- 개인/그룹 앨범 자동 생성
- 메타데이터 관리 (사진, 얼굴, 사용자, 그룹 관계)

## 🏗 Architecture
```
Client (iOS)
↓ REST API
Backend (FastAPI)
├── API Layer (FastAPI Router)
├── Domain (Entities, UseCases)
├── Services (Business Logic)
├── Infra (PostgreSQL, Redis, AWS S3, Rekognition)
└── Auth (JWT, OAuth2)
```

- **Clean Architecture / Hexagonal 구조** 기반
- Domain, Application, Infra, Interface 레이어 분리
- AI 연산은 초기에는 **AWS Rekognition** 활용 → 추후 FaceNet 기반 모델로 확장 예정


## ⚙️ Tech Stack
- **Language**: Python 3.12
- **Framework**: FastAPI 0.111+
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.x + Alembic (Migration)
- **Cache/Session**: Redis 7
- **Cloud**: AWS S3 (Storage), AWS Rekognition (Face Recognition)
- **Auth**: JWT, OAuth (Apple/Google)
- **Test**: pytest + coverage
- **CI/CD**: GitHub Actions


## 📂 Project Structure
```
dandel-backend/
├── app/
│ ├── api/ # FastAPI 라우터
│ ├── core/ # 설정, 보안, 인증
│ ├── domain/ # 엔티티, 유스케이스
│ ├── infra/ # DB, 외부 API, S3 연동
│ └── services/ # 비즈니스 로직
├── tests/ # 단위/통합 테스트
├── migrations/ # Alembic 마이그레이션
└── docker/ # Dockerfile, Compose 설정
```


## 🧪 Testing
- Unit Test: pytest
- Integration Test: Testcontainers (PostgreSQL, Redis)
- Contract Test: OpenAPI Spec 기반 검증
- 목표: **Coverage ≥ 80%**

실행:
```bash
pytest --cov=app
```

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone Repository
```bash
git clone https://github.com/dandel-ai/dandel-backend.git
cd dandel-backend
```

2. Install FastAPI Dependencies
```bash
pip install "fastapi[all]"
```

3. Setup Environment
환경 변수 파일 생성 (.env):
```bash
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dandel
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=dandel-bucket
JWT_SECRET=your_jwt_secret
```

4. Run with Docker (Option 1)
```bash
docker-compose up --build
```

5. Or Run Locally (Option 2)
```bash
# Apply Migrations
alembic upgrade head

# Start Server
uvicorn app.main:app --reload
```

6. Access API
- API Server: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📜 Contribution Guide
1. 모든 코드 PR은 lint (flake8, black) 및 테스트 통과 필요
2. 새로운 기능 추가 시 테스트 코드 필수
3. 시크릿/키는 .env 또는 AWS Secret Manager 사용 (절대 git push 금지)
4. 커밋 컨벤션: Conventional Commits 준수
    - feat: 새로운 기능
    - fix: 버그 수정
    - docs: 문서 변경
    - test: 테스트 코드 추가/수정

## 📅 Roadmap (MVP)
- 사용자 인증 (JWT + OAuth)
- 사진 업로드 및 S3 저장
- 얼굴 인식 → 앨범 분류
- 그룹별 공유 기능
- 간단한 검색 API
- CI/CD 파이프라인 구축

## 📧 Contact
Website: not yet
Email: dev.sangau20@gmail.com