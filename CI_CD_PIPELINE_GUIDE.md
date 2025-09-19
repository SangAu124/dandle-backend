# 🚀 CI/CD Pipeline Guide for Dandle Backend

## 📋 Overview

This guide provides a comprehensive CI/CD pipeline implementation for the Dandle Backend project using GitHub Actions. The pipeline automates testing, building, security scanning, and deployment to AWS EC2.

## 🏗️ Pipeline Architecture

```mermaid
graph LR
    A[Push to Main] --> B[CI Pipeline]
    B --> C[Security Scan]
    C --> D[Build & Push Image]
    D --> E[Deploy to EC2]
    E --> F[Health Check]

    B --> B1[Code Quality]
    B --> B2[Unit Tests]
    B --> B3[Integration Tests]

    C --> C1[Vulnerability Scan]
    C --> C2[SARIF Upload]

    D --> D1[Docker Build]
    D --> D2[Push to GHCR]

    E --> E1[Deploy to Production]
    E --> E2[Database Migration]
    E --> E3[Service Restart]
```

## 🔧 Pipeline Components

### 1. **Continuous Integration (CI)**

#### Code Quality Checks
- **Linting**: `flake8` for Python code style
- **Formatting**: `black` for consistent code formatting
- **Type Checking**: Ready for `mypy` integration

#### Testing Suite
- **Unit Tests**: `pytest` with coverage reporting
- **Integration Tests**: Database and Redis connectivity
- **API Tests**: Endpoint validation and health checks
- **Coverage**: Minimum 80% coverage requirement

#### Services Testing
- **PostgreSQL**: Automated test database setup
- **Redis**: Cache service testing
- **Environment**: Isolated test environment

### 2. **Security Pipeline**

#### Vulnerability Scanning
- **Trivy Scanner**: Comprehensive security vulnerability detection
- **SARIF Reports**: GitHub Security tab integration
- **Dependency Scanning**: Automated security alerts

### 3. **Build & Registry**

#### Docker Image Management
- **Multi-stage Builds**: Optimized container images
- **GitHub Container Registry**: Automated image publishing
- **Image Tagging**: Branch-based and SHA-based tags
- **Caching**: Layer caching for faster builds

### 4. **Continuous Deployment (CD)**

#### Automated Deployment
- **AWS EC2**: Production server deployment
- **Blue-Green Strategy**: Zero-downtime deployments
- **Health Checks**: Automated deployment verification
- **Rollback Capability**: Quick rollback on failure

#### Infrastructure Management
- **Environment Variables**: Secure secret management
- **Database Migrations**: Automated schema updates
- **Service Orchestration**: Docker Compose management

## 📁 File Structure

```
dandle-backend/
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml                    # Main pipeline workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md               # Bug report template
│   │   └── feature_request.md          # Feature request template
│   └── pull_request_template.md        # PR template
├── deploy/
│   ├── production-docker-compose.yml   # Production configuration
│   ├── nginx.conf                      # Reverse proxy config
│   └── scripts/
│       ├── backup-db.sh               # Database backup
│       ├── restore-db.sh              # Database restore
│       └── health-check.sh            # Health monitoring
├── tests/
│   └── test_health.py                 # Health check tests
├── GITHUB_SECRETS_SETUP.md           # Secrets configuration guide
└── CI_CD_PIPELINE_GUIDE.md           # This file
```

## 🚦 Workflow Triggers

### Automatic Triggers
- **Push to Main**: Full CI/CD pipeline
- **Push to Develop**: CI pipeline only
- **Pull Requests**: CI pipeline for validation

### Manual Triggers
- **Workflow Dispatch**: Manual deployment
- **Rollback**: Emergency rollback capability

## 🔐 Security & Secrets

### Required GitHub Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region | `ap-northeast-2` |
| `EC2_HOST` | EC2 public IP | `43.200.191.29` |
| `EC2_SSH_KEY` | SSH private key | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host:port/db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing secret | `your-super-secret-jwt-key` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000,https://yourdomain.com` |
| `DB_PASSWORD` | Database password | `secure-random-password` |

### Security Features
- ✅ **No Hardcoded Secrets**: All sensitive data in GitHub Secrets
- ✅ **Vulnerability Scanning**: Automated security checks
- ✅ **HTTPS Ready**: SSL/TLS configuration templates
- ✅ **Rate Limiting**: API protection with Nginx
- ✅ **Access Control**: Proper CORS configuration

