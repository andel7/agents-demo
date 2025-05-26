#!/bin/bash

# Exit on error
set -e

# Configuration
STACK_NAME="terasky-marketing-demo"
ENVIRONMENT="prod"
INSTANCE_TYPE="t3.large"
REGION="us-east-1"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if required parameters are provided
if [ -z "$1" ]; then
    echo "Usage: $0 <key-pair-name> [vpc-id] [subnet-id]"
    exit 1
fi

KEY_NAME=$1
VPC_ID=${2:-$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text)}
SUBNET_ID=${3:-$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0].SubnetId' --output text)}

echo "Deploying TeraSky Marketing AI Demo..."
echo "Stack Name: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "Instance Type: $INSTANCE_TYPE"
echo "Region: $REGION"
echo "Key Pair: $KEY_NAME"
echo "VPC ID: $VPC_ID"
echo "Subnet ID: $SUBNET_ID"

# Deploy CloudFormation stack
aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file cloudformation.yaml \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        InstanceType=$INSTANCE_TYPE \
        KeyName=$KEY_NAME \
        VpcId=$VPC_ID \
        SubnetId=$SUBNET_ID \
    --capabilities CAPABILITY_IAM \
    --tags owner=lev@terasky.com \
    --region $REGION

# Wait for stack to complete
echo "Waiting for stack deployment to complete..."
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $REGION

# Get instance details
INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
    --output text \
    --region $REGION)

INSTANCE_DNS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicDNS`].OutputValue' \
    --output text \
    --region $REGION)

echo "Deployment completed successfully!"
echo "Instance ID: $INSTANCE_ID"
echo "Instance DNS: $INSTANCE_DNS"
echo "Application will be available at: http://$INSTANCE_DNS"

# Wait for instance to be ready
echo "Waiting for instance to be ready..."
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

# Wait for application to start
echo "Waiting for application to start..."
sleep 60

echo "Setup complete! The application should now be accessible at:"
echo "http://$INSTANCE_DNS" 