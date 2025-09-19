# Task List

## Test Failures to Fix

- [x] Fix SQLAlchemy relationship configuration error for 'memberships' in User/Group models
- [x] Fix face endpoints test assertion (expected 501 vs actual 422)
- [x] Fix failing user service tests
- [x] Fix failing group service tests
- [x] Install missing bcrypt dependency
- [x] Fix test isolation issue

## Coverage Issues (53% → 59% → Goal: 80%)

- [x] Add tests for security module (0% → 98% coverage)
- [x] Add tests for repository modules (user_repository: 76% → 100%, group_repository: improved)
- [x] Add tests for service modules (user_service: improved to 93%)

## 💡 Significant Coverage Improvements Made

1. **Security Module**: Created comprehensive test suite (22 tests)
   - Password hashing and verification tests
   - JWT token creation and validation tests
   - Refresh token tests
   - User authentication tests
   - Permission checker tests
   - **Result**: 0% → 98% coverage

2. **Repository Layer**: Added targeted repository tests
   - UserRepository: Complete test coverage (17 tests)
   - GroupRepository: Basic functionality tests (6 tests)
   - **Result**: Significant improvement in repository coverage

3. **Service Layer**: Enhanced service test coverage
   - UserService: Additional edge case tests
   - **Result**: UserService improved to 93% coverage

## 📊 Overall Progress: 53% → 59% Coverage (+6%)

# 🔴 긴급

- [x] **[보안]** `app/core/config.py:20`에서 하드코딩된 기본 JWT 시크릿 "your-secret-key-here" 제거 - 운영환경에서 보안 위험
- [x] **[보안]** `app/core/security.py:138-144`에서 권한 검사 로직 미구현 - 모든 요청이 권한 검사 없이 통과
- [x] **[보안]** CORS 설정 `app/core/config.py:46`에서 "*" 모든 Origin 허용 - 운영환경에서 보안 위험

# 🟠 높음

- [x] **[성능]** `app/main.py:38`에서 deprecated `@app.on_event("startup")` 사용 - FastAPI 0.93+에서 권장하지 않음, `lifespan` 함수로 교체 필요
- [ ] **[아키텍처]** 43개의 TODO 항목으로 핵심 기능 미구현 - 모든 API 엔드포인트가 501 상태 반환
- [ ] **[테스트]** 테스트 커버리지 58% < 목표 80% - Repository/Service 레이어 0% 커버리지
- [x] **[데이터베이스]** `app/infra/user_repository.py:66`에서 `== True` 대신 `is True` 사용 권장

# 🟡 중간

- [x] **[코드품질]** `app/api/user_router.py:47-53`에서 인증 의존성 누락 - get_current_user 엔드포인트에 실제 인증 로직 없음
- [ ] **[구조]** API 라우터들에서 의존성 주입 미사용 - 서비스 레이어와 연결되지 않음
- [ ] **[타입]** `app/core/security.py:103,137`에서 타입 힌트 누락 - `current_user` 파라미터 타입 미명시
- [ ] **[성능]** `app/core/database.py:15-31`에서 PostgreSQL 연결 풀 설정 최적화 가능

# 🟢 낮음

- [ ] **[문서]** 모든 공개 API 함수에 Google Style Docstring 추가 필요
- [ ] **[정리]** `app/core/security.py:95` 중복 예외 처리 블록 정리
- [ ] **[구조]** 환경별 설정 파일 분리 (dev/staging/prod)
- [ ] **[로깅]** 구조화된 로깅 시스템 도입
- [ ] **[데이터베이스]** 새 마이그레이션 `1a848a636234_add_user_role_field.py`에서 role 필드가 nullable=True - 기본값 설정 고려
- [ ] **[테스트]** 새 role 필드에 대한 도메인 테스트 누락

## 📊 코드 리뷰 통계 (최신 업데이트)

- **총 분석 파일**: 30개 Python 파일
- **해결된 이슈**: 6개 (긴급 3개 + 높음 2개 + 중간 1개 ✅)
- **남은 이슈**: 13개 (긴급 0개, 높음 2개, 중간 3개, 낮음 8개)
- **테스트 커버리지**: 58% (목표 80%)
- **TODO 항목**: 42개 (추가 1개 감소)

## ✅ 양호한 점들

1. **코드 품질**
   - import * 사용 없음
   - print 디버깅 코드 없음
   - 적절한 모델 관계 설정

2. **아키텍처**
   - 깔끔한 레이어 분리 (domain, infra, services, api)
   - FastAPI 모범 사례 준수
   - Clean Architecture 패턴 적용