#!/bin/bash

# Comprehensive health check script for Dandle Backend
# Usage: ./health-check.sh [--detailed]

set -e

# Configuration
API_URL="http://localhost:8000"
DETAILED=false

# Parse arguments
if [ "$1" = "--detailed" ]; then
    DETAILED=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Dandle Backend Health Check${NC}"
echo -e "${BLUE}================================${NC}"

# Function to check service status
check_service() {
    local service_name="$1"
    local container_name="$2"

    if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
        echo -e "✅ $service_name: ${GREEN}Running${NC}"
        return 0
    else
        echo -e "❌ $service_name: ${RED}Not Running${NC}"
        return 1
    fi
}

# Function to check endpoint
check_endpoint() {
    local endpoint="$1"
    local expected_status="$2"
    local url="$API_URL$endpoint"

    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected_status" ]; then
        echo -e "✅ $endpoint: ${GREEN}OK ($response)${NC}"
        return 0
    else
        echo -e "❌ $endpoint: ${RED}Failed ($response)${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    local container_name="dandle-backend-db-1"

    if docker exec "$container_name" pg_isready -U dandleuser -d dandle >/dev/null 2>&1; then
        echo -e "✅ Database Connection: ${GREEN}OK${NC}"
        return 0
    else
        echo -e "❌ Database Connection: ${RED}Failed${NC}"
        return 1
    fi
}

# Function to check Redis connection
check_redis() {
    local container_name="dandle-backend-redis-1"

    if docker exec "$container_name" redis-cli ping | grep -q "PONG"; then
        echo -e "✅ Redis Connection: ${GREEN}OK${NC}"
        return 0
    else
        echo -e "❌ Redis Connection: ${RED}Failed${NC}"
        return 1
    fi
}

# Main health check
echo -e "\n${YELLOW}🐳 Docker Containers:${NC}"
health_status=0

check_service "Application" "dandle-backend-app-1" || health_status=1
check_service "Database" "dandle-backend-db-1" || health_status=1
check_service "Redis" "dandle-backend-redis-1" || health_status=1

echo -e "\n${YELLOW}🔗 API Endpoints:${NC}"
check_endpoint "/health" "200" || health_status=1
check_endpoint "/" "200" || health_status=1
check_endpoint "/docs" "200" || health_status=1

echo -e "\n${YELLOW}💾 Service Connections:${NC}"
check_database || health_status=1
check_redis || health_status=1

# Detailed checks if requested
if [ "$DETAILED" = true ]; then
    echo -e "\n${YELLOW}📊 Detailed Information:${NC}"

    # Container stats
    echo -e "\n${BLUE}Container Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        dandle-backend-app-1 dandle-backend-db-1 dandle-backend-redis-1 2>/dev/null || echo "Stats not available"

    # Disk usage
    echo -e "\n${BLUE}Disk Usage:${NC}"
    df -h /opt/dandle-backend 2>/dev/null || echo "Disk info not available"

    # Recent logs
    echo -e "\n${BLUE}Recent Application Logs (last 10 lines):${NC}"
    docker logs dandle-backend-app-1 --tail 10 2>/dev/null || echo "Logs not available"

    # Database status
    echo -e "\n${BLUE}Database Status:${NC}"
    docker exec dandle-backend-db-1 psql -U dandleuser -d dandle -c "SELECT COUNT(*) as total_users FROM users;" 2>/dev/null || echo "Database query failed"

    # Redis info
    echo -e "\n${BLUE}Redis Info:${NC}"
    docker exec dandle-backend-redis-1 redis-cli info memory | grep used_memory_human 2>/dev/null || echo "Redis info not available"

    # Network connectivity
    echo -e "\n${BLUE}Network Connectivity:${NC}"
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost 8000 && echo -e "✅ Port 8000: ${GREEN}Open${NC}" || echo -e "❌ Port 8000: ${RED}Closed${NC}"
        nc -z localhost 5432 && echo -e "✅ Port 5432: ${GREEN}Open${NC}" || echo -e "❌ Port 5432: ${RED}Closed${NC}"
        nc -z localhost 6379 && echo -e "✅ Port 6379: ${GREEN}Open${NC}" || echo -e "❌ Port 6379: ${RED}Closed${NC}"
    else
        echo "netcat not available for port checks"
    fi
fi

# Summary
echo -e "\n${BLUE}================================${NC}"
if [ $health_status -eq 0 ]; then
    echo -e "${GREEN}🎉 Overall Health Status: HEALTHY${NC}"
    echo -e "${GREEN}All services are running correctly!${NC}"
else
    echo -e "${RED}⚠️  Overall Health Status: UNHEALTHY${NC}"
    echo -e "${RED}Some services have issues. Please check the details above.${NC}"
fi

echo -e "\n${YELLOW}💡 Tips:${NC}"
echo -e "  • Run with --detailed for more information"
echo -e "  • Check logs: docker logs dandle-backend-app-1"
echo -e "  • Restart services: cd /opt/dandle-backend && docker-compose restart"
echo -e "  • Application URL: $API_URL"
echo -e "  • API Docs: $API_URL/docs"

exit $health_status