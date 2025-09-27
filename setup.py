#!/usr/bin/env python
"""
Complete setup script for Inventory Management SaaS
This script handles all the setup tasks including:
- Database migrations
- Sample data creation
- ML dataset generation
- Static files collection
- Superuser creation
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.inventory_saas.settings')
django.setup()


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def run_django_command(command, description):
    """Run a Django management command"""
    print(f"\n🔄 {description}...")
    try:
        execute_from_command_line(['manage.py'] + command.split())
        print(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'django', 'djangorestframework', 'psycopg2-binary', 
        'pymongo', 'celery', 'redis', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install requirements: pip install -r backend/requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True


def setup_database():
    """Set up the database"""
    print("\n🗄️ Setting up database...")
    
    # Run migrations
    if not run_django_command('makemigrations', 'Creating migrations'):
        return False
    
    if not run_django_command('migrate', 'Running migrations'):
        return False
    
    return True


def create_superuser():
    """Create a superuser"""
    print("\n👤 Creating superuser...")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists")
        return True
    
    # Create superuser
    try:
        user = User.objects.create_superuser(
            email='admin@inventory-saas.com',
            password='admin123',
            tenant=None  # Superuser doesn't need a tenant
        )
        print("✅ Superuser created successfully")
        print("Email: admin@inventory-saas.com")
        print("Password: admin123")
        return True
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False


def setup_sample_data():
    """Set up sample data"""
    print("\n📊 Setting up sample data...")
    
    try:
        # Import and run the sample data script
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from scripts.setup_sample_data import main as setup_sample_data_main
        setup_sample_data_main()
        return True
    except Exception as e:
        print(f"❌ Failed to setup sample data: {e}")
        return False


def setup_ml_data():
    """Set up ML data"""
    print("\n🤖 Setting up ML data...")
    
    try:
        # Import and run the ML data script
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))
        from scripts.setup_ml_data import main as setup_ml_data_main
        setup_ml_data_main()
        return True
    except Exception as e:
        print(f"❌ Failed to setup ML data: {e}")
        return False


def collect_static_files():
    """Collect static files"""
    print("\n📁 Collecting static files...")
    
    if not run_django_command('collectstatic --noinput', 'Collecting static files'):
        return False
    
    return True


def setup_media_directory():
    """Set up media directory"""
    print("\n📁 Setting up media directory...")
    
    media_dir = os.path.join(os.path.dirname(__file__), 'backend', 'media')
    os.makedirs(media_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = ['products', 'orders', 'invoices', 'exports']
    for subdir in subdirs:
        os.makedirs(os.path.join(media_dir, subdir), exist_ok=True)
    
    print("✅ Media directory setup completed")
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n⚙️ Setting up environment file...")
    
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    env_example = os.path.join(os.path.dirname(__file__), 'env.example')
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(env_example):
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created from example")
        print("⚠️ Please update .env file with your actual configuration")
        return True
    else:
        print("❌ env.example file not found")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Update .env file with your database and other configuration")
    print("2. Start the development server:")
    print("   cd backend && python manage.py runserver")
    print("3. Start the ML service (in another terminal):")
    print("   cd ml && uvicorn main:app --reload --port 8001")
    print("4. Start the frontend (in another terminal):")
    print("   cd frontend && npm install && npm run dev")
    
    print("\n🌐 Access URLs:")
    print("- Backend API: http://localhost:8000")
    print("- API Documentation: http://localhost:8000/api/docs/")
    print("- Admin Panel: http://localhost:8000/admin")
    print("- Frontend: http://localhost:3000")
    print("- ML Service: http://localhost:8001")
    
    print("\n🔑 Demo Credentials:")
    print("- Admin: admin@inventory-saas.com / admin123")
    print("- Demo User: demo@example.com / demo123")
    print("- Demo Tenant: Demo Company")
    
    print("\n📚 Documentation:")
    print("- Architecture: docs/ARCHITECTURE.md")
    print("- Getting Started: GETTING_STARTED.md")
    print("- Contributing: CONTRIBUTING.md")
    
    print("\n🚀 Ready to start developing!")


def main():
    """Main setup function"""
    print("🏭 Inventory Management SaaS - Setup Script")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Create superuser
    if not create_superuser():
        return False
    
    # Setup sample data
    if not setup_sample_data():
        return False
    
    # Setup ML data
    if not setup_ml_data():
        return False
    
    # Collect static files
    if not collect_static_files():
        return False
    
    # Setup media directory
    if not setup_media_directory():
        return False
    
    # Print next steps
    print_next_steps()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
