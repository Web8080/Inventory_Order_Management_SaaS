#!/bin/bash

# GitHub Preparation Script for Inventory Management SaaS
# Author: Victor Ibhafidon for XTAINLESS TECHNOLOGIES

echo "🚀 Preparing Inventory Management SaaS for GitHub..."

# Set GitHub username
GITHUB_USERNAME="web8080"
REPO_NAME="inventory-saas"

echo "📋 GitHub Configuration:"
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# ML Models
*.pkl
*.joblib
models/
ml_models/

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
EOF
    echo "✅ .gitignore created"
else
    echo "✅ .gitignore already exists"
fi

# Create LICENSE file
if [ ! -f LICENSE ]; then
    echo "📄 Creating MIT LICENSE..."
    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Victor Ibhafidon for XTAINLESS TECHNOLOGIES

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
    echo "✅ LICENSE created"
else
    echo "✅ LICENSE already exists"
fi

# Create CONTRIBUTING.md
if [ ! -f CONTRIBUTING.md ]; then
    echo "📝 Creating CONTRIBUTING.md..."
    cat > CONTRIBUTING.md << 'EOF'
# Contributing to Inventory Management SaaS

Thank you for your interest in contributing to the Inventory Management SaaS project!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/inventory-saas.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

See the [README.md](README.md) for detailed setup instructions.

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features

## Reporting Issues

When reporting issues, please include:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)

## Feature Requests

For feature requests, please:
- Describe the feature clearly
- Explain the use case
- Consider implementation complexity
- Check if similar features exist

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
EOF
    echo "✅ CONTRIBUTING.md created"
else
    echo "✅ CONTRIBUTING.md already exists"
fi

# Create GitHub Actions workflow
mkdir -p .github/workflows
if [ ! -f .github/workflows/ci-cd.yml ]; then
    echo "🔧 Creating GitHub Actions CI/CD workflow..."
    cat > .github/workflows/ci-cd.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_inventory_saas
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Python dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run Django tests
      run: |
        cd backend
        python manage.py test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_inventory_saas
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build
    
    - name: Check code quality
      run: |
        cd backend
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
EOF
    echo "✅ GitHub Actions workflow created"
else
    echo "✅ GitHub Actions workflow already exists"
fi

# Create deployment documentation
if [ ! -f DEPLOYMENT.md ]; then
    echo "📚 Creating DEPLOYMENT.md..."
    cat > DEPLOYMENT.md << 'EOF'
# Deployment Guide

This guide covers deploying the Inventory Management SaaS application to production.

## Prerequisites

- Docker and Docker Compose
- AWS Account (for S3, RDS, ECS)
- Domain name
- SSL certificate

## Production Deployment

### 1. Environment Setup

Create production environment variables:

```bash
# Database
DB_NAME=inventory_saas_prod
DB_USER=inventory_user
DB_PASSWORD=your_secure_password
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=5432

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket

# Security
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Stripe
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### 2. Database Setup

1. Create RDS PostgreSQL instance
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Load sample data: `python manage.py loaddata sample_data.json`

### 3. Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. SSL Certificate

Use Let's Encrypt or AWS Certificate Manager for SSL.

### 6. Monitoring

Set up:
- AWS CloudWatch for logs
- Sentry for error tracking
- Uptime monitoring

## Scaling

- Use AWS ECS Fargate for container orchestration
- Set up RDS read replicas for database scaling
- Use Redis for caching and session storage
- Implement CDN for static files

## Backup Strategy

- Automated RDS snapshots
- S3 versioning for file storage
- Regular database backups
- Configuration backup
EOF
    echo "✅ DEPLOYMENT.md created"
else
    echo "✅ DEPLOYMENT.md already exists"
fi

echo ""
echo "🎉 GitHub preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Initialize git repository: git init"
echo "2. Add all files: git add ."
echo "3. Initial commit: git commit -m 'Initial commit: Inventory Management SaaS'"
echo "4. Add remote: git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "5. Push to GitHub: git push -u origin main"
echo ""
echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "📸 Don't forget to add screenshots to the /screenshots/ folder!"
echo "📚 Update README.md with actual screenshots once added"
echo ""
echo "✨ Ready for GitHub! 🚀"
