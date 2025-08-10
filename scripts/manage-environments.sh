#!/bin/bash

# Multi-Environment Management Script for Nexus Movie Recommendation Backend
# Supports development, staging, and production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="nexus"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

log_header() {
    echo -e "${PURPLE}[NEXUS]${NC} $1"
}

# Show usage
show_usage() {
    echo "Usage: $0 <environment> <command> [options]"
    echo ""
    echo "Environments:"
    echo "  dev, development    - Local development environment"
    echo "  staging            - Staging environment"
    echo "  prod, production   - Production environment"
    echo ""
    echo "Commands:"
    echo "  start              - Start all services"
    echo "  stop               - Stop all services"
    echo "  restart            - Restart all services"
    echo "  status             - Show service status"
    echo "  logs [service]     - Show logs (optionally for specific service)"
    echo "  shell <service>    - Access service shell"
    echo "  migrate            - Run database migrations"
    echo "  collectstatic      - Collect static files"
    echo "  backup             - Create database backup"
    echo "  restore <file>     - Restore database from backup"
    echo "  update             - Pull latest changes and restart"
    echo "  cleanup            - Clean up unused Docker resources"
    echo "  health             - Run health checks"
    echo "  setup              - Initial environment setup"
    echo ""
    echo "Examples:"
    echo "  $0 dev start                    # Start development environment"
    echo "  $0 staging logs web             # Show staging web service logs"
    echo "  $0 prod shell web               # Access production web shell"
    echo "  $0 staging migrate              # Run staging migrations"
}

# Get environment configuration
get_env_config() {
    local env=$1
    
    case $env in
        "dev"|"development")
            ENVIRONMENT="development"
            COMPOSE_FILE="docker-compose.yml"
            ENV_FILE=".env.dev"
            CONTAINER_PREFIX="nexus_dev"
            ;;
        "staging")
            ENVIRONMENT="staging"
            COMPOSE_FILE="docker-compose.staging.yml"
            ENV_FILE=".env.staging"
            CONTAINER_PREFIX="nexus_staging"
            ;;
        "prod"|"production")
            ENVIRONMENT="production"
            COMPOSE_FILE="docker-compose.vps.yml"
            ENV_FILE=".env.production"
            CONTAINER_PREFIX="nexus_vps"
            ;;
        *)
            log_error "Invalid environment: $env"
            show_usage
            exit 1
            ;;
    esac
}

# Check if environment file exists
check_env_file() {
    if [[ ! -f "$PROJECT_ROOT/$ENV_FILE" ]]; then
        log_warning "Environment file $ENV_FILE not found"
        log_info "Creating from template..."
        
        local template_file=""
        case $ENVIRONMENT in
            "development")
                template_file=".env.example"
                ;;
            "staging")
                template_file=".env.staging.example"
                ;;
            "production")
                template_file=".env.production.example"
                ;;
        esac
        
        if [[ -f "$PROJECT_ROOT/$template_file" ]]; then
            cp "$PROJECT_ROOT/$template_file" "$PROJECT_ROOT/$ENV_FILE"
            log_warning "Please edit $ENV_FILE with your actual values"
        else
            log_error "Template file $template_file not found"
            exit 1
        fi
    fi
}

# Docker Compose wrapper
dc() {
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

# Start services
start_services() {
    log_header "Starting $ENVIRONMENT environment..."
    check_env_file
    dc up -d
    log_success "$ENVIRONMENT environment started"
}

# Stop services
stop_services() {
    log_header "Stopping $ENVIRONMENT environment..."
    dc down
    log_success "$ENVIRONMENT environment stopped"
}

# Restart services
restart_services() {
    log_header "Restarting $ENVIRONMENT environment..."
    dc restart
    log_success "$ENVIRONMENT environment restarted"
}

# Show status
show_status() {
    log_header "$ENVIRONMENT environment status:"
    dc ps
}

# Show logs
show_logs() {
    local service=$1
    log_header "Showing logs for $ENVIRONMENT environment..."
    if [[ -n "$service" ]]; then
        dc logs -f "$service"
    else
        dc logs -f
    fi
}

# Access service shell
access_shell() {
    local service=$1
    if [[ -z "$service" ]]; then
        log_error "Service name required for shell access"
        exit 1
    fi
    
    log_header "Accessing $service shell in $ENVIRONMENT environment..."
    
    case $service in
        "web"|"app")
            dc exec web /bin/bash
            ;;
        "db"|"database")
            dc exec db psql -U "${DB_USER:-postgres}" -d "${DB_NAME:-movie_recommendation_dev}"
            ;;
        "redis")
            dc exec redis redis-cli
            ;;
        *)
            dc exec "$service" /bin/bash
            ;;
    esac
}

