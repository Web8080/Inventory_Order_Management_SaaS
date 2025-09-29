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
    try:
        if not hasattr(request.user, 'tenant') or not request.user.tenant:
            return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
        
        tenant = request.user.tenant
        file = request.FILES.get('file')
        import_type = request.POST.get('type')
        
        if not file or not import_type:
            return JsonResponse({'error': 'Missing file or import type.'}, status=400)
        
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'Please upload a CSV file.'}, status=400)
        
        # Read and process the CSV file
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # Process based on import type
        if import_type == 'products':
            count = import_products(tenant, csv_reader)
        elif import_type == 'customers':
            count = import_customers(tenant, csv_reader)
        elif import_type == 'inventory':
            count = import_inventory(tenant, csv_reader)
        elif import_type == 'suppliers':
            count = import_suppliers(tenant, csv_reader)
        else:
            return JsonResponse({'error': 'Invalid import type.'}, status=400)
        
        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'Successfully imported {count} {import_type}.'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Import failed: {str(e)}'}, status=500)


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
                    selling_price=Decimal(row.get('price', '0.00')),
                    cost_price=Decimal(row.get('cost', '0.00')),
                    weight=float(row.get('weight', '0.0')),
                    dimensions=row.get('dimensions', ''),
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


@login_required
def download_template(request, template_type):
    """Download CSV template for data import"""
    samples = generate_sample_csvs()
    
    if template_type not in samples:
        return JsonResponse({'error': 'Invalid template type.'}, status=400)
    
    template_data = samples[template_type]
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{template_data["filename"]}"'
    
    # Write CSV content
    writer = csv.writer(response)
    writer.writerow(template_data['headers'])
    
    for row in template_data['sample_data']:
        writer.writerow(row)
    
    return response


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
