#!/bin/bash

# Nexus Deployment Script for Contabo VPS
# This script handles the complete deployment of the Movie Recommendation Backend

set -e

echo "🚀 Starting Nexus Deployment..."

# Configuration
PROJECT_NAME="nexus"
DOMAIN="nexus.k1nyanjui.com"
DEPLOY_PATH="/home/deploy/projects/nexus"
NGINX_PATH="/home/deploy/projects/nginx-proxy"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as deploy user
check_user() {
    if [ "$(whoami)" != "deploy" ]; then
        log_error "This script must be run as the 'deploy' user"
        exit 1
    fi
}

# Create directory structure
setup_directories() {
    log_info "Setting up directory structure..."
    
    mkdir -p "$DEPLOY_PATH"
    mkdir -p "$DEPLOY_PATH/data/postgres"
    mkdir -p "$DEPLOY_PATH/logs"
    mkdir -p "$DEPLOY_PATH/backups"
    mkdir -p "$NGINX_PATH/conf.d"
    mkdir -p "$NGINX_PATH/ssl"
    
    log_success "Directory structure created"
}

# Clone or update repository
setup_repository() {
    log_info "Setting up repository..."
    
    if [ -d "$DEPLOY_PATH/.git" ]; then
        log_info "Repository exists, pulling latest changes..."
        cd "$DEPLOY_PATH"
        git pull origin main
    else
        log_info "Cloning repository..."
        git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git "$DEPLOY_PATH"
        cd "$DEPLOY_PATH"
    fi
    
    log_success "Repository setup complete"
}

# Setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    if [ ! -f "$DEPLOY_PATH/.env" ]; then
        if [ -f "$DEPLOY_PATH/.env.vps.example" ]; then
            cp "$DEPLOY_PATH/.env.vps.example" "$DEPLOY_PATH/.env"
            log_warning "Created .env file from template. Please edit it with your actual values!"
            log_warning "Edit: $DEPLOY_PATH/.env"
        else
            log_error ".env.vps.example file not found!"
            exit 1
        fi
    else
        log_info ".env file already exists"
    fi
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    if [ ! -f "$NGINX_PATH/ssl/$DOMAIN.crt" ]; then
        log_warning "SSL certificates not found. You can:"
        log_warning "1. Use Let's Encrypt: certbot --nginx -d $DOMAIN"
        log_warning "2. Use self-signed certificates for testing"
        
        read -p "Generate self-signed certificates for testing? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            openssl req -x509 -newkey rsa:4096 -keyout "$NGINX_PATH/ssl/$DOMAIN.key" \
                -out "$NGINX_PATH/ssl/$DOMAIN.crt" -days 365 -nodes \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
            log_success "Self-signed certificates generated"
        fi
    else
        log_success "SSL certificates already exist"
    fi
}

# Setup Nginx configuration
setup_nginx() {
    log_info "Setting up Nginx configuration..."
    
    if [ -f "$DEPLOY_PATH/nginx/nexus.conf" ]; then
        cp "$DEPLOY_PATH/nginx/nexus.conf" "$NGINX_PATH/conf.d/nexus.conf"
        log_success "Nginx configuration copied"
    else
        log_error "Nginx configuration file not found!"
        exit 1
    fi
}

# Create Docker networks
setup_networks() {
    log_info "Setting up Docker networks..."
    
    # Create nginx-proxy network if it doesn't exist
    if ! docker network ls | grep -q "nginx-proxy"; then
        docker network create nginx-proxy
        log_success "Created nginx-proxy network"
    else
        log_info "nginx-proxy network already exists"
    fi
}

# Pull latest Docker images
pull_images() {
    log_info "Pulling latest Docker images..."
    
    cd "$DEPLOY_PATH"
    docker-compose -f docker-compose.vps.yml pull
    
    log_success "Docker images pulled"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    cd "$DEPLOY_PATH"
    
    # Start the application
    docker-compose -f docker-compose.vps.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check if services are running
    if docker-compose -f docker-compose.vps.yml ps | grep -q "Up"; then
        log_success "Services started successfully"
    else
        log_error "Some services failed to start"
        docker-compose -f docker-compose.vps.yml logs
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd "$DEPLOY_PATH"
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations
    docker-compose -f docker-compose.vps.yml exec -T web python manage.py migrate
    
    # Collect static files
    docker-compose -f docker-compose.vps.yml exec -T web python manage.py collectstatic --noinput
    
    log_success "Database migrations completed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check if the application responds
    if curl -f -s "http://localhost:8000/api/health/" > /dev/null; then
        log_success "Application health check passed"
    else
        log_warning "Application health check failed, but this might be normal during startup"
    fi
    
    # Check if Nginx can reach the application
    if curl -f -s -k "https://$DOMAIN/api/health/" > /dev/null; then
        log_success "External health check passed"
    else
        log_warning "External health check failed. Check Nginx configuration and SSL setup"
    fi
}

# Show deployment status
show_status() {
    echo
    echo "🎉 Deployment Summary:"
    echo "====================="
    echo "📁 Project Path: $DEPLOY_PATH"
    echo "🌐 Domain: https://$DOMAIN"
    echo "🐳 Services Status:"
    
    cd "$DEPLOY_PATH"
    docker-compose -f docker-compose.vps.yml ps
    
    echo
    echo "📋 Next Steps:"
    echo "1. Edit environment variables: $DEPLOY_PATH/.env"
    echo "2. Setup SSL certificates with Let's Encrypt:"
    echo "   sudo certbot --nginx -d $DOMAIN"
    echo "3. Test the application: https://$DOMAIN"
    echo "4. Monitor logs: docker-compose -f docker-compose.vps.yml logs -f"
}

# Main deployment function
main() {
    log_info "Starting Nexus deployment for Contabo VPS..."
    
    check_user
    setup_directories
    setup_repository
    setup_environment
    setup_ssl
    setup_nginx
    setup_networks
    pull_images
    start_services
    run_migrations
    health_check
    show_status
    
    log_success "Deployment completed! 🚀"
}

# Run main function
main "$@"
