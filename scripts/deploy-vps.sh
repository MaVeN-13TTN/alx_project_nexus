#!/bin/bash

# Multi-Environment VPS Deployment Script
# Deploys single application serving both staging and production

set -e

PROJECT_ROOT="/home/deploy/projects/nexus"
ENV_FILE=".env"

echo "🚀 Deploying Multi-Environment Setup..."

# Navigate to project directory
cd "$PROJECT_ROOT"

# Pull latest changes
git pull origin main

# Copy environment file if not exists
if [[ ! -f "$ENV_FILE" ]]; then
    cp ".env.vps.example" "$ENV_FILE"
    echo "⚠️  Please edit $ENV_FILE with your actual values"
    exit 1
fi

# Stop existing services
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" down

# Pull latest images
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" pull

# Start services
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" up -d

# Wait for services
sleep 30

# Run migrations for both databases
echo "🔄 Running production migrations..."
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" exec -T web python manage.py migrate

echo "🔄 Running staging migrations..."
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" exec -T web bash -c "
export HTTP_HOST=staging-nexus.k1nyanjui.com
python manage.py migrate
"

# Collect static files
docker-compose -f docker-compose.vps.yml --env-file "$ENV_FILE" exec -T web python manage.py collectstatic --noinput

echo "✅ Multi-environment deployment complete!"
echo "🌐 Production: https://nexus.k1nyanjui.com"
echo "🎭 Staging: https://staging-nexus.k1nyanjui.com"