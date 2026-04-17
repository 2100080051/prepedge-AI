#!/bin/bash
"""
Production deployment automation script for PrepEdge AI.
Handles setup, migrations, and monitoring.
"""

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
LOG_DIR="logs"
BACKUP_DIR="backups"

# Functions
print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Main deployment flow
main() {
    print_header "PrepEdge AI Production Deployment"
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Create necessary directories
    create_directories
    
    # Start services
    start_services
    
    # Run migrations
    run_migrations
    
    # Verify deployment
    verify_deployment
    
    # Final status
    print_header "Deployment Complete!"
    print_success "All services are running"
    print_info "API: http://localhost:8000"
    print_info "Docs: http://localhost:8000/docs"
    print_info "Health: http://localhost:8000/api/v1/health/deep"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check .env file
    if [ ! -f .env ]; then
        print_error ".env file not found"
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_info "Please edit .env with your configuration"
        exit 1
    fi
    print_success ".env file exists"
}

setup_environment() {
    print_info "Setting up environment..."
    
    # Source .env file
    set -a
    source .env
    set +a
    
    print_success "Environment variables loaded"
}

create_directories() {
    print_info "Creating necessary directories..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    print_success "Created $LOG_DIR directory"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    print_success "Created $BACKUP_DIR directory"
    
    # Create SSL directory
    mkdir -p ssl
    print_success "Created ssl directory"
}

start_services() {
    print_header "Starting Services"
    
    print_info "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build
    print_success "Images built successfully"
    
    print_info "Starting containers..."
    docker-compose -f "$COMPOSE_FILE" up -d
    print_success "Containers started"
    
    # Wait for PostgreSQL to be ready
    print_info "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U prepedge &> /dev/null; then
            print_success "Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Database failed to start"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for Redis to be ready
    print_info "Waiting for Redis to be ready..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Redis failed to start"
            exit 1
        fi
        sleep 1
    done
}

run_migrations() {
    print_header "Running Database Migrations"
    
    print_info "Running Alembic migrations..."
    docker-compose -f "$COMPOSE_FILE" exec -T api alembic upgrade head
    print_success "Migrations completed"
}

verify_deployment() {
    print_header "Verifying Deployment"
    
    # Check if API is responding
    print_info "Checking API health..."
    for i in {1..10}; do
        if curl -sf http://localhost:8000/api/v1/health > /dev/null; then
            print_success "API is responding"
            break
        fi
        if [ $i -eq 10 ]; then
            print_error "API failed to respond"
            print_info "Run: docker-compose -f $COMPOSE_FILE logs api"
            exit 1
        fi
        sleep 2
    done
    
    # Check services status
    print_info "Checking service status..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Get health information
    print_info "Fetching health information..."
    curl -s http://localhost:8000/api/v1/health/deep | jq . || true
}

# Additional commands
case "${1:-}" in
    "start")
        print_header "Starting Services"
        docker-compose -f "$COMPOSE_FILE" up -d
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    
    "stop")
        print_header "Stopping Services"
        docker-compose -f "$COMPOSE_FILE" down
        print_success "Services stopped"
        ;;
    
    "restart")
        print_header "Restarting Services"
        docker-compose -f "$COMPOSE_FILE" restart
        print_success "Services restarted"
        ;;
    
    "logs")
        SERVICE="${2:-api}"
        print_info "Showing logs for $SERVICE..."
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
        ;;
    
    "migrate")
        print_info "Running database migrations..."
        docker-compose -f "$COMPOSE_FILE" exec api alembic upgrade head
        print_success "Migrations completed"
        ;;
    
    "backup")
        print_header "Creating Database Backup"
        BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
        print_info "Creating backup to $BACKUP_FILE..."
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U prepedge prepedge > "$BACKUP_FILE"
        print_success "Backup created: $BACKUP_FILE"
        ls -lh "$BACKUP_FILE"
        ;;
    
    "restore")
        if [ -z "$2" ]; then
            print_error "Usage: $0 restore <backup_file>"
            exit 1
        fi
        BACKUP_FILE="$2"
        if [ ! -f "$BACKUP_FILE" ]; then
            print_error "Backup file not found: $BACKUP_FILE"
            exit 1
        fi
        print_header "Restoring Database"
        print_info "Restoring from $BACKUP_FILE..."
        cat "$BACKUP_FILE" | docker-compose -f "$COMPOSE_FILE" exec -T db psql -U prepedge prepedge
        print_success "Restore completed"
        ;;
    
    "health")
        print_info "Checking system health..."
        curl -s http://localhost:8000/api/v1/health/deep | jq .
        ;;
    
    "stats")
        print_header "System Statistics"
        docker stats --no-stream
        ;;
    
    "clean")
        print_header "Cleaning Up"
        print_info "Stopping and removing containers..."
        docker-compose -f "$COMPOSE_FILE" down -v
        print_success "Cleanup completed"
        ;;
    
    "full-deploy")
        main
        ;;
    
    *)
        echo "PrepEdge AI Deployment Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  full-deploy    Run complete deployment (default)"
        echo "  start          Start all services"
        echo "  stop           Stop all services"
        echo "  restart        Restart all services"
        echo "  logs <service> View service logs (default: api)"
        echo "  migrate        Run database migrations"
        echo "  backup         Create database backup"
        echo "  restore <file> Restore database from backup"
        echo "  health         Check system health"
        echo "  stats          Show system statistics"
        echo "  clean          Remove all containers and volumes"
        echo ""
        echo "Examples:"
        echo "  $0 full-deploy              # Full deployment"
        echo "  $0 start                    # Start services"
        echo "  $0 logs api                 # View API logs"
        echo "  $0 backup                   # Backup database"
        echo "  $0 restore backups/backup_20240101.sql"
        ;;
esac
