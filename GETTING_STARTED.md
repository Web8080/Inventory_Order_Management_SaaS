# Getting Started with Inventory Management SaaS

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- MongoDB 6+
- Redis 6+

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd Inventory_Order_Management_SaaS
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose up --build

# Or start individual services
docker-compose up db mongodb redis  # Start databases
docker-compose up backend           # Start Django backend
docker-compose up frontend          # Start React frontend
docker-compose up ml-service        # Start ML service
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **ML Service**: http://localhost:8001
- **Admin Panel**: http://localhost:8000/admin

### 5. Demo Credentials

- **Demo Tenant**: acme-demo
- **Email**: owner@acme.test
- **Password**: Passw0rd!

## 🏗️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### ML Pipeline Development

```bash
cd ml

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start ML service
uvicorn main:app --reload --port 8001
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=. --cov-report=html  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## 📊 Key Features

### ✅ Implemented

- **Multi-tenant Architecture**: Row-level tenancy with tenant isolation
- **User Management**: Role-based access control (Owner, Manager, Clerk)
- **Product Catalog**: SKU management, categories, suppliers
- **Inventory Tracking**: Stock levels, warehouses, transactions
- **Order Management**: Sales and purchase orders with fulfillment
- **ML Forecasting**: Demand prediction using XGBoost and Prophet
- **API Documentation**: OpenAPI/Swagger documentation
- **Authentication**: JWT-based auth with refresh tokens
- **Docker Support**: Full containerization for development and production

### 🚧 In Progress

- **Third-party Integrations**: Shopify, WooCommerce webhooks
- **Advanced Analytics**: Business intelligence dashboard
- **Real-time Updates**: WebSocket connections
- **Mobile App**: React Native application

## 🏛️ Architecture

### Technology Stack

- **Frontend**: React 18, TypeScript, Chakra UI, Zustand
- **Backend**: Django 4.2, DRF, PostgreSQL, Redis, Celery
- **ML**: FastAPI, Pandas, Scikit-learn, XGBoost, Prophet
- **Infrastructure**: AWS, Docker, ECS Fargate, RDS, S3

### Database Design

- **PostgreSQL**: Primary relational data with multi-tenant rows
- **MongoDB**: Event logs, audit trails, time-series data
- **Redis**: Caching, session storage, Celery task queue

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/inventory_saas
MONGODB_URL=mongodb://localhost:27017/inventory_saas
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# AWS (for production)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🚀 Deployment

### AWS Deployment

```bash
cd deployment/aws

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Monitoring

### Application Monitoring

- **Sentry**: Error tracking and performance monitoring
- **CloudWatch**: AWS infrastructure metrics
- **Custom Dashboards**: Business KPIs and metrics

### Logging

- **Structured Logging**: JSON format for easy parsing
- **Log Aggregation**: Centralized logging with ELK stack
- **Audit Trails**: All user actions logged with context

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens**: Short-lived access tokens with refresh
- **Role-Based Access**: Granular permissions per tenant
- **Tenant Isolation**: Application-level data separation
- **API Rate Limiting**: Prevent abuse and DoS attacks

### Data Protection

- **Encryption at Rest**: Database and file storage encryption
- **Encryption in Transit**: HTTPS/TLS everywhere
- **Secrets Management**: AWS Secrets Manager integration
- **Input Validation**: Comprehensive validation on all inputs

## 📚 Documentation

- **API Documentation**: `/api/docs/` (Swagger UI)
- **Architecture Guide**: `docs/ARCHITECTURE.md`
- **Deployment Guide**: `deployment/README.md`
- **ML Pipeline Guide**: `ml/README.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- **Code Style**: Follow Black (Python) and Prettier (TypeScript)
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update docs for new features
- **Security**: Follow security best practices

## 📞 Support

- **Issues**: Create GitHub issues for bugs and feature requests
- **Documentation**: Check the docs folder for detailed guides
- **Community**: Join our Discord server for discussions

## 🎯 Roadmap

### Q1 2024
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Real-time inventory updates
- [ ] Mobile application (React Native)

### Q2 2024
- [ ] Advanced analytics dashboard
- [ ] Multi-warehouse support
- [ ] Barcode scanning integration

### Q3 2024
- [ ] Microservices architecture
- [ ] GraphQL API
- [ ] Advanced reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Coding! 🚀**

For more detailed information, check out the [Architecture Documentation](docs/ARCHITECTURE.md).
