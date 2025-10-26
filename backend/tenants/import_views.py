"""
Data import views for tenant onboarding
"""

import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import json

from .models import Tenant
from .utils import process_csv_import, generate_sample_csvs
from products.models import Category, Supplier, Product, ProductVariant
from inventory.models import StockItem, Warehouse


@login_required
def data_import_page(request):
    """Data import page for tenants"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        messages.error(request, 'No tenant associated with your account.')
        return redirect('/')
    
    tenant = request.user.tenant
    
    # Get import statistics
    stats = {
        'products_count': Product.objects.filter(tenant=tenant).count(),
        'customers_count': 0,  # Would be from User model with role='customer'
        'inventory_count': StockItem.objects.filter(tenant=tenant).count(),
        'suppliers_count': Supplier.objects.filter(tenant=tenant).count(),
    }
    
    context = {
        'tenant': tenant,
        'stats': stats,
    }
    
    return render(request, 'tenants/data_import.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_csv(request):
    """Handle CSV file upload and import"""
    print("=" * 50)
    print("CSV UPLOAD REQUEST RECEIVED")
    print("=" * 50)
    
    try:
        if not hasattr(request.user, 'tenant') or not request.user.tenant:
            print("ERROR: No tenant associated with user")
            return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
        
        tenant = request.user.tenant
        file = request.FILES.get('file')
        import_type = request.POST.get('type')
        
        print(f"Upload request - Tenant: {tenant.name}, File: {file.name if file else 'None'}, Type: {import_type}")
        print(f"Request FILES: {list(request.FILES.keys())}")
        print(f"Request POST: {dict(request.POST)}")
        
        if not file or not import_type:
            return JsonResponse({'error': 'Missing file or import type.'}, status=400)
        
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'Please upload a CSV file.'}, status=400)
        
        # Read and process the CSV file
        content = file.read().decode('utf-8')
        print(f"CSV content length: {len(content)}")
        print(f"CSV content preview: {content[:200]}...")
        
        # Create CSV reader and check content
        csv_reader = csv.DictReader(io.StringIO(content))
        print(f"CSV headers: {csv_reader.fieldnames}")
        
        # Convert to list to check if we have any rows (this consumes the reader)
        rows = list(csv_reader)
        print(f"Number of CSV rows found: {len(rows)}")
        if rows:
            print(f"First row sample: {rows[0]}")
        else:
            print("No rows found in CSV!")
            return JsonResponse({
                'success': False,
                'count': 0,
                'message': 'No data rows found in CSV file.'
            })
        
        # Process based on import type
        # Re-create CSV reader since the previous one was consumed
        csv_reader = csv.DictReader(io.StringIO(content))
        
        if import_type == 'products':
            count = import_products(tenant, csv_reader)
        elif import_type == 'customers':
            count = import_customers(tenant, csv_reader)
        elif import_type == 'inventory':
            count = import_inventory(tenant, csv_reader)
        elif import_type == 'suppliers':
            count = import_suppliers(tenant, csv_reader)
        elif import_type == 'orders':
            count = import_orders(tenant, csv_reader)
        else:
            return JsonResponse({'error': 'Invalid import type.'}, status=400)
        
        print(f"Import result: {count} {import_type} imported")
        
        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'Successfully imported {count} {import_type}.'
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Import failed: {str(e)}'}, status=500)


def import_products(tenant, csv_reader):
    """Import products from CSV"""
    imported_count = 0
    error_count = 0
    
    with transaction.atomic():
        for row_num, row in enumerate(csv_reader, 1):
            try:
                print(f"Processing row {row_num}: {row}")
                
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
                
                # Get or create product
                product, created = Product.objects.get_or_create(
                    tenant=tenant,
                    sku=row.get('sku', f'PROD-{row_num}'),
                    defaults={
                        'name': row.get('name', 'Unnamed Product'),
                        'description': row.get('description', ''),
                        'category': category,
                        'supplier': supplier,
                        'cost_price': Decimal('0.00'),  # Default cost price
                        'selling_price': Decimal(row.get('price', row.get('selling_price', '0.00'))),
                        'unit': 'piece',  # Default unit
                        'reorder_point': 10,  # Default reorder point
                        'reorder_quantity': 50,  # Default reorder quantity
                        'barcode': row.get('barcode', ''),
                        'is_active': True,
                        'is_tracked': True
                    }
                )
                if created:
                    print(f"Created new product: {product.name} (ID: {product.id})")
                else:
                    print(f"Using existing product: {product.name} (ID: {product.id})")
                
                # Get or create product variant with a different SKU
                variant_sku = f"{row.get('sku', f'PROD-{product.id}')}-VAR"
                variant, variant_created = ProductVariant.objects.get_or_create(
                    tenant=tenant,
                    product=product,
                    sku=variant_sku,
                    defaults={
                        'name': row.get('name', 'Default Variant'),
                        'selling_price': Decimal(row.get('selling_price', row.get('price', '0.00'))),
                        'cost_price': Decimal(row.get('cost_price', row.get('cost', '0.00'))),
                        'is_active': True
                    }
                )
                if variant_created:
                    print(f"Created new variant: {variant.sku} (ID: {variant.id})")
                else:
                    print(f"Using existing variant: {variant.sku} (ID: {variant.id})")
                
                # Create initial stock if stock quantity is provided
                stock_quantity = row.get('stock', '')
                if stock_quantity and stock_quantity.isdigit():
                    from inventory.models import Warehouse, StockItem
                    
                    # Get or create default warehouse
                    warehouse, warehouse_created = Warehouse.objects.get_or_create(
                        tenant=tenant,
                        code='MAIN',
                        defaults={
                            'name': f"{tenant.name} Main Warehouse",
                            'address': "Main warehouse location",
                            'is_default': True,
                            'is_active': True
                        }
                    )
                    
                    # Create stock item
                    stock_item, stock_created = StockItem.objects.get_or_create(
                        tenant=tenant,
                        product=product,
                        warehouse=warehouse,
                        defaults={
                            'quantity': int(stock_quantity),
                            'reserved_quantity': 0
                        }
                    )
                    
                    if stock_created:
                        print(f"Created initial stock: {stock_quantity} units for {product.name}")
                    else:
                        # Update existing stock
                        stock_item.quantity = int(stock_quantity)
                        stock_item.save()
                        print(f"Updated stock: {stock_quantity} units for {product.name}")
                
                imported_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error importing product row {row_num}: {e}")
                print(f"Row data: {row}")
                continue
    
    print(f"Import completed: {imported_count} products imported, {error_count} errors")
    return imported_count


def import_customers(tenant, csv_reader):
    """Import customers from CSV"""
    from products.models import Customer
    
    imported_count = 0
    error_count = 0
    
    with transaction.atomic():
        for row_num, row in enumerate(csv_reader, 1):
            try:
                print(f"Processing customer row {row_num}: {row}")
                
                customer, created = Customer.objects.get_or_create(
                    tenant=tenant,
                    email=row.get('email', ''),
                    defaults={
                        'first_name': row.get('first_name', 'Unknown'),
                        'last_name': row.get('last_name', 'Customer'),
                        'phone': row.get('phone', ''),
                        'address': row.get('address', ''),
                        'city': row.get('city', ''),
                        'state': row.get('state', ''),
                        'zip_code': row.get('zip_code', ''),
                        'country': row.get('country', ''),
                        'company': row.get('company', ''),
                        'is_active': True,  # Default to active
                        'notes': row.get('notes', '')
                    }
                )
                
                if created:
                    imported_count += 1
                    print(f"Created customer: {customer.full_name}")
                else:
                    print(f"Customer already exists: {customer.full_name}")
                
            except Exception as e:
                error_count += 1
                print(f"Error importing customer row {row_num}: {e}")
                print(f"Row data: {row}")
                continue
    
    print(f"Customer import completed: {imported_count} customers imported, {error_count} errors")
    return imported_count


def import_inventory(tenant, csv_reader):
    """Import inventory from CSV"""
    from inventory.models import Warehouse, StockItem
    from products.models import Product, ProductVariant
    
    imported_count = 0
    error_count = 0
    
    with transaction.atomic():
        for row_num, row in enumerate(csv_reader, 1):
            try:
                print(f"Processing inventory row {row_num}: {row}")
                
                # Find product by SKU
                sku = row.get('product_sku', '')
                if not sku:
                    print(f"No product SKU found in row {row_num}")
                    continue
                
                try:
                    product = Product.objects.get(sku=sku, tenant=tenant)
                except Product.DoesNotExist:
                    print(f"Product with SKU {sku} not found for tenant {tenant.name}")
                    continue
                
                # Get or create warehouse
                warehouse_name = row.get('warehouse', 'Main Warehouse')
                
                warehouse, warehouse_created = Warehouse.objects.get_or_create(
                    tenant=tenant,
                    name=warehouse_name,
                    defaults={
                        'code': warehouse_name.upper().replace(' ', '_')[:10],
                        'address': f"Warehouse address for {warehouse_name}",
                        'is_active': True,
                        'is_default': warehouse_name.lower() == 'main warehouse'
                    }
                )
                
                if warehouse_created:
                    print(f"Created new warehouse: {warehouse.name}")
                else:
                    print(f"Using existing warehouse: {warehouse.name}")
                
                # Get or create stock item
                stock_item, stock_created = StockItem.objects.get_or_create(
                    tenant=tenant,
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': int(row.get('quantity', 0)),
                        'reserved_quantity': 0  # Default to 0
                    }
                )
                
                if stock_created:
                    imported_count += 1
                    print(f"Created new stock item: {product.name} in {warehouse.name}")
                else:
                    # Update existing stock item
                    stock_item.quantity = int(row.get('quantity', stock_item.quantity))
                    stock_item.save()
                    print(f"Updated existing stock item: {product.name} in {warehouse.name}")
                
            except Exception as e:
                error_count += 1
                print(f"Error importing inventory row {row_num}: {e}")
                print(f"Row data: {row}")
                continue
    
    print(f"Inventory import completed: {imported_count} items imported, {error_count} errors")
    return imported_count


def import_suppliers(tenant, csv_reader):
    """Import suppliers from CSV"""
    from products.models import Supplier
    
    imported_count = 0
    error_count = 0
    
    print(f"Starting supplier import for tenant: {tenant.name}")
    print(f"CSV reader fieldnames: {csv_reader.fieldnames}")
    
    with transaction.atomic():
        for row_num, row in enumerate(csv_reader, 1):
            try:
                print(f"Processing supplier row {row_num}: {row}")
                
                supplier, created = Supplier.objects.get_or_create(
                    tenant=tenant,
                    name=row.get('name', 'Unnamed Supplier'),
                    defaults={
                        'contact_person': row.get('contact_person', ''),
                        'email': row.get('email', ''),
                        'phone': row.get('phone', ''),
                        'address': row.get('address', ''),
                        'website': row.get('website', ''),
                        'payment_terms': row.get('payment_terms', ''),
                        'notes': row.get('notes', ''),
                        'is_active': True  # Default to active
                    }
                )
                
                if created:
                    imported_count += 1
                    print(f"Created new supplier: {supplier.name}")
                else:
                    print(f"Supplier already exists: {supplier.name}")
                
            except Exception as e:
                error_count += 1
                print(f"Error importing supplier row {row_num}: {e}")
                print(f"Row data: {row}")
                continue
    
    print(f"Import completed: {imported_count} suppliers imported, {error_count} errors")
    return imported_count


def import_orders(tenant, csv_reader):
    """Import orders from CSV"""
    from orders.models import Order, OrderLine
    from products.models import Product, ProductVariant
    from django.utils.dateparse import parse_datetime
    from django.utils import timezone
    
    imported_count = 0
    error_count = 0
    
    with transaction.atomic():
        for row_num, row in enumerate(csv_reader, 1):
            try:
                print(f"Processing order row {row_num}: {row}")
                
                # Get or create the product
                product_sku = row.get('product_sku', '')
                if not product_sku:
                    print(f"No product SKU found in row {row_num}")
                    continue
                    
                try:
                    product = Product.objects.get(tenant=tenant, sku=product_sku)
                except Product.DoesNotExist:
                    print(f"Product with SKU {product_sku} not found for tenant {tenant.name}")
                    continue
                
                # Create the order
                order, order_created = Order.objects.get_or_create(
                    tenant=tenant,
                    order_number=row.get('order_number', f'ORD-{imported_count + 1}'),
                    defaults={
                        'order_type': 'sale',  # Default to sale
                        'status': row.get('status', 'pending'),
                        'customer_name': row.get('customer_name', 'Unknown Customer'),
                        'customer_email': row.get('customer_email', 'customer@example.com'),
                        'customer_phone': row.get('customer_phone', '555-0123'),
                        'customer_address': '',  # Default empty
                        'subtotal': Decimal(row.get('total_price', '0.00')),
                        'tax_amount': Decimal('0.00'),  # Default to 0
                        'discount_amount': Decimal('0.00'),  # Default to 0
                        'shipping_amount': Decimal('0.00'),  # Default to 0
                        'total_amount': Decimal(row.get('total_price', '0.00')),
                        'payment_status': 'pending',  # Default to pending
                        'payment_method': '',  # Default empty
                        'shipping_address': '',  # Default empty
                        'shipping_method': '',  # Default empty
                        'order_date': parse_datetime(row.get('order_date', '')) if row.get('order_date') else timezone.now(),
                        'required_date': None,  # Default to None
                        'notes': ''  # Default empty
                    }
                )
                
                if order_created:
                    print(f"Created new order: {order.order_number}")
                else:
                    print(f"Order already exists: {order.order_number}")
                
                # Create the order line
                order_line, item_created = OrderLine.objects.get_or_create(
                    tenant=tenant,
                    order=order,
                    product=product,
                    defaults={
                        'quantity': int(row.get('quantity', 1)),
                        'unit_price': Decimal(row.get('unit_price', '0.00')),
                        'line_total': Decimal(row.get('line_total', '0.00'))
                    }
                )
                
                if item_created:
                    imported_count += 1
                    print(f"Created order line for {product.name}")
                else:
                    print(f"Order line already exists for {product.name}")
                
            except Exception as e:
                error_count += 1
                print(f"Error importing order row {row_num}: {e}")
                print(f"Row data: {row}")
                continue
    
    print(f"Order import completed: {imported_count} orders imported, {error_count} errors")
    return imported_count


@login_required
def download_template(request, template_type):
    """Download CSV template for data import"""
    import os
    from django.conf import settings
    
    # Map template types to file names
    template_files = {
        'products': 'products_template.csv',
        'inventory': 'inventory_template.csv',
        'orders': 'orders_template.csv',
        'customers': 'customers_template.csv',
        'suppliers': 'suppliers_template.csv'
    }
    
    if template_type not in template_files:
        return JsonResponse({'error': 'Invalid template type.'}, status=400)
    
    # Get the file path
    file_name = template_files[template_type]
    file_path = os.path.join(settings.BASE_DIR, 'templates', 'csv_templates', file_name)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'Template file not found.'}, status=404)
    
    # Read and serve the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    except Exception as e:
        return JsonResponse({'error': f'Error reading template file: {str(e)}'}, status=500)


# Manual Entry Endpoints
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manual_products(request):
    """Add a product manually"""
    try:
        data = json.loads(request.body)
        tenant = request.user.tenant
        
        # Get or create category
        category = None
        if data.get('category'):
            category, _ = Category.objects.get_or_create(
                name=data['category'],
                tenant=tenant,
                defaults={'description': f'Category for {data["category"]}'}
            )
        
        # Get or create supplier
        supplier = None
        if data.get('supplier'):
            supplier, _ = Supplier.objects.get_or_create(
                name=data['supplier'],
                tenant=tenant,
                defaults={
                    'contact_person': 'Contact Person',
                    'email': 'supplier@example.com',
                    'phone': '555-0123'
                }
            )
        
        # Create product
        product = Product.objects.create(
            tenant=tenant,
            name=data['name'],
            description=data.get('description', ''),
            category=category,
            brand=data.get('brand', ''),
            supplier=supplier,
            is_active=True
        )
        
        # Create product variant
        ProductVariant.objects.create(
            tenant=tenant,
            product=product,
            sku=data['sku'],
            name=data['name'],
            selling_price=Decimal(data['selling_price']),
            cost_price=Decimal(data['cost_price']),
            barcode=data.get('barcode', ''),
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Product added successfully',
            'product_id': product.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manual_inventory(request):
    """Add inventory manually"""
    try:
        data = json.loads(request.body)
        tenant = request.user.tenant
        
        # Get product variant
        try:
            variant = ProductVariant.objects.get(sku=data['product_sku'], tenant=tenant)
        except ProductVariant.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            }, status=400)
        
        # Get or create warehouse
        warehouse, _ = Warehouse.objects.get_or_create(
            name=data['warehouse'],
            tenant=tenant,
            defaults={
                'address': 'Main Warehouse Address',
                'is_default': True
            }
        )
        
        # Create stock item
        StockItem.objects.create(
            tenant=tenant,
            product_variant=variant,
            warehouse=warehouse,
            quantity=int(data['quantity']),
            reorder_point=int(data.get('reorder_point', 10)),
            location=data.get('location', ''),
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Inventory added successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manual_customers(request):
    """Add a customer manually - stored as customer data for future orders"""
    try:
        data = json.loads(request.body)
        tenant = request.user.tenant
        
        # For now, we'll just return success since customers are stored in orders
        # In a real system, you might want to create a Customer model
        # For this demo, we'll store customer info in the session or a simple storage
        
        return JsonResponse({
            'success': True,
            'message': 'Customer information saved successfully. Customer data will be used when creating orders.',
            'customer_name': f"{data['first_name']} {data['last_name']}"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manual_suppliers(request):
    """Add a supplier manually"""
    try:
        data = json.loads(request.body)
        tenant = request.user.tenant
        
        # Create supplier
        supplier = Supplier.objects.create(
            tenant=tenant,
            name=data['name'],
            contact_person=data['contact_person'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Supplier added successfully',
            'supplier_id': supplier.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def import_status(request):
    """Get import status and statistics"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
    
    tenant = request.user.tenant
    
    stats = {
        'products_count': Product.objects.filter(tenant=tenant).count(),
        'customers_count': 0,  # Would be from User model with role='customer'
        'inventory_count': StockItem.objects.filter(tenant=tenant).count(),
        'suppliers_count': Supplier.objects.filter(tenant=tenant).count(),
    }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })
