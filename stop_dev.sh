#!/bin/bash

# Inventory Management SaaS - Development Stop Script
# This script stops all running services

set -e

echo "🛑 Stopping Inventory Management SaaS Development Environment"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Stop services by PID
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                print_warning "Force killing $service_name..."
                kill -9 $pid
            fi
            
            print_success "$service_name stopped"
        else
            print_warning "$service_name was not running"
        fi
        rm -f "$pid_file"
    else
        print_warning "PID file for $service_name not found"
    fi
}

# Stop all services
stop_all_services() {
    print_status "Stopping all services..."
    
    # Stop frontend
    stop_service "Frontend" "logs/frontend.pid"
    
    # Stop ML service
    stop_service "ML Service" "logs/ml.pid"
    
    # Stop backend
    stop_service "Backend" "logs/backend.pid"
    
    print_success "All services stopped"
}

# Stop Docker containers
stop_docker_containers() {
    print_status "Stopping Docker containers..."
    
    # Stop all services defined in docker-compose.yml
    docker compose down
    
    print_success "Docker containers stopped"
}

# Clean up logs
cleanup_logs() {
    print_status "Cleaning up log files..."
    
    if [ -d "logs" ]; then
        rm -f logs/*.log
        rm -f logs/*.pid
        print_success "Log files cleaned up"
    else
        print_warning "Logs directory not found"
    fi
}

# Main function
main() {
    # Stop all services
    stop_all_services
    
    # Stop Docker containers
    stop_docker_containers
    
    # Clean up logs
    cleanup_logs
    
    echo ""
    echo "✅ All services stopped successfully!"
    echo "=================================="
    echo ""
    echo "To start services again, run: ./start_dev.sh"
    echo ""
}

# Run main function
main "$@"
