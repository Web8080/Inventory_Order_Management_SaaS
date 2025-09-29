"""
Tenant utilities for data import and onboarding
"""

import csv
import io
from decimal import Decimal
from django.db import transaction
from products.models import Category, Supplier, Product, ProductVariant
from inventory.models import Warehouse, StockItem
from orders.models import Order, OrderLine


def process_csv_import(tenant, files):
    """
    Process uploaded CSV files for tenant onboarding
    """
    results = {
        'products_imported': 0,
        'customers_imported': 0,
        'inventory_imported': 0,
        'suppliers_imported': 0,
        'errors': []
    }
    
    for file in files:
        try:
            # Read CSV content
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Determine file type based on filename or content
            filename = file.name.lower()
            
            if 'product' in filename:
                results['products_imported'] += import_products(tenant, csv_reader)
            elif 'customer' in filename:
                results['customers_imported'] += import_customers(tenant, csv_reader)
            elif 'inventory' in filename or 'stock' in filename:
                results['inventory_imported'] += import_inventory(tenant, csv_reader)
            elif 'supplier' in filename:
                results['suppliers_imported'] += import_suppliers(tenant, csv_reader)
            else:
                # Try to auto-detect based on columns
                if auto_detect_and_import(tenant, csv_reader, results):
                    continue
                else:
                    results['errors'].append(f"Could not determine file type for {file.name}")
                    
        except Exception as e:
            results['errors'].append(f"Error processing {file.name}: {str(e)}")
    
    return results


def import_products(tenant, csv_reader):
    """Import products from CSV"""
    imported_count = 0
    
    with transaction.atomic():
        for row in csv_reader:
            try:
                # Get or create category
                category_name = row.get('category', 'General')
                category, _ = Category.objects.get_or_create(
                    tenant=tenant,
                    name=category_name,
                    defaults={'description': f'{category_name} products', 'is_active': True}
                )
                
                # Get or create supplier
                supplier_name = row.get('supplier', 'Default Supplier')
                supplier, _ = Supplier.objects.get_or_create(
                    tenant=tenant,
                    name=supplier_name,
                    defaults={
                        'contact_person': 'Contact Person',
                        'email': 'supplier@example.com',
                        'phone': '555-0123',
                        'is_active': True
                    }
                )
                
                # Create product
                product = Product.objects.create(
                    tenant=tenant,
                    name=row.get('name', 'Unnamed Product'),
                    description=row.get('description', ''),
                    category=category,
                    supplier=supplier,
                    is_active=True
                )
                
                # Create product variant
                ProductVariant.objects.create(
                    product=product,
                    sku=row.get('sku', f'PROD-{product.id}'),
                    name=row.get('name', 'Default Variant'),
                    selling_price=Decimal(row.get('selling_price', row.get('price', '0.00'))),
                    cost_price=Decimal(row.get('cost_price', row.get('cost', '0.00'))),
                    barcode=row.get('barcode', ''),
                    is_active=True
                )
                
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing product row: {e}")
                continue
    
    return imported_count


def import_customers(tenant, csv_reader):
    """Import customers from CSV"""
    imported_count = 0
    
    with transaction.atomic():
        for row in csv_reader:
            try:
                # Create customer (stored as User with role 'customer')
                from .models import User
                customer = User.objects.create_user(
                    username=f"customer_{row.get('email', f'customer_{imported_count}')}",
                    email=row.get('email', f'customer{imported_count}@example.com'),
                    first_name=row.get('first_name', 'Customer'),
                    last_name=row.get('last_name', 'Name'),
                    phone=row.get('phone', ''),
                    tenant=tenant,
                    role='customer',
                    is_active=True
                )
                
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing customer row: {e}")
                continue
    
    return imported_count


def import_inventory(tenant, csv_reader):
    """Import inventory from CSV"""
    imported_count = 0
    
    with transaction.atomic():
        # Get default warehouse
        warehouse = Warehouse.objects.filter(tenant=tenant, is_default=True).first()
        if not warehouse:
            warehouse = Warehouse.objects.create(
                tenant=tenant,
                name=f"{tenant.name} Main Warehouse",
                code='MAIN',
                address="123 Main Street",
                is_default=True,
                is_active=True
            )
        
        for row in csv_reader:
            try:
                # Find product by SKU
                sku = row.get('product_sku', '')
                if not sku:
                    continue
                
                try:
                    variant = ProductVariant.objects.get(sku=sku, product__tenant=tenant)
                except ProductVariant.DoesNotExist:
                    continue
                
                # Create stock item
                StockItem.objects.create(
                    tenant=tenant,
                    product_variant=variant,
                    warehouse=warehouse,
                    quantity=int(row.get('quantity', '0')),
                    reorder_point=int(row.get('reorder_point', '10')),
                    cost_price=Decimal(row.get('cost_price', '0.00')),
                    is_active=True
                )
                
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing inventory row: {e}")
                continue
    
    return imported_count