# Run migrations
run_migrations() {
    log_header "Running migrations in $ENVIRONMENT environment..."
    dc exec web python manage.py migrate
    log_success "Migrations completed"
}

# Collect static files
collect_static() {
    log_header "Collecting static files in $ENVIRONMENT environment..."
    dc exec web python manage.py collectstatic --noinput
    log_success "Static files collected"
}

# Create backup
create_backup() {
    log_header "Creating database backup for $ENVIRONMENT environment..."
    
    local backup_dir="$PROJECT_ROOT/backups"
    mkdir -p "$backup_dir"
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/${ENVIRONMENT}_backup_${timestamp}.sql"
    
    dc exec -T db pg_dump -U "${DB_USER:-postgres}" -d "${DB_NAME:-movie_recommendation_dev}" > "$backup_file"
    
    if [[ -f "$backup_file" ]]; then
        log_success "Backup created: $backup_file"
    else
        log_error "Backup failed"
        exit 1
    fi
}

# Restore backup
restore_backup() {
    local backup_file=$1
    if [[ -z "$backup_file" ]]; then
        log_error "Backup file required for restore"
        exit 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_header "Restoring database backup in $ENVIRONMENT environment..."
    log_warning "This will overwrite the current database!"
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    dc exec -T db psql -U "${DB_USER:-postgres}" -d "${DB_NAME:-movie_recommendation_dev}" < "$backup_file"
    log_success "Database restored from $backup_file"
}

# Update environment
update_environment() {
    log_header "Updating $ENVIRONMENT environment..."
    
    # Pull latest code
    git pull origin main
    
    # Pull latest images
    dc pull
    
    # Restart services
    dc up -d
    
    # Run migrations
    run_migrations
    
    # Collect static files (for production/staging)
    if [[ "$ENVIRONMENT" != "development" ]]; then
        collect_static
    fi
    
    log_success "$ENVIRONMENT environment updated"
}

# Cleanup Docker resources
cleanup_docker() {
    log_header "Cleaning up Docker resources..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful!)
    read -p "Remove unused volumes? This may delete data! (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
    fi
    
    # Remove unused networks
    docker network prune -f
    
    log_success "Docker cleanup completed"
}

# Health check
health_check() {
    log_header "Running health checks for $ENVIRONMENT environment..."
    
    # Check if services are running
    if ! dc ps | grep -q "Up"; then
        log_error "Services are not running"
        return 1
    fi
    
    # Check web service health
    if dc exec web curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
        log_success "Web service is healthy"
    else
        log_error "Web service health check failed"
        return 1
    fi
    
    # Check database connection
    if dc exec db pg_isready -U "${DB_USER:-postgres}" > /dev/null 2>&1; then
        log_success "Database is healthy"
    else
        log_error "Database health check failed"
        return 1
    fi
    
    # Check Redis connection
    if dc exec redis redis-cli ping | grep -q "PONG"; then
        log_success "Redis is healthy"
    else
        log_error "Redis health check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Setup environment
setup_environment() {
    log_header "Setting up $ENVIRONMENT environment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Create environment file
    check_env_file
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/backups"
    
    # Start services
    start_services
    
    # Wait for services to be ready
    sleep 30
    
    # Run migrations
    run_migrations
    
    # Create superuser (for development)
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "Creating superuser for development..."
        dc exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com || true
    fi
    
    log_success "$ENVIRONMENT environment setup completed"
}

# Main function
main() {
    if [[ $# -lt 2 ]]; then
        show_usage
        exit 1
    fi
    
    local environment=$1
    local command=$2
    shift 2
    
    get_env_config "$environment"
    
    case $command in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$1"
            ;;
        "shell")
            access_shell "$1"
            ;;
        "migrate")
            run_migrations
            ;;
        "collectstatic")
            collect_static
            ;;
        "backup")
            create_backup
            ;;
        "restore")
            restore_backup "$1"
            ;;
        "update")
            update_environment
            ;;
        "cleanup")
            cleanup_docker
            ;;
        "health")
            health_check
            ;;
        "setup")
            setup_environment
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"