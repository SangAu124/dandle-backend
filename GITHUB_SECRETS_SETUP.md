# 🔐 GitHub Secrets Setup Guide

To enable the CI/CD pipeline, you need to configure the following secrets in your GitHub repository.

## 📍 How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Navigate to **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret listed below

## 🔑 Required Secrets

### AWS Configuration
```
AWS_ACCESS_KEY_ID
```
**Value**: Your AWS access key ID
**Description**: AWS credentials for EC2 access and services

```
AWS_SECRET_ACCESS_KEY
```
**Value**: Your AWS secret access key
**Description**: AWS secret key (keep this secure!)

```
AWS_REGION
```
**Value**: `ap-northeast-2`
**Description**: AWS region where your EC2 instance is located

### EC2 Deployment
```
EC2_HOST
```
**Value**: `43.200.191.29`
**Description**: Public IP address of your EC2 instance

```
EC2_SSH_KEY
```
**Value**: Contents of your `dandle-backend-key.pem` file
**Description**: SSH private key for EC2 access (paste the entire file content)

### Database Configuration
```
DATABASE_URL
```
**Value**: `postgresql+psycopg2://dandleuser:3oHe04Pns6N8ayjb2YcyA7zQxEhIxDixveJyJ65xhYM=@db:5432/dandle`
**Description**: PostgreSQL connection string

```
DB_PASSWORD
```
**Value**: `3oHe04Pns6N8ayjb2YcyA7zQxEhIxDixveJyJ65xhYM=`
**Description**: Database password

### Application Configuration
```
REDIS_URL
```
**Value**: `redis://redis:6379/0`
**Description**: Redis connection string

```
JWT_SECRET
```
**Value**: `40di2sg2AQa6MoT0LcnuiPf-r-Cg5Ys-Zx9AtZPnlq-iOSicGVXGXW63MRfBM1jU3SZomGRcRLFTXxJN3fimUw`
**Description**: JWT signing secret

```
CORS_ORIGINS
```
**Value**: `http://localhost:3000,http://43.200.191.29:8000,https://yourdomain.com`
**Description**: Allowed CORS origins (comma-separated)

## 🔄 Setting Up GitHub Container Registry

### 1. Enable GitHub Packages
Your repository needs access to GitHub Container Registry (ghcr.io) to store Docker images.

### 2. Personal Access Token (Optional)
If you encounter permission issues, create a Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with these scopes:
   - `read:packages`
   - `write:packages`
   - `delete:packages`
3. Add as secret:
   ```
   GITHUB_TOKEN
   ```
   **Value**: Your personal access token

## 🏗️ Repository Setup Commands

Run these commands to prepare your repository:

```bash
# Initialize git repository (if not already done)
git init
git remote add origin https://github.com/YOUR_USERNAME/dandle-backend.git

# Add all files and commit
git add .
git commit -m "feat: Add CI/CD pipeline with GitHub Actions

🚀 Features:
- Comprehensive CI pipeline with testing and linting
- Automated Docker image building and publishing
- CD pipeline for AWS EC2 deployment
- Security scanning with Trivy
- Database backup and restore scripts
- Health monitoring and rollback capabilities

🤖 Generated with Claude Code"

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔍 Verification Steps

After setting up secrets and pushing code:

1. **Check Actions Tab**: Go to Actions tab in your GitHub repository
2. **Monitor First Run**: The workflow should trigger automatically on push
3. **Review Logs**: Check each job for any errors
4. **Verify Deployment**: Visit your API at `http://43.200.191.29:8000/health`

## 🚨 Security Best Practices

### ✅ Do's
- ✅ Use GitHub Secrets for all sensitive data
- ✅ Rotate secrets regularly
- ✅ Use environment-specific secrets
- ✅ Monitor access logs

### ❌ Don'ts
- ❌ Never commit secrets to code
- ❌ Don't share secrets in plain text
- ❌ Don't use production secrets in development
- ❌ Don't store secrets in documentation

## 🔧 Troubleshooting

### Common Issues

**1. Permission Denied for EC2**
```bash
# Solution: Check EC2_SSH_KEY format and permissions
# Make sure the SSH key is the complete private key including headers
```

**2. Docker Image Pull Failed**
```bash
# Solution: Verify GitHub Container Registry permissions
# Ensure GITHUB_TOKEN has package read/write permissions
```

**3. Database Connection Failed**
```bash
# Solution: Check DATABASE_URL format and credentials
# Verify database container is running on EC2
```

**4. AWS Credentials Invalid**
```bash
# Solution: Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# Check IAM user permissions for EC2 access
```

## 📋 Quick Setup Checklist

- [ ] Repository created on GitHub
- [ ] All 10 secrets added to repository
- [ ] Code pushed to main branch
- [ ] First workflow run completed successfully
- [ ] Application deployed and accessible
- [ ] Health check passes
- [ ] API documentation available

## 🎯 Next Steps

After successful setup:

1. **Custom Domain**: Configure a custom domain with SSL
2. **Monitoring**: Set up application monitoring
3. **Backup Schedule**: Configure automated database backups
4. **Performance**: Optimize container resources
5. **Security**: Implement additional security measures

---

🎉 **You're all set!** Your CI/CD pipeline is ready to automatically deploy your Dandle Backend on every push to main branch!