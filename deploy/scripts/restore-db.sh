#!/bin/bash

# Database restore script for Dandle Backend
# Usage: ./restore-db.sh <backup-file>

set -e

# Configuration
BACKUP_DIR="/opt/dandle-backend/backups"
DB_CONTAINER="dandle-backend-db-1"
DB_NAME="dandle"
DB_USER="dandleuser"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Usage: $0 <backup-file>${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    # Try looking in backup directory
    if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    else
        echo -e "${RED}❌ Backup file not found: $1${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}🔄 Starting database restore...${NC}"
echo -e "${YELLOW}📁 Backup file: $BACKUP_FILE${NC}"

# Check if database container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}❌ Database container is not running${NC}"
    exit 1
fi

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This will replace the current database!${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Restore cancelled${NC}"
    exit 1
fi

# Stop the application to prevent new connections
echo -e "${YELLOW}🛑 Stopping application...${NC}"
cd /opt/dandle-backend
docker-compose stop app

# Create a backup of current database before restore
echo -e "${YELLOW}💾 Creating backup of current database...${NC}"
CURRENT_BACKUP="pre_restore_$(date +%Y%m%d_%H%M%S)"
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_DIR/${CURRENT_BACKUP}.sql.gz"
echo -e "${GREEN}✅ Current database backed up as: ${CURRENT_BACKUP}.sql.gz${NC}"

# Drop and recreate database
echo -e "${YELLOW}🗑️  Dropping current database...${NC}"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore from backup
echo -e "${YELLOW}📥 Restoring from backup...${NC}"

if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Compressed backup
    zcat "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
else
    # Uncompressed backup
    cat "$BACKUP_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
fi

# Start the application
echo -e "${YELLOW}🚀 Starting application...${NC}"
docker-compose start app

# Wait for application to be healthy
echo -e "${YELLOW}⏳ Waiting for application to be healthy...${NC}"
timeout 60s bash -c 'until curl -f http://localhost:8000/health >/dev/null 2>&1; do sleep 2; done' || {
    echo -e "${RED}❌ Application failed to start properly${NC}"
    echo -e "${YELLOW}🔄 You may need to restore from the pre-restore backup: ${CURRENT_BACKUP}.sql.gz${NC}"
    exit 1
}

echo -e "${GREEN}✅ Database restore completed successfully!${NC}"
echo -e "${GREEN}🎉 Application is running and healthy${NC}"

# Show restore summary
echo -e "\n${YELLOW}📋 Restore Summary:${NC}"
echo -e "  • Restored from: $BACKUP_FILE"
echo -e "  • Pre-restore backup: $BACKUP_DIR/${CURRENT_BACKUP}.sql.gz"
echo -e "  • Application status: ✅ Healthy"