#!/bin/bash

# Inventory Management SaaS - Development Startup Script (No Docker)
# This script starts all services for local development without Docker

set -e

echo "🏭 Starting Inventory Management SaaS Development Environment (No Docker)"
echo "======================================================================="

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

# Check if required services are installed
check_services() {
    print_status "Checking required services..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm"
        exit 1
    fi
    print_success "npm found: $(npm --version)"
    
    # Check PostgreSQL (optional)
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found: $(psql --version | head -n1)"
    else
        print_warning "PostgreSQL not found. Will use SQLite for development."
    fi
    
    # Check Redis (optional)
    if command -v redis-server &> /dev/null; then
        print_success "Redis found: $(redis-server --version | head -n1)"
    else
        print_warning "Redis not found. Will use in-memory cache for development."
    fi
}

# Create .env file if it doesn't exist
create_env_file() {
    print_status "Setting up environment file..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from example"
            
            # Update .env for local development without Docker
            sed -i.bak 's/DB_HOST=db/DB_HOST=localhost/' .env
            sed -i.bak 's/DB_PORT=5432/DB_PORT=5432/' .env
            sed -i.bak 's/MONGODB_URL=mongodb:\/\/mongodb:27017\/inventory_saas/MONGODB_URL=mongodb:\/\/localhost:27017\/inventory_saas/' .env
            sed -i.bak 's/CELERY_BROKER_URL=redis:\/\/redis:6379\/0/CELERY_BROKER_URL=redis:\/\/localhost:6379\/0/' .env
            sed -i.bak 's/CELERY_RESULT_BACKEND=redis:\/\/redis:6379\/0/CELERY_RESULT_BACKEND=redis:\/\/localhost:6379\/0/' .env
            
            print_warning "Updated .env for local development"
        else
            print_error "env.example file not found"
            exit 1
        fi
    else
        print_success ".env file already exists"
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
    
    # Upgrade pip
    pip install --upgrade pip
    
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

# Start Redis (if available)
start_redis() {
    if command -v redis-server &> /dev/null; then
        print_status "Starting Redis..."
        
        # Check if Redis is already running
        if pgrep -x "redis-server" > /dev/null; then
            print_success "Redis is already running"
        else
            # Start Redis in background
            redis-server --daemonize yes --port 6379
            sleep 2
            
            if pgrep -x "redis-server" > /dev/null; then
                print_success "Redis started successfully"
            else
                print_warning "Failed to start Redis. Continuing without Redis..."
            fi
        fi
    else
        print_warning "Redis not available. Using in-memory cache."
    fi
}

# Start MongoDB (if available)
start_mongodb() {
    if command -v mongod &> /dev/null; then
        print_status "Starting MongoDB..."
        
        # Check if MongoDB is already running
        if pgrep -x "mongod" > /dev/null; then
            print_success "MongoDB is already running"
        else
            # Create MongoDB data directory
            mkdir -p data/mongodb
            
            # Start MongoDB in background
            mongod --dbpath data/mongodb --fork --logpath data/mongodb.log
            sleep 3
            
            if pgrep -x "mongod" > /dev/null; then
                print_success "MongoDB started successfully"
            else
                print_warning "Failed to start MongoDB. Using SQLite for all data."
            fi
        fi
    else
        print_warning "MongoDB not available. Using SQLite for all data."
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    source venv/bin/activate
    cd backend
    python manage.py makemigrations
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

# Create logs directory
create_logs_dir() {
    mkdir -p logs
    mkdir -p data
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
    if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
        print_success "Backend service is running on http://localhost:8000"
    else
        print_warning "Backend service may not be fully ready yet. Check logs/backend.log"
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
    if curl -s http://localhost:8001/ > /dev/null 2>&1; then
        print_success "ML service is running on http://localhost:8001"
    else
        print_warning "ML service may not be fully ready yet. Check logs/ml.log"
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
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        print_success "Frontend service is running on http://localhost:3000"
    else
        print_warning "Frontend service may not be fully ready yet. Check logs/frontend.log"
    fi
}

# Main function
main() {
    # Create necessary directories
    create_logs_dir
    
    # Check prerequisites
    check_services
    create_env_file
    
    # Setup environments
    setup_python_env
    setup_node_env
    
    # Start services
    start_redis
    start_mongodb
    
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
    echo "📋 To stop all services, run: ./stop_dev_no_docker.sh"
    echo "📋 To view logs, check the logs/ directory"
    echo ""
    echo "🚀 Happy coding!"
}

# Run main function
main "$@"
