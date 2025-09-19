#!/bin/bash

# EC2 User Data Script for Dandle Backend Deployment
# This script runs on EC2 instance startup

set -e

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install -y git

# Create application directory
mkdir -p /opt/dandle-backend
cd /opt/dandle-backend

# Clone repository (replace with your actual repo URL)
git clone https://github.com/sangau/dandle-backend.git .

# Create environment file
cat > .env << EOF
DATABASE_URL=postgresql+psycopg2://dandleuser:${DB_PASSWORD}@db:5432/dandle
REDIS_URL=redis://redis:6379/0
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=ap-northeast-2
JWT_SECRET=${JWT_SECRET}
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
DB_PASSWORD=${DB_PASSWORD}
EOF

# Set proper permissions
chown -R ec2-user:ec2-user /opt/dandle-backend

# Start services
docker-compose up -d

# Setup log rotation
cat > /etc/logrotate.d/dandle-backend << EOF
/opt/dandle-backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
}
EOF

# Setup system service for auto-restart
cat > /etc/systemd/system/dandle-backend.service << EOF
[Unit]
Description=Dandle Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dandle-backend
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

systemctl enable dandle-backend.service

echo "Dandle Backend deployment completed!"