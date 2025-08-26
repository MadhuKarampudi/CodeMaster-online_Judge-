#!/bin/bash

# Deployment script for Online Judge to AWS

echo "🚀 Starting deployment process..."

# Check if Docker Hub username is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your Docker Hub username"
    echo "Usage: ./deploy.sh <dockerhub-username>"
    exit 1
fi

DOCKERHUB_USERNAME=$1

# Build and tag Docker image
echo "📦 Building Docker image..."
docker build -t online-judge:latest .

# Tag for Docker Hub
echo "🏷️ Tagging image for Docker Hub..."
docker tag online-judge:latest $DOCKERHUB_USERNAME/online-judge:latest

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push $DOCKERHUB_USERNAME/online-judge:latest

# Update Dockerrun.aws.json with the correct image name
echo "📝 Updating Dockerrun.aws.json..."
sed -i.bak "s/your-dockerhub-username/$DOCKERHUB_USERNAME/g" Dockerrun.aws.json

# Create deployment package for Elastic Beanstalk
echo "📁 Creating deployment package..."
zip -r online-judge-deploy.zip Dockerrun.aws.json .ebextensions/ production_settings.py

echo "✅ Deployment package ready!"
echo "📋 Next steps:"
echo "1. Upload online-judge-deploy.zip to AWS Elastic Beanstalk"
echo "2. Configure environment variables in EB console:"
echo "   - DEBUG=False"
echo "   - SECRET_KEY=<your-secret-key>"
echo "   - ALLOWED_HOSTS=<your-domain>"
echo "   - USE_DOCKER=false"
echo "3. Set up RDS database (optional)"
echo "4. Configure domain and SSL certificate"
