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

## 코드 리뷰 결과

### 🔍 발견된 이슈들

1. **구현되지 않은 기능들 (40+ TODO 항목)**
   - 모든 API 엔드포인트가 501 Not Implemented 상태
   - 서비스 레이어의 핵심 로직 미구현
   - AWS 연동 및 얼굴 인식 기능 미완성

2. **테스트 커버리지 부족 (53% < 80%)**
   - Security 모듈: 0% 커버리지 (65 statements 미테스트)
   - Repository 모듈들: 대부분 0-60% 커버리지
   - Album/Photo/Face 서비스: 0% 커버리지

3. **의존성 관리**
   - requirements.txt에 bcrypt 누락 (설치됨)
   - 모든 필요 패키지는 적절히 명시됨

### ✅ 양호한 점들

1. **코드 품질**
   - import * 사용 없음
   - 하드코딩된 시크릿 없음
   - print 디버깅 코드 없음

2. **아키텍처**
   - 깔끔한 레이어 분리 (domain, infra, services, api)
   - 적절한 모델 관계 설정
   - FastAPI 모범 사례 준수