## 🎯 Deployment Strategy

### Production Deployment
1. **Image Build**: Create optimized Docker image
2. **Image Push**: Publish to GitHub Container Registry
3. **EC2 Update**: SSH deployment to production server
4. **Service Update**: Rolling update with health checks
5. **Verification**: Automated health check validation

### Rollback Strategy
1. **Backup Creation**: Automatic backup before deployment
2. **Quick Rollback**: Manual trigger for emergency rollback
3. **Health Monitoring**: Continuous health check monitoring

## 📊 Monitoring & Observability

### Health Checks
- **Application Health**: `/health` endpoint monitoring
- **Database Health**: PostgreSQL connectivity checks
- **Redis Health**: Cache service validation
- **Resource Monitoring**: CPU and memory usage

### Logging & Debugging
- **Container Logs**: Centralized Docker logging
- **GitHub Actions Logs**: Detailed pipeline execution logs
- **Error Tracking**: Automated error notification

## 🔧 Usage Examples

### Deploying a New Feature
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: Add new feature"

# 3. Push and create PR
git push origin feature/new-feature

# 4. After PR approval, merge to main
# - CI/CD pipeline automatically triggers
# - Tests run automatically
# - Security scanning performed
# - Deployment to production
```

### Emergency Rollback
```bash
# Trigger rollback workflow in GitHub Actions
# Or manual rollback via SSH:

ssh -i dandle-backend-key.pem ec2-user@43.200.191.29
cd /opt/dandle-backend
sudo ./deploy/scripts/restore-db.sh backup_20231219_143000.sql.gz
```

### Database Backup
```bash
# Manual backup
ssh -i dandle-backend-key.pem ec2-user@43.200.191.29
sudo ./deploy/scripts/backup-db.sh manual-backup-$(date +%Y%m%d)
```

### Health Check
```bash
# Detailed health check
ssh -i dandle-backend-key.pem ec2-user@43.200.191.29
sudo ./deploy/scripts/health-check.sh --detailed
```

## 🚀 Getting Started

### 1. Repository Setup
```bash
git clone https://github.com/YOUR_USERNAME/dandle-backend.git
cd dandle-backend
```

### 2. Configure Secrets
Follow the [GitHub Secrets Setup Guide](GITHUB_SECRETS_SETUP.md)

### 3. First Deployment
```bash
git add .
git commit -m "feat: Initial CI/CD pipeline setup"
git push origin main
```

### 4. Monitor Deployment
- Go to GitHub Actions tab
- Watch the pipeline execution
- Verify deployment at your EC2 endpoint

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Review security scan results
- **Monthly**: Update dependencies and base images
- **Quarterly**: Review and rotate secrets

### Performance Optimization
- **Image Size**: Optimize Docker layers
- **Build Speed**: Leverage caching strategies
- **Resource Usage**: Monitor and adjust EC2 instance

## 🆘 Troubleshooting

### Common Issues

#### Pipeline Fails at CI Stage
```bash
# Check test failures
# Review linting errors
# Verify environment setup
```

#### Deployment Fails
```bash
# Check SSH connectivity
# Verify AWS credentials
# Review Docker logs
```

#### Health Check Fails
```bash
# Check application logs
# Verify database connectivity
# Review environment variables
```

## 🎉 Benefits

### For Development Team
- ✅ **Automated Quality**: Consistent code quality checks
- ✅ **Fast Feedback**: Quick issue detection
- ✅ **Reduced Manual Work**: Automated deployment process
- ✅ **Reliable Rollbacks**: Safe deployment with rollback capability

### For Operations
- ✅ **Consistent Deployments**: Standardized deployment process
- ✅ **Monitoring**: Comprehensive health checking
- ✅ **Security**: Automated vulnerability scanning
- ✅ **Backup & Recovery**: Automated backup procedures

### For Business
- ✅ **Faster Time to Market**: Rapid feature deployment
- ✅ **Higher Quality**: Automated testing and quality checks
- ✅ **Lower Risk**: Safe deployment with rollback capability
- ✅ **Cost Efficiency**: Automated operations reducing manual overhead

---

🎯 **Your Dandle Backend is now equipped with a production-ready CI/CD pipeline!**

For support and questions, please refer to the issue templates and create a GitHub issue.