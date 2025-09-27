# Contributing to Inventory Management SaaS

Thank you for your interest in contributing to the Inventory Management SaaS project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@inventory-saas.com](mailto:conduct@inventory-saas.com).

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (recommended for development)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)
- **Git** (for version control)
- **PostgreSQL 14+** (if not using Docker)
- **MongoDB 6+** (if not using Docker)
- **Redis 6+** (if not using Docker)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/inventory-saas.git
   cd inventory-saas
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/originalowner/inventory-saas.git
   ```

## 🛠️ Development Setup

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# ML Service: http://localhost:8001
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### ML Service Setup

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

## 📝 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues and improve stability
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize code and improve performance
- **Security**: Fix security vulnerabilities
- **UI/UX**: Improve user interface and experience

### Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   # or
   git checkout -b docs/your-documentation-update
   ```

2. **Make your changes** following our coding standards

3. **Test your changes** thoroughly

4. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add new inventory tracking feature"
   # or
   git commit -m "fix: resolve authentication issue"
   # or
   git commit -m "docs: update API documentation"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## 🎨 Code Style

### Python (Backend)

We use the following tools for Python code formatting and linting:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .

# Type checking
mypy .
```

### TypeScript/JavaScript (Frontend)

We use the following tools for frontend code:

- **Prettier** for code formatting
- **ESLint** for linting
- **TypeScript** for type checking

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Code Style Guidelines

#### Python

- Use **PEP 8** style guide
- Maximum line length: **88 characters** (Black default)
- Use **type hints** for function parameters and return values
- Use **docstrings** for classes and functions
- Use **meaningful variable names**

```python
def calculate_inventory_value(
    products: List[Product], 
    warehouse_id: str
) -> Decimal:
    """
    Calculate total inventory value for products in a warehouse.
    
    Args:
        products: List of products to calculate value for
        warehouse_id: ID of the warehouse
        
    Returns:
        Total inventory value as Decimal
    """
    total_value = Decimal('0')
    for product in products:
        if product.warehouse_id == warehouse_id:
            total_value += product.quantity * product.cost_price
    return total_value
```

#### TypeScript/React

- Use **functional components** with hooks
- Use **TypeScript interfaces** for props and state
- Use **meaningful component and variable names**
- Use **proper error handling**

```typescript
interface ProductCardProps {
  product: Product;
  onEdit: (product: Product) => void;
  onDelete: (productId: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onEdit,
  onDelete,
}) => {
  const handleEdit = useCallback(() => {
    onEdit(product);
  }, [product, onEdit]);

  const handleDelete = useCallback(() => {
    onDelete(product.id);
  }, [product.id, onDelete]);

  return (
    <Card>
      <CardBody>
        <Heading size="md">{product.name}</Heading>
        <Text>SKU: {product.sku}</Text>
        <Text>Stock: {product.current_stock}</Text>
        <Button onClick={handleEdit}>Edit</Button>
        <Button onClick={handleDelete} colorScheme="red">
          Delete
        </Button>
      </CardBody>
    </Card>
  );
};
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_products.py

# Run with verbose output
pytest -v
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run tests in watch mode
npm run test:watch
```

### Test Guidelines

- **Write tests** for new features and bug fixes
- **Maintain test coverage** above 80%
- **Use descriptive test names**
- **Test edge cases** and error conditions
- **Mock external dependencies**

```python
# Backend test example
def test_create_product_with_valid_data():
    """Test creating a product with valid data."""
    tenant = TenantFactory()
    user = UserFactory(tenant=tenant)
    
    product_data = {
        'sku': 'TEST-001',
        'name': 'Test Product',
        'cost_price': 10.00,
        'selling_price': 15.00,
    }
    
    response = client.post(
        '/api/products/',
        data=product_data,
        headers={'Authorization': f'Bearer {user.access_token}'}
    )
    
    assert response.status_code == 201
    assert response.data['sku'] == 'TEST-001'
    assert Product.objects.filter(sku='TEST-001').exists()
```

```typescript
// Frontend test example
describe('ProductCard', () => {
  const mockProduct: Product = {
    id: '1',
    sku: 'TEST-001',
    name: 'Test Product',
    current_stock: 10,
  };

  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  it('renders product information correctly', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('SKU: TEST-001')).toBeInTheDocument();
    expect(screen.getByText('Stock: 10')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    render(
      <ProductCard
        product={mockProduct}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockProduct);
  });
});
```

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   ```

2. **Check code style**:
   ```bash
   # Backend
   cd backend && black --check . && isort --check-only . && flake8 .
   
   # Frontend
   cd frontend && npm run lint
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #issue_number
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** in staging environment
4. **Approval** from at least one maintainer
5. **Merge** to main branch

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the bug
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, browser, version)
5. **Screenshots** if applicable
6. **Error logs** if available

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. macOS, Windows, Linux]
 - Browser: [e.g. Chrome, Firefox, Safari]
 - Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## 📚 Documentation

### Documentation Guidelines

- **Keep documentation up to date** with code changes
- **Use clear and concise language**
- **Include code examples** where helpful
- **Add screenshots** for UI documentation
- **Follow the existing documentation style**

### Types of Documentation

- **API Documentation**: Update OpenAPI/Swagger specs
- **User Documentation**: Update user guides and tutorials
- **Developer Documentation**: Update architecture and setup guides
- **Code Documentation**: Add docstrings and comments

## 🔒 Security

### Security Guidelines

- **Never commit secrets** or sensitive information
- **Use environment variables** for configuration
- **Follow security best practices** in code
- **Report security vulnerabilities** privately

### Reporting Security Issues

If you discover a security vulnerability, please report it privately:

1. **Email**: security@inventory-saas.com
2. **Include**: Detailed description and steps to reproduce
3. **Do not** create public issues for security vulnerabilities

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] Security review completed

## 🤔 Questions?

If you have questions about contributing:

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For specific problems
- **Email**: contributors@inventory-saas.com
- **Discord**: Join our community server

## 🙏 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Project documentation**

Thank you for contributing to Inventory Management SaaS! 🚀
