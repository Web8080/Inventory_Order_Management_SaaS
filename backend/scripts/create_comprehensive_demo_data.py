#!/usr/bin/env python
"""
Comprehensive Demo Data Creator for Multi-Tenant Inventory SaaS
Creates multiple tenants with extensive data to showcase the platform
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, User, TenantSettings
from products.models import Category, Supplier, Product, ProductVariant, ProductImage
from inventory.models import Warehouse, StockItem, StockTransaction
from orders.models import Order, OrderLine, OrderStatusHistory
from integrations.models import Integration

User = get_user_model()

# Sample data for different business types
BUSINESS_DATA = [
    {
        'name': 'TechGear Electronics',
        'domain': 'techgear.com',
        'industry': 'Electronics',
        'description': 'Premium electronics and gadgets retailer',
        'products': [
            {'name': 'iPhone 15 Pro', 'sku': 'IPH15P-256', 'price': 999.99, 'category': 'Smartphones'},
            {'name': 'MacBook Pro M3', 'sku': 'MBP-M3-14', 'price': 1999.99, 'category': 'Laptops'},
            {'name': 'AirPods Pro', 'sku': 'APP-2ND', 'price': 249.99, 'category': 'Audio'},
            {'name': 'iPad Air', 'sku': 'IPA-5TH-64', 'price': 599.99, 'category': 'Tablets'},
            {'name': 'Apple Watch Series 9', 'sku': 'AW9-45MM', 'price': 429.99, 'category': 'Wearables'},
            {'name': 'Samsung Galaxy S24', 'sku': 'SGS24-256', 'price': 799.99, 'category': 'Smartphones'},
            {'name': 'Dell XPS 13', 'sku': 'DX13-512', 'price': 1299.99, 'category': 'Laptops'},
            {'name': 'Sony WH-1000XM5', 'sku': 'SWH-1000XM5', 'price': 399.99, 'category': 'Audio'},
        ]
    },
    {
        'name': 'Fashion Forward',
        'domain': 'fashionforward.com',
        'industry': 'Fashion',
        'description': 'Trendy clothing and accessories',
        'products': [
            {'name': 'Designer Jeans', 'sku': 'DJ-32-BLUE', 'price': 89.99, 'category': 'Clothing'},
            {'name': 'Cotton T-Shirt', 'sku': 'CTS-M-WHT', 'price': 24.99, 'category': 'Clothing'},
            {'name': 'Leather Jacket', 'sku': 'LJ-L-BLK', 'price': 199.99, 'category': 'Outerwear'},
            {'name': 'Running Shoes', 'sku': 'RS-10-WHT', 'price': 129.99, 'category': 'Footwear'},
            {'name': 'Handbag', 'sku': 'HB-M-BRN', 'price': 79.99, 'category': 'Accessories'},
            {'name': 'Sunglasses', 'sku': 'SG-BLK', 'price': 149.99, 'category': 'Accessories'},
            {'name': 'Dress', 'sku': 'DR-M-RED', 'price': 69.99, 'category': 'Clothing'},
            {'name': 'Sneakers', 'sku': 'SN-9-BLK', 'price': 99.99, 'category': 'Footwear'},
        ]
    },
    {
        'name': 'Home & Garden Plus',
        'domain': 'homegardenplus.com',
        'industry': 'Home & Garden',
        'description': 'Everything for your home and garden',
        'products': [
            {'name': 'Garden Hose', 'sku': 'GH-50FT', 'price': 39.99, 'category': 'Garden Tools'},
            {'name': 'Plant Pot Set', 'sku': 'PPS-3PC', 'price': 29.99, 'category': 'Planters'},
            {'name': 'LED Light Bulbs', 'sku': 'LED-4PK', 'price': 19.99, 'category': 'Lighting'},
            {'name': 'Kitchen Knife Set', 'sku': 'KKS-6PC', 'price': 79.99, 'category': 'Kitchen'},
            {'name': 'Throw Pillows', 'sku': 'TP-2PC', 'price': 34.99, 'category': 'Decor'},
            {'name': 'Garden Seeds', 'sku': 'GS-MIX', 'price': 9.99, 'category': 'Seeds'},
            {'name': 'Storage Bins', 'sku': 'SB-3PC', 'price': 24.99, 'category': 'Storage'},
            {'name': 'Candles', 'sku': 'CND-6PK', 'price': 14.99, 'category': 'Decor'},
        ]
    },
    {
        'name': 'Sports & Fitness Hub',
        'domain': 'sportsfitnesshub.com',
        'industry': 'Sports & Fitness',
        'description': 'Professional sports and fitness equipment',
        'products': [
            {'name': 'Yoga Mat', 'sku': 'YM-PRO', 'price': 49.99, 'category': 'Fitness'},
            {'name': 'Dumbbells Set', 'sku': 'DS-20LB', 'price': 89.99, 'category': 'Weights'},
            {'name': 'Running Shorts', 'sku': 'RS-M-BLK', 'price': 34.99, 'category': 'Activewear'},
            {'name': 'Tennis Racket', 'sku': 'TR-PRO', 'price': 149.99, 'category': 'Tennis'},
            {'name': 'Basketball', 'sku': 'BB-OFF', 'price': 29.99, 'category': 'Basketball'},
            {'name': 'Protein Powder', 'sku': 'PP-5LB', 'price': 59.99, 'category': 'Supplements'},
            {'name': 'Resistance Bands', 'sku': 'RB-SET', 'price': 19.99, 'category': 'Fitness'},
            {'name': 'Golf Clubs Set', 'sku': 'GCS-14PC', 'price': 299.99, 'category': 'Golf'},
        ]
    },
    {
        'name': 'Bookworm Central',
        'domain': 'bookwormcentral.com',
        'industry': 'Books & Media',
        'description': 'Books, e-books, and educational materials',
        'products': [
            {'name': 'Programming Book', 'sku': 'PB-PYTHON', 'price': 49.99, 'category': 'Technology'},
            {'name': 'Fiction Novel', 'sku': 'FN-MYST', 'price': 16.99, 'category': 'Fiction'},
            {'name': 'Cookbook', 'sku': 'CB-ITAL', 'price': 24.99, 'category': 'Cooking'},
            {'name': 'Children\'s Book', 'sku': 'CB-FAIRY', 'price': 12.99, 'category': 'Children'},
            {'name': 'Business Book', 'sku': 'BB-LEAD', 'price': 19.99, 'category': 'Business'},
            {'name': 'History Book', 'sku': 'HB-WW2', 'price': 29.99, 'category': 'History'},
            {'name': 'Science Book', 'sku': 'SB-PHYS', 'price': 39.99, 'category': 'Science'},
            {'name': 'Art Book', 'sku': 'AB-REN', 'price': 34.99, 'category': 'Art'},
        ]
    }
]

def create_tenant_data(business_data):
    """Create a complete tenant with all related data"""
    
    # Create tenant
    tenant = Tenant.objects.create(
        name=business_data['name'],
        slug=business_data['domain'].replace('.com', '').replace('.', '-'),
        plan='premium',
        is_active=True
    )
    
    # Create tenant settings
    TenantSettings.objects.create(
        tenant=tenant,
        low_stock_threshold=10,
        auto_reorder_enabled=True,
        ml_forecasting_enabled=True,
        email_notifications=True,
        low_stock_alerts=True,
        order_notifications=True
    )
    
    # Create users for this tenant
    owner = User.objects.create_user(
        username=f"{business_data['name'].lower().replace(' ', '')}_owner",
        email=f"owner@{business_data['domain']}",
        password='demo123',
        first_name='John',
        last_name='Owner',
        tenant=tenant,
        role='owner',
        is_tenant_admin=True,
        is_active=True
    )
    
    manager = User.objects.create_user(
        username=f"{business_data['name'].lower().replace(' ', '')}_manager",
        email=f"manager@{business_data['domain']}",
        password='demo123',
        first_name='Jane',
        last_name='Manager',
        tenant=tenant,
        role='manager',
        is_active=True
    )
    
    clerk = User.objects.create_user(
        username=f"{business_data['name'].lower().replace(' ', '')}_clerk",
        email=f"clerk@{business_data['domain']}",
        password='demo123',
        first_name='Bob',
        last_name='Clerk',
        tenant=tenant,
        role='clerk',
        is_active=True
    )
    
    # Create warehouse
    warehouse = Warehouse.objects.create(
        tenant=tenant,
        name=f"{business_data['name']} Main Warehouse",
        code='MAIN',
        address=f"123 {business_data['industry']} Street, City, State 12345",
        contact_person='Warehouse Manager',
        phone='555-0123',
        email=f'warehouse@{business_data["domain"]}',
        is_active=True,
        is_default=True
    )
    
    # Create categories
    categories = {}
    for product_data in business_data['products']:
        category_name = product_data['category']
        if category_name not in categories:
            category = Category.objects.create(
                tenant=tenant,
                name=category_name,
                description=f"{category_name} products for {business_data['name']}",
                is_active=True
            )
            categories[category_name] = category
    
    # Create supplier
    supplier = Supplier.objects.create(
        tenant=tenant,
        name=f"{business_data['name']} Supplier",
        contact_person='Supplier Manager',
        email=f'supplier@{business_data["domain"]}',
        phone='555-0456',
        address=f"456 Supplier Ave, City, State 12345",
        is_active=True
    )
    
    # Create products and variants
    products = []
    for product_data in business_data['products']:
        product = Product.objects.create(
            tenant=tenant,
            name=product_data['name'],
            sku=product_data['sku'],
            description=f"High-quality {product_data['name'].lower()} from {business_data['name']}",
            category=categories[product_data['category']],
            supplier=supplier,
            cost_price=Decimal(str(product_data['price'] * 0.6)),  # 60% of selling price
            selling_price=Decimal(str(product_data['price'])),
            reorder_point=random.randint(5, 20),
            reorder_quantity=random.randint(20, 100),
            is_active=True
        )
        
        # Create variant
        variant = ProductVariant.objects.create(
            tenant=tenant,
            product=product,
            name='Default',
            sku=f"{product_data['sku']}-VAR",
            selling_price=Decimal(str(product_data['price'])),
            cost_price=Decimal(str(product_data['price'] * 0.6)),
            reorder_point=random.randint(5, 20),
            reorder_quantity=random.randint(20, 100),
            is_active=True
        )
        
        # Create stock item
        initial_quantity = random.randint(50, 200)
        stock_item = StockItem.objects.create(
            tenant=tenant,
            product=product,
            variant=variant,
            warehouse=warehouse,
            quantity=initial_quantity,
            reserved_quantity=random.randint(0, 10)
        )
        
        products.append({
            'product': product,
            'variant': variant,
            'stock_item': stock_item,
            'price': product_data['price']
        })
    
    # Create orders (sales and purchases)
    orders_created = 0
    
    # Create sales orders
    for i in range(random.randint(15, 30)):
        order_date = datetime.now() - timedelta(days=random.randint(1, 90))
        
        order = Order.objects.create(
            tenant=tenant,
            order_number=f"SO-{tenant.id.hex[:8].upper()}-{i+1:04d}",
            order_type='sale',
            status=random.choice(['pending', 'processing', 'shipped', 'delivered']),
            order_date=order_date,
            customer_name=f"Customer {i+1}",
            customer_email=f"customer{i+1}@{business_data['domain']}",
            customer_address=f"{i+1} Customer Street, City, State 12345",
            shipping_address=f"{i+1} Customer Street, City, State 12345",
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            shipping_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('0.00'),
            payment_status=random.choice(['pending', 'paid', 'failed']),
            created_by=random.choice([owner, manager, clerk])
        )
        
        # Create order lines
        num_lines = random.randint(1, 5)
        selected_products = random.sample(products, min(num_lines, len(products)))
        
        order_total = Decimal('0.00')
        for product_data in selected_products:
            quantity = random.randint(1, 10)
            unit_price = product_data['price']
            line_total = Decimal(str(quantity * unit_price))
            
            OrderLine.objects.create(
                tenant=tenant,
                order=order,
                product=product_data['product'],
                variant=product_data['variant'],
                quantity=quantity,
                unit_price=Decimal(str(unit_price)),
                line_total=line_total
            )
            
            order_total += line_total
            
            # Update stock
            product_data['stock_item'].quantity -= quantity
            product_data['stock_item'].save()
            
            # Create stock transaction
            StockTransaction.objects.create(
                tenant=tenant,
                product=product_data['product'],
                variant=product_data['variant'],
                warehouse=warehouse,
                transaction_type='out',
                quantity=-quantity,  # Negative for out
                reason='sale',
                reference_id=order.id,
                reference_type='order',
                notes=f"Sale order {order.order_number}",
                user=random.choice([owner, manager, clerk])
            )
        
        # Update order totals
        tax_amount = order_total * Decimal('0.08')  # 8% tax
        shipping_amount = Decimal('9.99') if order_total < 50 else Decimal('0.00')
        order.subtotal = order_total
        order.tax_amount = tax_amount
        order.shipping_amount = shipping_amount
        order.total_amount = order_total + tax_amount + shipping_amount
        order.save()
        
        # Create order status history
        OrderStatusHistory.objects.create(
            tenant=tenant,
            order=order,
            to_status=order.status,
            notes=f"Order {order.status}",
            changed_by=random.choice([owner, manager, clerk])
        )
        
        orders_created += 1
    
    # Create purchase orders
    for i in range(random.randint(5, 15)):
        order_date = datetime.now() - timedelta(days=random.randint(1, 60))
        
        order = Order.objects.create(
            tenant=tenant,
            order_number=f"PO-{tenant.id.hex[:8].upper()}-{i+1:04d}",
            order_type='purchase',
            status=random.choice(['pending', 'ordered', 'received']),
            order_date=order_date,
            supplier=supplier,
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            shipping_amount=Decimal('0.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('0.00'),
            payment_status=random.choice(['pending', 'paid']),
            created_by=random.choice([owner, manager])
        )
        
        # Create order lines
        num_lines = random.randint(1, 3)
        selected_products = random.sample(products, min(num_lines, len(products)))
        
        order_total = Decimal('0.00')
        for product_data in selected_products:
            quantity = random.randint(20, 100)
            unit_price = product_data['price'] * 0.6  # Cost price
            line_total = Decimal(str(quantity * unit_price))
            
            OrderLine.objects.create(
                tenant=tenant,
                order=order,
                product=product_data['product'],
                variant=product_data['variant'],
                quantity=quantity,
                unit_price=Decimal(str(unit_price)),
                line_total=line_total
            )
            
            order_total += line_total
            
            # Update stock if received
            if order.status == 'received':
                product_data['stock_item'].quantity += quantity
                product_data['stock_item'].save()
                
                # Create stock transaction
                StockTransaction.objects.create(
                    tenant=tenant,
                    product=product_data['product'],
                    variant=product_data['variant'],
                    warehouse=warehouse,
                    transaction_type='in',
                    quantity=quantity,  # Positive for in
                    reason='purchase',
                    reference_id=order.id,
                    reference_type='order',
                    notes=f"Purchase order {order.order_number}",
                    user=random.choice([owner, manager])
                )
        
        # Update order totals
        order.subtotal = order_total
        order.total_amount = order_total
        order.save()
        
        orders_created += 1
    
    # Create integration
    Integration.objects.create(
        tenant=tenant,
        name='Shopify Integration',
        integration_type='shopify',
        is_enabled=True,
        config={
            'shop_domain': business_data['domain'],
            'api_version': '2023-10',
            'webhook_secret': 'demo_webhook_secret'
        }
    )
    
    print(f"✅ Created tenant: {business_data['name']}")
    print(f"   - Users: 3 (owner, manager, clerk)")
    print(f"   - Products: {len(products)}")
    print(f"   - Orders: {orders_created}")
    print(f"   - Warehouse: 1")
    print(f"   - Integration: 1")
    
    return tenant

def main():
    """Create comprehensive demo data"""
    print("🚀 Creating comprehensive demo data for multi-tenant showcase...")
    print()
    
    # Clear existing demo data (optional)
    print("🧹 Clearing existing demo data...")
    Tenant.objects.filter(name__in=[b['name'] for b in BUSINESS_DATA]).delete()
    
    # Create tenants
    tenants = []
    for business_data in BUSINESS_DATA:
        tenant = create_tenant_data(business_data)
        tenants.append(tenant)
        print()
    
    print("🎉 Comprehensive demo data creation complete!")
    print()
    print("📊 Summary:")
    print(f"   - Tenants created: {len(tenants)}")
    print(f"   - Total users: {len(tenants) * 3}")
    print(f"   - Total products: {sum(len(b['products']) for b in BUSINESS_DATA)}")
    print(f"   - Total orders: ~{sum(random.randint(20, 45) for _ in BUSINESS_DATA)}")
    print()
    print("🔐 Login credentials for each tenant:")
    for i, business_data in enumerate(BUSINESS_DATA):
        print(f"   {i+1}. {business_data['name']}:")
        print(f"      - Owner: owner@{business_data['domain']} / demo123")
        print(f"      - Manager: manager@{business_data['domain']} / demo123")
        print(f"      - Clerk: clerk@{business_data['domain']} / demo123")
    print()
    print("🌐 Access URLs:")
    print("   - Frontend: http://localhost:5173/")
    print("   - Admin Panel: http://localhost:8000/admin/")
    print("   - Analytics Dashboard: http://localhost:8000/admin/dashboard/")
    print("   - Reports: http://localhost:8000/admin/reports/")

if __name__ == '__main__':
    main()
