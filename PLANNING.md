# Project Planning Document

## Project Overview

Dandle Backend is an AI-powered automatic face recognition and photo organization service backend. The system provides intelligent photo management capabilities with facial recognition technology to automatically sort and organize photos in group settings such as classes, trips, and events.

## Architecture

The project follows **Clean Architecture / Hexagonal Architecture** principles with clear separation of concerns across four main layers:

### Core Components

- **Interface Layer (`api/`)**: FastAPI router-based RESTful API endpoints
- **Application Layer (`services/`)**: Business logic and use cases orchestration
- **Domain Layer (`domain/`)**: Core entities and business models (SQLAlchemy models)
- **Infrastructure Layer (`infra/`)**: External integrations (database repositories, AWS services, S3 storage)
- **Core (`core/`)**: Configuration, security, authentication, and database connection management

### Data Model

The database schema consists of the following main entities:

#### Users
- **users**: User accounts with authentication (email, username, password, OAuth integration)
- Fields: id, email, username, full_name, hashed_password, is_active, is_verified, profile_image_url, role
- OAuth support: apple_id, google_id
- Timestamps: created_at, updated_at

#### Groups & Memberships
- **groups**: Photo sharing groups (class, trip, event types)
- **group_memberships**: User-group relationships with roles (admin, member)
- Group features: invite codes, public/private settings, member limits

#### Photos & Metadata
- **photos**: Photo storage with rich metadata (S3 integration, EXIF data, GPS coordinates)
- **photo_tags**: AI-generated image tags with confidence scores
- Support for: file metadata, camera info, location data, processing status

#### Albums & Sharing
- **albums**: Photo collections (personal, group, auto-generated)
- **album_photos**: Many-to-many relationship between albums and photos
- **album_shares**: Album sharing with permission levels (view, edit, admin)

#### Face Recognition
- **faces**: Face detection results with AWS Rekognition integration
- **face_collections**: AWS Rekognition collections for different users/groups
- **face_matches**: Face similarity matching with confirmation workflow
- Rich face metadata: bounding boxes, landmarks, emotions, age/gender estimation

### API Endpoints

#### Authentication (`/api/v1/auth`)
- `POST /login` - User authentication with JWT tokens
- `POST /logout` - User logout with token invalidation
- `POST /refresh` - JWT token refresh
- `GET /me` - Current user profile information

#### User Management (`/api/v1/users`)
- `POST /` - User registration
- `GET /me` - Current user information
- `GET /{user_id}` - User profile lookup
- `PUT /{user_id}` - User profile updates

#### Group Management (`/api/v1/groups`)
- `POST /` - Group creation
- `GET /{group_id}` - Group information
- `PUT /{group_id}` - Group updates
- `POST /{group_id}/join` - Join group by ID
- `POST /join-by-code/{invite_code}` - Join by invite code
- `GET /{group_id}/members` - Member listing

#### Photo Management (`/api/v1/photos`)
- `POST /upload` - Photo upload with S3 integration
- `GET /{photo_id}` - Photo information
- `GET /` - Photo listing with filtering
- `PUT /{photo_id}` - Photo updates
- `DELETE /{photo_id}` - Photo deletion (soft delete)
- `GET /{photo_id}/tags` - Photo tags/labels
- `POST /{photo_id}/process` - Face recognition processing

#### Album Management (`/api/v1/albums`)
- `POST /` - Album creation
- `GET /{album_id}` - Album information
- `GET /` - Album listing with filtering
- `PUT /{album_id}` - Album updates
- `DELETE /{album_id}` - Album deletion
- `POST /{album_id}/photos` - Add photos to album
- `DELETE /{album_id}/photos/{photo_id}` - Remove photos
- `POST /{album_id}/share` - Album sharing
- `GET /{album_id}/shares` - Sharing management

#### Face Recognition (`/api/v1/faces`)
- `GET /unidentified` - Unidentified faces
- `GET /photo/{photo_id}` - Faces in specific photo
- `GET /{face_id}` - Face information
- `POST /{face_id}/identify` - Face tagging
- `GET /user/{user_id}` - User's faces
- `GET /search/similar/{face_id}` - Similar face search
- `POST /collections` - Face collection management
- `POST /process/photo/{photo_id}` - Photo face processing
- `POST /matches/{match_id}/confirm` - Match confirmation

