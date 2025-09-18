### 프레임워크 & 버전
- Python 3.12
- FastAPI 0.111+ (설치: `pip install "fastapi[all]"`)
- SQLAlchemy 2.x (ORM)
- PostgreSQL 15
- Redis 7 (캐시/세션 관리)

### 빠른 시작
```bash
# FastAPI 모든 의존성 설치
pip install "fastapi[all]"

# 개발 서버 실행
uvicorn app.main:app --reload

# API 문서 확인
# http://localhost:8000/docs
```

### 아키텍처 패턴
- **Clean Architecture / Hexagonal 구조**
  - Domain / Application / Infrastructure / Interface 레이어 분리
- API 레이어는 FastAPI Router 기반 RESTful 설계
- AI 연동: AWS Rekognition API → 추후 자체 FaceNet 모델로 교체 가능

### 코딩 컨벤션
- PEP8 준수
- 함수/변수명: snake_case
- 클래스명: PascalCase
- Docstring: Google Style Docstring
- 린트: flake8 + black 포맷터 적용

### 테스트 전략
- Unit Test: pytest 기반
- Integration Test: Testcontainers로 DB/Redis 연동 검증
- Contract Test: OpenAPI Spec 기반 클라이언트-서버 계약 검증
- CI/CD: GitHub Actions → pytest + coverage ≥ 80% 목표

### 패키지 구조
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

### 금지사항
- Fat Controller 금지 (라우터에 비즈니스 로직 직접 작성 X)
- Raw SQL 직접 호출 금지 (ORM/Query Builder 활용)
- 하드코딩된 시크릿/키 저장 금지 → 환경 변수 또는 AWS Secret Manager 사용
- 전역 상태 공유 금지 (요청 단위 DI 적용)
- `print` 로깅 금지 → Python logger 구조화 로깅 필수