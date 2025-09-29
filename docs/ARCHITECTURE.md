# Inventory Management SaaS - Architecture Documentation

## Overview

This is a comprehensive multi-tenant inventory and order management SaaS platform built with modern technologies and best practices. The system provides inventory tracking, order management, demand forecasting using ML, and third-party integrations.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   Django API    │    │   ML Service    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   PostgreSQL    │    │   MongoDB       │
│   (CDN)         │    │   (Primary DB)  │    │   (Events)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis         │
                       │   (Cache/Queue) │
                       └─────────────────┘
```

### Technology Stack

#### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Chakra UI** for component library
- **React Router** for routing
- **Zustand** for state management
- **React Query** for data fetching
- **React Hook Form** with Yup validation

#### Backend
- **Django 4.2** with Django REST Framework
- **PostgreSQL** for primary database
- **MongoDB** for event logs and time-series data
- **Redis** for caching and Celery task queue
- **Celery** for background tasks
- **JWT** for authentication
- **Stripe** for payments

#### ML Pipeline
- **FastAPI** for ML service
- **Pandas** for data processing
- **Scikit-learn** for machine learning
- **XGBoost** for gradient boosting
- **Prophet** for time series forecasting

#### Infrastructure
- **AWS** for cloud hosting
- **Docker** for containerization
- **ECS Fargate** for container orchestration
- **RDS** for managed PostgreSQL
- **ElastiCache** for managed Redis
- **S3** for file storage
- **CloudFront** for CDN

## Multi-Tenant Architecture

### Row-Level Tenancy

The system uses row-level tenancy where all tenant data is stored in the same database with a `tenant_id` field on each record. This approach provides:

- **Cost Efficiency**: Single database instance
- **Easier Maintenance**: One database to manage
- **Simpler Scaling**: Horizontal scaling through read replicas
- **Data Isolation**: Application-level enforcement

### Tenant Isolation

```python
# Example of tenant-aware model
class Product(TenantAwareModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    # ... other fields
```

### Security Measures

1. **Middleware Enforcement**: All requests are filtered by tenant
2. **Database Constraints**: Unique constraints include tenant_id
3. **API Permissions**: Role-based access control per tenant
4. **Audit Logging**: All actions logged with tenant context

## Database Design

### Core Tables

#### Tenants
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'clerk',
    is_tenant_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Products
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    cost_price DECIMAL(10,2) DEFAULT 0,
    selling_price DECIMAL(10,2) DEFAULT 0,
    reorder_point INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, sku)
);
```

#### Orders
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    total_amount DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Indexing Strategy

```sql
-- Tenant-based indexes for performance
CREATE INDEX idx_products_tenant_sku ON products(tenant_id, sku);
CREATE INDEX idx_orders_tenant_date ON orders(tenant_id, created_at);
CREATE INDEX idx_stock_items_tenant_product ON stock_items(tenant_id, product_id);

-- Composite indexes for common queries
CREATE INDEX idx_orders_tenant_status ON orders(tenant_id, status);
CREATE INDEX idx_products_tenant_active ON products(tenant_id, is_active);
```

## API Design

### RESTful Endpoints

#### Authentication
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/refresh/        # Token refresh
GET  /api/auth/profile/        # User profile
PUT  /api/auth/profile/        # Update profile
```

#### Products
```
GET    /api/products/          # List products
POST   /api/products/          # Create product
GET    /api/products/{id}/     # Get product
PUT    /api/products/{id}/     # Update product
DELETE /api/products/{id}/     # Delete product
```

#### Orders
```
GET    /api/orders/            # List orders
POST   /api/orders/            # Create order
GET    /api/orders/{id}/       # Get order
PUT    /api/orders/{id}/       # Update order
POST   /api/orders/{id}/fulfill/ # Fulfill order
```

#### Inventory
```
GET    /api/inventory/stock-items/     # List stock items
POST   /api/inventory/adjust/          # Adjust stock
GET    /api/inventory/low-stock/       # Get low stock alerts
GET    /api/inventory/warehouses/      # List warehouses
```

### API Documentation

The API is documented using OpenAPI 3.0 (Swagger) and can be accessed at:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## ML Pipeline

### Demand Forecasting

The ML pipeline provides demand forecasting using multiple algorithms:

1. **XGBoost**: For products with sufficient historical data
2. **Random Forest**: For products with moderate data
3. **Prophet**: For time series with seasonality
4. **Simple Average**: For products with limited data

### Feature Engineering

```python
def create_features(df):
    # Time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek
    
    # Lag features
    for lag in [1, 7, 14, 30]:
        df[f'lag_{lag}'] = df['quantity'].shift(lag)
    
    # Rolling statistics
    for window in [7, 14, 30]:
        df[f'rolling_mean_{window}'] = df['quantity'].rolling(window).mean()
    
    return df
```

### Model Training

```python
# Training pipeline
def train_models(tenant_id, product_ids=None):
    # Get historical data
    data = get_historical_sales(tenant_id, product_ids)
    
    # Train global model
    global_model = train_global_model(data)
    
    # Train product-specific models
    for product_id in data['product_id'].unique():
        product_data = data[data['product_id'] == product_id]
        model = train_product_model(product_data)
        save_model(product_id, model)
```

## Security

### Authentication & Authorization

1. **JWT Tokens**: Short-lived access tokens with refresh tokens
2. **Role-Based Access**: Owner, Manager, Clerk roles
3. **Tenant Isolation**: All data filtered by tenant
4. **API Rate Limiting**: Prevent abuse

### Data Protection

1. **Encryption at Rest**: Database and S3 encryption
2. **Encryption in Transit**: HTTPS/TLS everywhere
3. **Secrets Management**: AWS Secrets Manager
4. **Input Validation**: Comprehensive validation on all inputs

### Compliance

1. **GDPR**: Data export and deletion capabilities
2. **SOC 2**: Security controls and monitoring
3. **Audit Logging**: All actions logged with context

## Deployment

### Infrastructure as Code

The infrastructure is defined using Terraform:

```hcl
# VPC with public/private subnets
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# ECS Fargate cluster
resource "aws_ecs_cluster" "main" {
  name = "inventory-saas"
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  engine = "postgres"
  instance_class = "db.t3.micro"
}
```

### CI/CD Pipeline

GitHub Actions provides automated CI/CD:

1. **Testing**: Unit tests, integration tests, linting
2. **Security Scanning**: Trivy vulnerability scanning
3. **Build**: Docker image creation
4. **Deploy**: ECS service updates

### Monitoring

1. **CloudWatch**: Application and infrastructure metrics
2. **Sentry**: Error tracking and performance monitoring
3. **Custom Dashboards**: Business metrics and KPIs

## Scalability

### Horizontal Scaling

1. **ECS Fargate**: Auto-scaling based on CPU/memory
2. **RDS Read Replicas**: Read scaling for database
3. **ElastiCache**: Distributed caching
4. **CloudFront**: Global CDN

### Performance Optimization

1. **Database Indexing**: Optimized queries
2. **Caching Strategy**: Redis for frequently accessed data
3. **API Pagination**: Efficient data loading
4. **Background Tasks**: Celery for heavy operations

## Development Workflow

### Local Development

```bash
# Start all services
docker-compose up --build

# Run tests
cd backend && python manage.py test
cd frontend && npm test

# Run linting
cd backend && flake8 . && black . && isort .
cd frontend && npm run lint
```

### Code Quality

1. **Type Safety**: TypeScript for frontend, type hints for Python
2. **Code Formatting**: Black, isort for Python; Prettier for TypeScript
3. **Linting**: Flake8, ESLint
4. **Testing**: Pytest, Jest with high coverage requirements

## Future Enhancements

### Planned Features

1. **Advanced ML Models**: LSTM, Transformer models
2. **Real-time Updates**: WebSocket connections
3. **Mobile App**: React Native application
4. **Advanced Analytics**: Business intelligence dashboard
5. **Multi-warehouse**: Complex warehouse management
6. **Barcode Scanning**: Mobile barcode integration

### Technical Improvements

1. **Microservices**: Break down monolithic backend
2. **Event Sourcing**: CQRS pattern implementation
3. **GraphQL**: Alternative to REST API
4. **Kubernetes**: Container orchestration
5. **Service Mesh**: Istio for service communication

## Conclusion

This architecture provides a solid foundation for a scalable, secure, and maintainable inventory management SaaS platform. The multi-tenant design ensures cost efficiency while maintaining data isolation, and the ML pipeline provides valuable business insights through demand forecasting.

The technology choices prioritize developer productivity, system reliability, and business value delivery while maintaining the flexibility to evolve with changing requirements.

