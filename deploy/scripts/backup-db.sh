#!/bin/bash

# Database backup script for Dandle Backend
# Usage: ./backup-db.sh [backup-name]

set -e

# Configuration
BACKUP_DIR="/opt/dandle-backend/backups"
DB_CONTAINER="dandle-backend-db-1"
DB_NAME="dandle"
DB_USER="dandleuser"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${1:-backup_${TIMESTAMP}}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🗄️  Starting database backup...${NC}"

# Create backup directory if it doesn't exist
sudo mkdir -p "$BACKUP_DIR"

# Check if database container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}❌ Database container is not running${NC}"
    exit 1
fi

# Create database backup
echo -e "${YELLOW}📦 Creating backup: ${BACKUP_NAME}.sql${NC}"

docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DIR/${BACKUP_NAME}.sql"

# Compress the backup
echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
gzip "$BACKUP_DIR/${BACKUP_NAME}.sql"

# Set proper permissions
sudo chown -R ec2-user:ec2-user "$BACKUP_DIR"

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" | cut -f1)

echo -e "${GREEN}✅ Backup completed successfully!${NC}"
echo -e "📁 Backup location: $BACKUP_DIR/${BACKUP_NAME}.sql.gz"
echo -e "📊 Backup size: $BACKUP_SIZE"

# Optional: Upload to S3 (uncomment if needed)
# if [ -n "$AWS_S3_BACKUP_BUCKET" ]; then
#     echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
#     aws s3 cp "$BACKUP_DIR/${BACKUP_NAME}.sql.gz" "s3://$AWS_S3_BACKUP_BUCKET/db-backups/"
#     echo -e "${GREEN}✅ Backup uploaded to S3${NC}"
# fi

# Optional: Clean up old backups (keep last 7 days)
echo -e "${YELLOW}🧹 Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +7 -delete

echo -e "${GREEN}🎉 Database backup process completed!${NC}"