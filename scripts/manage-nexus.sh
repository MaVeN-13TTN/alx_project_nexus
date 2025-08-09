#!/bin/bash

# Nexus Management Script for Contabo VPS
# Provides common management operations for the deployed application

set -e

PROJECT_PATH="/home/deploy/projects/nexus"
COMPOSE_FILE="docker-compose.vps.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Change to project directory
cd "$PROJECT_PATH"

# Function definitions
status() {
    log_info "Checking service status..."
    docker-compose -f $COMPOSE_FILE ps
}

logs() {
    local service=${1:-}
    if [ -n "$service" ]; then
        log_info "Showing logs for $service..."
        docker-compose -f $COMPOSE_FILE logs -f "$service"
    else
        log_info "Showing logs for all services..."
        docker-compose -f $COMPOSE_FILE logs -f
    fi
}

restart() {
    local service=${1:-}
    if [ -n "$service" ]; then
        log_info "Restarting $service..."
        docker-compose -f $COMPOSE_FILE restart "$service"
    else
        log_info "Restarting all services..."
        docker-compose -f $COMPOSE_FILE restart
    fi
    log_success "Restart completed"
}

stop() {
    log_info "Stopping all services..."
    docker-compose -f $COMPOSE_FILE stop
    log_success "All services stopped"
}

start() {
    log_info "Starting all services..."
    docker-compose -f $COMPOSE_FILE up -d
    sleep 10
    status
    log_success "All services started"
}

update() {
    log_info "Updating application..."
    
    # Pull latest code
    git pull origin main
    
    # Pull latest images
    docker-compose -f $COMPOSE_FILE pull
    
    # Restart services
    docker-compose -f $COMPOSE_FILE up -d
    
    # Run migrations
    docker-compose -f $COMPOSE_FILE exec -T web python manage.py migrate
    
    # Collect static files
    docker-compose -f $COMPOSE_FILE exec -T web python manage.py collectstatic --noinput
    
    log_success "Update completed"
}

backup() {
    log_info "Creating database backup..."
    
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    local backup_path="./backups/$backup_file"
    
    mkdir -p ./backups
    
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U movie_api_user movie_recommendation_prod > "$backup_path"
    
    # Compress the backup
    gzip "$backup_path"
    
    log_success "Backup created: ${backup_path}.gz"
}

shell() {
    local service=${1:-web}
    log_info "Opening shell for $service..."
    docker-compose -f $COMPOSE_FILE exec "$service" /bin/bash
}

health() {
    log_info "Performing health check..."
    
    # Check if containers are running
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_error "Some services are not running"
        return 1
    fi
    
    # Check application health endpoint
    if curl -f -s "http://localhost:8000/api/health/" > /dev/null; then
        log_success "Application is healthy"
    else
        log_error "Application health check failed"
        return 1
    fi
    
    # Check external access
    if curl -f -s -k "https://nexus.k1nyanjui.com/api/health/" > /dev/null; then
        log_success "External access is working"
    else
        log_warning "External access check failed"
    fi
}

cleanup() {
    log_info "Cleaning up unused Docker resources..."
    
    # Remove unused containers, networks, images
    docker system prune -f
    
    # Remove old images
    docker image prune -f
    
    log_success "Cleanup completed"
}

show_help() {
    echo "Nexus Management Script"
    echo "======================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  status              Show service status"
    echo "  logs [service]      Show logs (all services or specific service)"
    echo "  restart [service]   Restart services (all or specific service)"
    echo "  stop                Stop all services"
    echo "  start               Start all services"
    echo "  update              Update application (git pull + docker update)"
    echo "  backup              Create database backup"
    echo "  shell [service]     Open shell in container (default: web)"
    echo "  health              Perform health check"
    echo "  cleanup             Clean up unused Docker resources"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 logs web"
    echo "  $0 restart"
    echo "  $0 shell db"
    echo ""
}

# Main command handling
case "${1:-help}" in
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    restart)
        restart "$2"
        ;;
    stop)
        stop
        ;;
    start)
        start
        ;;
    update)
        update
        ;;
    backup)
        backup
        ;;
    shell)
        shell "$2"
        ;;
    health)
        health
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
