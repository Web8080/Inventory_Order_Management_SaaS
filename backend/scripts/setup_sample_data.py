#!/usr/bin/env python
"""
Script to set up sample data for the Inventory Management SaaS
This includes creating sample products with images from Unsplash
"""

import os
import sys
import django
import requests
from io import BytesIO
from PIL import Image
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_saas.settings')
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from tenants.models import Tenant, User
from products.models import Category, Supplier, Product
from orders.models import Order, OrderLine
from inventory.models import StockItem, StockTransaction


def download_image(url, filename):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None


def create_sample_tenant():
    """Create sample tenant and user"""
    tenant, created = Tenant.objects.get_or_create(
        slug="demo-tenant",
        defaults={
            'name': "Demo Company",
            'plan': 'premium'
        }
    )
    
    user, created = User.objects.get_or_create(
        email="demo@example.com",
        defaults={
            'tenant': tenant,
            'role': 'owner',
            'is_tenant_admin': True,
            'is_staff': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
    
    return tenant, user


def create_sample_categories(tenant):
    """Create sample product categories"""
    categories_data = [
        {
            'name': 'Electronics',
            'description': 'Electronic devices and accessories',
            'sort_order': 1,
            'tenant': tenant
        },
        {
            'name': 'Clothing',
            'description': 'Apparel and fashion items',
            'sort_order': 2,
            'tenant': tenant
        },
        {
            'name': 'Home & Garden',
            'description': 'Home improvement and garden supplies',
            'sort_order': 3,
            'tenant': tenant
        },
        {
            'name': 'Sports & Outdoors',
            'description': 'Sports equipment and outdoor gear',
            'sort_order': 4,
            'tenant': tenant
        },
        {
            'name': 'Books',
            'description': 'Books and educational materials',
            'sort_order': 5,
            'tenant': tenant
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            tenant=tenant,
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        print(f"{'Created' if created else 'Found'} category: {category.name}")
    
    return categories


def create_sample_suppliers(tenant):
    """Create sample suppliers"""
    suppliers_data = [
        {
            'name': 'TechSupply Co.',
            'contact_person': 'John Smith',
            'email': 'john@techsupply.com',
            'phone': '+1-555-0123',
            'address': '123 Tech Street, Silicon Valley, CA 94000',
            'website': 'https://techsupply.com',
            'payment_terms': 'Net 30',
            'tenant': tenant
        },
        {
            'name': 'Fashion Forward Ltd.',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah@fashionforward.com',
            'phone': '+1-555-0456',
            'address': '456 Fashion Ave, New York, NY 10001',
            'website': 'https://fashionforward.com',
            'payment_terms': 'Net 15',
            'tenant': tenant
        },
        {
            'name': 'Home Depot Wholesale',
            'contact_person': 'Mike Wilson',
            'email': 'mike@homedepot.com',
            'phone': '+1-555-0789',
            'address': '789 Home Lane, Atlanta, GA 30309',
            'website': 'https://homedepot.com',
            'payment_terms': 'Net 45',
            'tenant': tenant
        }
    ]
    
    suppliers = {}
    for sup_data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            name=sup_data['name'],
            tenant=tenant,
            defaults=sup_data
        )
        suppliers[sup_data['name']] = supplier
        print(f"{'Created' if created else 'Found'} supplier: {supplier.name}")
    
    return suppliers


def create_sample_products(tenant, categories, suppliers):
    """Create sample products with images"""
    
    # Product data with Unsplash image URLs
    products_data = [
        {
            'sku': 'LAPTOP-001',
            'name': 'MacBook Pro 16"',
            'description': 'Apple MacBook Pro with M2 chip, 16GB RAM, 512GB SSD',
            'category': categories['Electronics'],
            'supplier': suppliers['TechSupply Co.'],
            'cost_price': 1800.00,
            'selling_price': 2499.00,
            'reorder_point': 5,
            'reorder_quantity': 20,
            'barcode': '1234567890123',
            'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop'
        },
        {
            'sku': 'PHONE-001',
            'name': 'iPhone 15 Pro',
            'description': 'Apple iPhone 15 Pro with 128GB storage',
            'category': categories['Electronics'],
            'supplier': suppliers['TechSupply Co.'],
            'cost_price': 800.00,
            'selling_price': 999.00,
            'reorder_point': 10,
            'reorder_quantity': 50,
            'barcode': '1234567890124',
            'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&h=600&fit=crop'
        },
        {
            'sku': 'TSHIRT-001',
            'name': 'Cotton T-Shirt',
            'description': 'Premium cotton t-shirt, available in multiple colors',
            'category': categories['Clothing'],
            'supplier': suppliers['Fashion Forward Ltd.'],
            'cost_price': 8.00,
            'selling_price': 24.99,
            'reorder_point': 50,
            'reorder_quantity': 200,
            'barcode': '1234567890125',
            'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=600&fit=crop'
        },
        {
            'sku': 'JEANS-001',
            'name': 'Blue Jeans',
            'description': 'Classic blue denim jeans, various sizes',
            'category': categories['Clothing'],
            'supplier': suppliers['Fashion Forward Ltd.'],
            'cost_price': 25.00,
            'selling_price': 79.99,
            'reorder_point': 30,
            'reorder_quantity': 100,
            'barcode': '1234567890126',
            'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&h=600&fit=crop'
        },
        {
            'sku': 'HAMMER-001',
            'name': 'Claw Hammer',
            'description': 'Professional claw hammer, 16 oz',
            'category': categories['Home & Garden'],
            'supplier': suppliers['Home Depot Wholesale'],
            'cost_price': 12.00,
            'selling_price': 24.99,
            'reorder_point': 20,
            'reorder_quantity': 100,
            'barcode': '1234567890127',
            'image_url': 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop'
        },
        {
            'sku': 'DRILL-001',
            'name': 'Cordless Drill',
            'description': '18V cordless drill with battery and charger',
            'category': categories['Home & Garden'],
            'supplier': suppliers['Home Depot Wholesale'],
            'cost_price': 45.00,
            'selling_price': 89.99,
            'reorder_point': 15,
            'reorder_quantity': 50,
            'barcode': '1234567890128',
            'image_url': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800&h=600&fit=crop'
        },
        {
            'sku': 'BALL-001',
            'name': 'Soccer Ball',
            'description': 'Official size 5 soccer ball',
            'category': categories['Sports & Outdoors'],
            'supplier': suppliers['TechSupply Co.'],
            'cost_price': 15.00,
            'selling_price': 29.99,
            'reorder_point': 25,
            'reorder_quantity': 100,
            'barcode': '1234567890129',
            'image_url': 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=800&h=600&fit=crop'
        },
        {
            'sku': 'BOOK-001',
            'name': 'Python Programming Guide',
            'description': 'Complete guide to Python programming',
            'category': categories['Books'],
            'supplier': suppliers['TechSupply Co.'],
            'cost_price': 20.00,
            'selling_price': 39.99,
            'reorder_point': 10,
            'reorder_quantity': 50,
            'barcode': '1234567890130',
            'image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=600&fit=crop'
        }
    ]
    
    products = {}
    for prod_data in products_data:
        # Download and save image
        image_content = download_image(prod_data['image_url'], f"{prod_data['sku']}.jpg")
        
        # Create product
        product_data = {k: v for k, v in prod_data.items() if k != 'image_url'}
        product_data['tenant'] = tenant
        
        product, created = Product.objects.get_or_create(
            tenant=tenant,
            sku=prod_data['sku'],
            defaults=product_data
        )
        
        # Save image if downloaded successfully
        if image_content and created:
            try:
                # Create a ContentFile from the image data
                image_file = ContentFile(image_content, name=f"{prod_data['sku']}.jpg")
                product.image.save(f"{prod_data['sku']}.jpg", image_file, save=True)
                print(f"Saved image for {product.name}")
            except Exception as e:
                print(f"Error saving image for {product.name}: {e}")
        
        products[prod_data['sku']] = product
        print(f"{'Created' if created else 'Found'} product: {product.name}")
    
    return products


def create_sample_stock(tenant, products):
    """Create sample stock levels"""
    import random
    from inventory.models import Warehouse
    
    # Create default warehouse
    warehouse, created = Warehouse.objects.get_or_create(
        tenant=tenant,
        code='MAIN',
        defaults={
            'name': 'Main Warehouse',
            'address': '123 Main Street, City, State 12345',
            'contact_person': 'Warehouse Manager',
            'phone': '+1-555-0000',
            'email': 'warehouse@example.com',
            'is_active': True,
            'is_default': True
        }
    )
    if created:
        print(f"Created warehouse: {warehouse.name}")
    
    for sku, product in products.items():
        # Create random initial stock
        initial_stock = random.randint(5, 100)
        
        stock_item, created = StockItem.objects.get_or_create(
            tenant=tenant,
            product=product,
            warehouse=warehouse,
            defaults={
                'quantity': initial_stock,
                'reserved_quantity': 0
            }
        )
        
        if created:
            # Create initial stock transaction
            StockTransaction.objects.create(
                tenant=tenant,
                product=product,
                warehouse=warehouse,
                transaction_type='in',
                quantity=initial_stock,
                reason='adjustment',
                reference_type='initial_setup',
                notes=f'Initial stock setup for {product.name}'
            )
            print(f"Created stock for {product.name}: {initial_stock} units")


def create_sample_orders(tenant, products):
    """Create sample orders"""
    import random
    from datetime import datetime, timedelta
    
    # Create some sample orders
    orders_data = [
        {
            'order_number': 'SO-2024-001',
            'order_type': 'sale',
            'status': 'fulfilled',
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'total_amount': 0  # Will be calculated
        },
        {
            'order_number': 'SO-2024-002',
            'order_type': 'sale',
            'status': 'pending',
            'customer_name': 'Jane Smith',
            'customer_email': 'jane@example.com',
            'total_amount': 0
        },
        {
            'order_number': 'PO-2024-001',
            'order_type': 'purchase',
            'status': 'fulfilled',
            'supplier_name': 'TechSupply Co.',
            'total_amount': 0
        }
    ]
    
    for order_data in orders_data:
        order, created = Order.objects.get_or_create(
            tenant=tenant,
            order_number=order_data['order_number'],
            defaults={
                'order_type': order_data['order_type'],
                'status': order_data['status'],
                'customer_name': order_data.get('customer_name'),
                'customer_email': order_data.get('customer_email'),
                'supplier_name': order_data.get('supplier_name'),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 30))
            }
        )
        
        if created:
            # Add random order lines
            num_lines = random.randint(1, 3)
            selected_products = random.sample(list(products.values()), num_lines)
            
            total_amount = 0
            for product in selected_products:
                quantity = random.randint(1, 5)
                unit_price = product.selling_price if order.order_type == 'sale' else product.cost_price
                line_total = quantity * unit_price
                total_amount += line_total
                
                OrderLine.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
            
            order.total_amount = total_amount
            order.save()
            
            print(f"Created order: {order.order_number} - ${total_amount:.2f}")


def main():
    """Main function to set up all sample data"""
    print("Setting up sample data for Inventory Management SaaS...")
    
    # Create tenant and user
    print("\n1. Creating tenant and user...")
    tenant, user = create_sample_tenant()
    print(f"Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"User: {user.email} (ID: {user.id})")
    
    # Create categories
    print("\n2. Creating categories...")
    categories = create_sample_categories(tenant)
    
    # Create suppliers
    print("\n3. Creating suppliers...")
    suppliers = create_sample_suppliers(tenant)
    
    # Create products with images
    print("\n4. Creating products with images...")
    products = create_sample_products(tenant, categories, suppliers)
    
    # Create stock levels
    print("\n5. Creating stock levels...")
    create_sample_stock(tenant, products)
    
    # Create sample orders
    print("\n6. Creating sample orders...")
    # create_sample_orders(tenant, products)  # Skip for now
    
    print("\n✅ Sample data setup completed!")
    print(f"\nDemo credentials:")
    print(f"Email: demo@example.com")
    print(f"Password: demo123")
    print(f"Tenant: Demo Company")
    
    print(f"\nYou can now:")
    print(f"1. Start the development server: python manage.py runserver")
    print(f"2. Visit: http://localhost:8000/admin")
    print(f"3. Login with the demo credentials above")
    print(f"4. Visit: http://localhost:8000/api/docs/ for API documentation")


if __name__ == '__main__':
    main()