## Technology Stack

- **Language**: Python 3.12
- **Web Framework**: FastAPI 0.111+ with full dependencies
- **ORM**: SQLAlchemy 2.x
- **Database**: PostgreSQL 15
- **Cache/Session**: Redis 7
- **Cloud Services**: AWS (S3 for storage, Rekognition for face recognition)
- **Authentication**: JWT tokens with passlib for password hashing
- **Image Processing**: Pillow
- **Background Tasks**: Celery
- **Testing**: pytest with coverage, pytest-asyncio
- **Development**: black formatter, flake8 linter, pre-commit hooks
- **Monitoring**: Sentry integration
- **HTTP Client**: httpx
- **Email**: fastapi-mail

## Project Structure

```
dandle-backend/
├── app/
│   ├── api/                 # FastAPI routers (auth, users, groups, photos, albums, faces)
│   ├── core/                # Configuration, security, database connection
│   ├── domain/              # SQLAlchemy models (entities)
│   ├── infra/               # Repository layer (database access, external APIs)
│   ├── services/            # Business logic and use cases
│   └── main.py              # FastAPI application entry point
├── tests/                   # Unit and integration tests
├── migrations/              # Alembic database migrations
├── docker/                  # Docker configuration files
└── requirements.txt         # Python dependencies
```

## Testing Strategy

- **Unit Tests**: pytest-based testing for individual components
- **Integration Tests**: Testcontainers for database and Redis integration testing
- **Contract Tests**: OpenAPI specification-based client-server contract validation
- **CI/CD**: GitHub Actions with automated testing
- **Coverage Target**: ≥ 80% code coverage requirement
- **Async Testing**: pytest-asyncio for FastAPI endpoint testing

## Development Commands

```bash
# Environment setup
pip install "fastapi[all]"
pip install -r requirements.txt

# Development server
uvicorn app.main:app --reload

# API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)

# Database migrations
alembic init alembic
alembic revision --autogenerate -m "migration message"
alembic upgrade head

# Testing
pytest
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# Code formatting and linting
black .
flake8 .

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Environment Setup

1. **Python Version**: Python 3.12 required
2. **Virtual Environment**: Recommended to use venv or conda
3. **Database**: PostgreSQL 15 instance required
4. **Cache**: Redis 7 instance required
5. **AWS Services**: S3 bucket and Rekognition service access
6. **Environment Variables**: Use .env file or AWS Secret Manager for configuration

Required environment variables:
- Database connection strings
- Redis connection settings
- AWS credentials and region
- JWT secret keys
- CORS origins configuration

## Development Guidelines

### Coding Conventions
- **Code Style**: PEP8 compliance required
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Documentation**: Google Style Docstrings
- **Formatting**: black formatter and flake8 linter enforcement
- **Type Hints**: Use Python type hints throughout

### Architecture Rules
- **No Fat Controllers**: Keep business logic out of API routers
- **Use ORM**: No raw SQL queries - use SQLAlchemy ORM or Query Builder
- **Dependency Injection**: Request-scoped dependency injection (no global state)
- **Structured Logging**: Use Python logger, no print statements
- **Service Layer**: Business logic belongs in services, not repositories

## Security Considerations

- **No Hardcoded Secrets**: Use environment variables or AWS Secret Manager
- **Authentication**: JWT-based authentication with refresh tokens
- **Password Security**: bcrypt hashing with salt
- **CORS Configuration**: Properly configured cross-origin resource sharing
- **Input Validation**: Pydantic models for request/response validation
- **SQL Injection Protection**: ORM usage prevents SQL injection
- **File Upload Security**: S3 integration with proper access controls
- **Token Management**: Secure token storage and invalidation on logout

## Future Considerations

- **Custom Face Recognition**: Replace AWS Rekognition with self-hosted FaceNet model
- **Real-time Features**: WebSocket integration for live photo uploads and notifications
- **Mobile SDK**: Dedicated mobile app integration
- **Advanced Search**: Full-text search with Elasticsearch integration
- **Analytics Dashboard**: Usage metrics and photo analytics
- **Video Processing**: Extend face recognition to video files
- **Privacy Controls**: Enhanced privacy settings and GDPR compliance
- **Performance Optimization**: Caching strategies and CDN integration
- **Microservices**: Split into smaller services as the application scales