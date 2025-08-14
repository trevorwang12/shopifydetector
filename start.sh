#!/bin/bash

# Shopify Theme Detector - Docker Deployment Script
# Usage: ./start.sh [dev|prod|stop|restart|logs]

set -e

PROJECT_NAME="shopify-theme-detector"
DEV_COMPOSE="docker-compose.dev.yml"
PROD_COMPOSE="docker-compose.prod.yml"
DEFAULT_COMPOSE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p logs/nginx
    mkdir -p ssl
    print_success "Directories created successfully"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_info "Please edit .env file with your configuration"
        else
            print_error ".env.example not found"
            exit 1
        fi
    fi
}

# Development deployment
start_dev() {
    print_info "Starting development environment..."
    check_docker
    create_directories
    check_env
    
    docker-compose -f $DEV_COMPOSE down 2>/dev/null || true
    docker-compose -f $DEV_COMPOSE up -d --build
    
    print_success "Development environment started!"
    print_info "Application: http://localhost:5000"
    print_info "View logs: docker-compose -f $DEV_COMPOSE logs -f"
}

# Production deployment
start_prod() {
    print_info "Starting production environment..."
    check_docker
    create_directories
    check_env
    
    # Check for SSL certificates
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        print_warning "SSL certificates not found. Generating self-signed certificate..."
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_info "Self-signed certificate generated. Replace with proper certificate for production."
    fi
    
    docker-compose -f $PROD_COMPOSE down 2>/dev/null || true
    docker-compose -f $PROD_COMPOSE up -d --build
    
    print_success "Production environment started!"
    print_info "HTTP: http://localhost"
    print_info "HTTPS: https://localhost"
    print_info "Prometheus: http://localhost:9090"
    print_info "View logs: docker-compose -f $PROD_COMPOSE logs -f"
}

# Standard deployment
start_standard() {
    print_info "Starting standard environment..."
    check_docker
    create_directories
    check_env
    
    docker-compose -f $DEFAULT_COMPOSE down 2>/dev/null || true
    docker-compose -f $DEFAULT_COMPOSE up -d --build
    
    print_success "Standard environment started!"
    print_info "Application: http://localhost:5000"
    print_info "Nginx: http://localhost"
    print_info "View logs: docker-compose logs -f"
}

# Stop all services
stop_services() {
    print_info "Stopping all services..."
    
    docker-compose -f $DEV_COMPOSE down 2>/dev/null || true
    docker-compose -f $PROD_COMPOSE down 2>/dev/null || true
    docker-compose -f $DEFAULT_COMPOSE down 2>/dev/null || true
    
    print_success "All services stopped"
}

# Restart services
restart_services() {
    print_info "Restarting services..."
    stop_services
    sleep 2
    
    # Determine which environment to restart based on running containers
    if docker ps --format "{{.Names}}" | grep -q "dev"; then
        start_dev
    elif docker ps --format "{{.Names}}" | grep -q "prod"; then
        start_prod
    else
        start_standard
    fi
}

# Show logs
show_logs() {
    print_info "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    print_info "Showing logs for all containers..."
    
    # Try to show logs for any running compose setup
    if docker-compose -f $PROD_COMPOSE ps -q > /dev/null 2>&1; then
        docker-compose -f $PROD_COMPOSE logs --tail=50 -f
    elif docker-compose -f $DEV_COMPOSE ps -q > /dev/null 2>&1; then
        docker-compose -f $DEV_COMPOSE logs --tail=50 -f
    else
        docker-compose logs --tail=50 -f
    fi
}

# Show status
show_status() {
    print_info "Docker Compose Status:"
    echo ""
    
    echo "=== Running Containers ==="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "=== Resource Usage ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    echo ""
    echo "=== Health Checks ==="
    curl -s http://localhost:5000/health 2>/dev/null && echo "✅ Application: Healthy" || echo "❌ Application: Unhealthy"
    curl -s http://localhost/health 2>/dev/null && echo "✅ Nginx: Healthy" || echo "❌ Nginx: Not accessible"
}

# Show help
show_help() {
    echo "Shopify Theme Detector - Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev      Start development environment (hot reload, debug mode)"
    echo "  prod     Start production environment (SSL, monitoring, redis)"
    echo "  standard Start standard environment (nginx proxy, production Flask)"
    echo "  stop     Stop all services"
    echo "  restart  Restart services"
    echo "  logs     Show logs for running services"
    echo "  status   Show status of running containers"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Start development environment"
    echo "  $0 prod     # Start production environment"
    echo "  $0 logs     # View logs"
    echo "  $0 stop     # Stop all services"
}

# Main logic
case "${1:-help}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "standard")
        start_standard
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_help
        ;;
esac