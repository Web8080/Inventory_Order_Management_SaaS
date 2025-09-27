#!/bin/bash

# Inventory Management SaaS - Development Startup Script
# This script starts all services for local development

set -e

echo "🏭 Starting Inventory Management SaaS Development Environment"
echo "=============================================================="

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

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if required files exist
check_files() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from example..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from example"
            print_warning "Please update .env file with your configuration"
        else
            print_error "env.example file not found"
            exit 1
        fi
    fi
}

# Start databases with Docker Compose
start_databases() {
    print_status "Starting databases (PostgreSQL, MongoDB, Redis)..."
    
    # Start only the database services
    docker compose up -d db mongodb redis
    
    # Wait for databases to be ready
    print_status "Waiting for databases to be ready..."
    sleep 10
    
    # Check if databases are running
    if docker compose ps db | grep -q "Up"; then
        print_success "PostgreSQL is running"
    else
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    
    if docker compose ps mongodb | grep -q "Up"; then
        print_success "MongoDB is running"
    else
        print_error "MongoDB failed to start"
        exit 1
    fi
    
    if docker compose ps redis | grep -q "Up"; then
        print_success "Redis is running"
    else
        print_error "Redis failed to start"
        exit 1
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install backend requirements
    print_status "Installing backend requirements..."
    pip install -r backend/requirements.txt
    
    # Install ML requirements
    print_status "Installing ML requirements..."
    pip install -r ml/requirements.txt
    
    print_success "Python environment setup completed"
}

# Setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    # Check if node_modules exists
    if [ ! -d "frontend/node_modules" ]; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    print_success "Node.js environment setup completed"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    source venv/bin/activate
    cd backend
    python manage.py migrate
    cd ..
    
    print_success "Database migrations completed"
}

# Create superuser if it doesn't exist
create_superuser() {
    print_status "Checking for superuser..."
    
    source venv/bin/activate
    cd backend
    
    # Check if superuser exists
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "Superuser exists"; then
        print_status "Creating superuser..."
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@inventory-saas.com', 'admin123')" | python manage.py shell
        print_success "Superuser created (admin@inventory-saas.com / admin123)"
    else
        print_success "Superuser already exists"
    fi
    
    cd ..
}

# Setup sample data
setup_sample_data() {
    print_status "Setting up sample data..."
    
    source venv/bin/activate
    cd backend
    
    # Check if sample data exists
    if ! python manage.py shell -c "from tenants.models import Tenant; print('Sample data exists' if Tenant.objects.filter(slug='demo-tenant').exists() else 'No sample data')" | grep -q "Sample data exists"; then
        print_status "Creating sample data..."
        python scripts/setup_sample_data.py
        print_success "Sample data created"
    else
        print_success "Sample data already exists"
    fi
    
    cd ..
}

# Start backend service
start_backend() {
    print_status "Starting Django backend service..."
    
    # Start backend in background
    source venv/bin/activate
    cd backend
    python manage.py runserver 0.0.0.0:8000 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:8000/api/ > /dev/null; then
        print_success "Backend service is running on http://localhost:8000"
    else
        print_error "Backend service failed to start"
        exit 1
    fi
}

# Start ML service
start_ml_service() {
    print_status "Starting ML service..."
    
    # Start ML service in background
    source venv/bin/activate
    cd ml
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../logs/ml.log 2>&1 &
    ML_PID=$!
    echo $ML_PID > ../logs/ml.pid
    cd ..
    
    # Wait for ML service to start
    sleep 5
    
    # Check if ML service is running
    if curl -s http://localhost:8001/ > /dev/null; then
        print_success "ML service is running on http://localhost:8001"
    else
        print_error "ML service failed to start"
        exit 1
    fi
}

# Start frontend service
start_frontend() {
    print_status "Starting React frontend service..."
    
    # Start frontend in background
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    cd ..
    
    # Wait for frontend to start
    sleep 10
    
    # Check if frontend is running
    if curl -s http://localhost:3000/ > /dev/null; then
        print_success "Frontend service is running on http://localhost:3000"
    else
        print_error "Frontend service failed to start"
        exit 1
    fi
}

# Create logs directory
create_logs_dir() {
    mkdir -p logs
}

# Main function
main() {
    # Create logs directory
    create_logs_dir
    
    # Check prerequisites
    check_docker
    check_files
    
    # Setup environments
    setup_python_env
    setup_node_env
    
    # Start databases
    start_databases
    
    # Setup backend
    run_migrations
    create_superuser
    setup_sample_data
    
    # Start services
    start_backend
    start_ml_service
    start_frontend
    
    # Print success message
    echo ""
    echo "🎉 All services started successfully!"
    echo "=================================="
    echo ""
    echo "🌐 Access URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/api/docs/"
    echo "  Admin Panel:  http://localhost:8000/admin"
    echo "  ML Service:   http://localhost:8001"
    echo ""
    echo "🔑 Demo Credentials:"
    echo "  Admin:        admin@inventory-saas.com / admin123"
    echo "  Demo User:    demo@example.com / demo123"
    echo ""
    echo "📋 To stop all services, run: ./stop_dev.sh"
    echo "📋 To view logs, check the logs/ directory"
    echo ""
    echo "🚀 Happy coding!"
}

# Run main function
main "$@"