def import_suppliers(tenant, csv_reader):
    """Import suppliers from CSV"""
    imported_count = 0
    
    with transaction.atomic():
        for row in csv_reader:
            try:
                Supplier.objects.create(
                    tenant=tenant,
                    name=row.get('name', 'Unnamed Supplier'),
                    contact_person=row.get('contact_person', 'Contact Person'),
                    email=row.get('email', 'supplier@example.com'),
                    phone=row.get('phone', '555-0123'),
                    address=row.get('address', ''),
                    is_active=True
                )
                
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing supplier row: {e}")
                continue
    
    return imported_count


def auto_detect_and_import(tenant, csv_reader, results):
    """Auto-detect file type and import accordingly"""
    # Get first row to analyze columns
    first_row = next(csv_reader, None)
    if not first_row:
        return False
    
    columns = [col.lower() for col in first_row.keys()]
    
    # Check for product indicators
    if any(col in columns for col in ['name', 'sku', 'price', 'cost']):
        if 'product' in columns or 'category' in columns:
            results['products_imported'] += import_products(tenant, [first_row] + list(csv_reader))
            return True
    
    # Check for customer indicators
    if any(col in columns for col in ['email', 'first_name', 'last_name', 'phone']):
        if 'customer' in columns or 'email' in columns:
            results['customers_imported'] += import_customers(tenant, [first_row] + list(csv_reader))
            return True
    
    # Check for inventory indicators
    if any(col in columns for col in ['product_sku', 'quantity', 'warehouse']):
        results['inventory_imported'] += import_inventory(tenant, [first_row] + list(csv_reader))
        return True
    
    # Check for supplier indicators
    if any(col in columns for col in ['supplier', 'contact_person', 'address']):
        results['suppliers_imported'] += import_suppliers(tenant, [first_row] + list(csv_reader))
        return True
    
    return False


def generate_sample_csvs():
    """Generate sample CSV files for download"""
    samples = {
        'products': {
            'filename': 'products_template.csv',
            'headers': ['sku', 'name', 'description', 'category', 'brand', 'supplier', 'selling_price', 'cost_price', 'barcode'],
            'sample_data': [
                ['PROD001', 'Sample Product A', 'Description for Product A', 'Electronics', 'BrandX', 'SupplierY', '19.99', '10.00', '1234567890123'],
                ['PROD002', 'Sample Product B', 'Description for Product B', 'Clothing', 'BrandZ', 'SupplierW', '29.99', '15.00', '3210987654321'],
                ['PROD003', 'Sample Product C', 'Description for Product C', 'Home & Garden', 'BrandA', 'SupplierB', '49.99', '25.00', '4567891234567']
            ]
        },
        'customers': {
            'filename': 'customers_template.csv',
            'headers': ['first_name', 'last_name', 'email', 'phone', 'address'],
            'sample_data': [
                ['John', 'Doe', 'john.doe@example.com', '555-1234', '123 Main St, Anytown, USA'],
                ['Jane', 'Smith', 'jane.smith@example.com', '555-5678', '456 Oak Ave, Otherville, USA'],
                ['Bob', 'Johnson', 'bob.johnson@example.com', '555-9012', '789 Pine Rd, Somewhere, USA']
            ]
        },
        'inventory': {
            'filename': 'inventory_template.csv',
            'headers': ['product_sku', 'warehouse', 'quantity', 'reorder_point', 'location'],
            'sample_data': [
                ['PROD001', 'Main Warehouse', '100', '20', 'Aisle 1, Shelf 3'],
                ['PROD002', 'Main Warehouse', '50', '10', 'Aisle 2, Shelf 1'],
                ['PROD003', 'Secondary Warehouse', '75', '15', 'Aisle 3, Shelf 2']
            ]
        },
        'suppliers': {
            'filename': 'suppliers_template.csv',
            'headers': ['name', 'contact_person', 'email', 'phone', 'address'],
            'sample_data': [
                ['Supplier A Inc', 'Alice Johnson', 'alice@supplierA.com', '111-222-3333', '789 Pine Ln, Supplier City, SC 12345'],
                ['Global Parts Ltd', 'Bob Williams', 'bob@globalparts.com', '444-555-6666', '101 Industrial Rd, Parts Town, PT 67890'],
                ['Quality Goods Co', 'Carol Davis', 'carol@qualitygoods.com', '777-888-9999', '555 Commerce St, Business City, BC 54321']
            ]
        }
    }
    
    return samples
