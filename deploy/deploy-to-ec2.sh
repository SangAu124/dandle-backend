#!/bin/bash

# AWS EC2 Deployment Script for Dandle Backend
# Usage: ./deploy-to-ec2.sh

set -e

# Configuration
INSTANCE_TYPE="t3.medium"
AMI_ID="ami-0fef361b298d838c8"  # Amazon Linux 2023 in ap-northeast-2
KEY_NAME="dandle-backend-key"
SECURITY_GROUP_NAME="dandle-backend-sg"
REGION="ap-northeast-2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Dandle Backend deployment to AWS EC2...${NC}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Run 'aws configure' first.${NC}"
    exit 1
fi

# Generate random password for database
DB_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 64)

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION > /dev/null 2>&1; then
    echo -e "${YELLOW}📋 Creating EC2 key pair...${NC}"
    aws ec2 create-key-pair --key-name $KEY_NAME --region $REGION --query 'KeyMaterial' --output text > $KEY_NAME.pem
    chmod 400 $KEY_NAME.pem
    echo -e "${GREEN}✅ Key pair created: $KEY_NAME.pem${NC}"
else
    echo -e "${YELLOW}📋 Key pair $KEY_NAME already exists${NC}"
fi

# Create security group if it doesn't exist
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --region $REGION > /dev/null 2>&1; then
    echo -e "${YELLOW}🔒 Creating security group...${NC}"
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for Dandle Backend" \
        --region $REGION \
        --query 'GroupId' --output text)

    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION

    echo -e "${GREEN}✅ Security group created: $SECURITY_GROUP_ID${NC}"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --region $REGION --query 'SecurityGroups[0].GroupId' --output text)
    echo -e "${YELLOW}🔒 Using existing security group: $SECURITY_GROUP_ID${NC}"
fi

# Create user data script with environment variables
USER_DATA=$(cat deploy/ec2-userdata.sh | sed \
    -e "s/\${DB_PASSWORD}/$DB_PASSWORD/g" \
    -e "s/\${JWT_SECRET}/$JWT_SECRET/g" \
    -e "s/\${AWS_ACCESS_KEY_ID}/$(aws configure get aws_access_key_id)/g" \
    -e "s/\${AWS_SECRET_ACCESS_KEY}/$(aws configure get aws_secret_access_key)/g" | base64 -w 0)

# Launch EC2 instance
echo -e "${YELLOW}🖥️  Launching EC2 instance...${NC}"
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data "$USER_DATA" \
    --region $REGION \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=dandle-backend},{Key=Project,Value=dandle},{Key=Environment,Value=production}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${GREEN}✅ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo -e "${GREEN}📍 Instance ID: $INSTANCE_ID${NC}"
echo -e "${GREEN}🌐 Public IP: $PUBLIC_IP${NC}"
echo -e "${GREEN}🔑 SSH Command: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP${NC}"
echo -e "${GREEN}🚀 API URL: http://$PUBLIC_IP:8000${NC}"
echo -e "${GREEN}📚 API Docs: http://$PUBLIC_IP:8000/docs${NC}"

# Save deployment info
cat > deployment-info.txt << EOF
Dandle Backend Deployment Information
====================================
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Key Pair: $KEY_NAME.pem
Security Group: $SECURITY_GROUP_ID ($SECURITY_GROUP_NAME)
Region: $REGION
SSH Command: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP
API URL: http://$PUBLIC_IP:8000
API Docs: http://$PUBLIC_IP:8000/docs
Database Password: $DB_PASSWORD
JWT Secret: $JWT_SECRET

Deployment Date: $(date)
EOF

echo -e "${GREEN}💾 Deployment info saved to deployment-info.txt${NC}"
echo -e "${YELLOW}⚠️  Note: It may take 5-10 minutes for the application to be fully ready.${NC}"