"""
Dashboard views for tenant-specific data
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Tenant
from products.models import Product, ProductVariant
from inventory.models import StockItem, StockTransaction
from orders.models import Order, OrderLine


@login_required
def dashboard_data(request):
    """Get dashboard data for the current tenant"""
    tenant = request.user.tenant
    
    # Get date ranges
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    # Sales data (last 30 days)
    sales_data = []
    for i in range(30):
        date = now - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        daily_sales = OrderLine.objects.filter(
            order__tenant=tenant,
            order__order_date__gte=day_start,
            order__order_date__lt=day_end,
            order__status='completed'
        ).aggregate(total=Sum('line_total'))['total'] or 0
        
        sales_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': float(daily_sales)
        })
    
    sales_data.reverse()  # Oldest to newest
    
    # Key metrics
    total_products = Product.objects.filter(tenant=tenant).count()
    total_orders = Order.objects.filter(tenant=tenant).count()
    total_inventory_value = StockItem.objects.filter(tenant=tenant).aggregate(
        total=Sum('quantity') * Sum('cost_price')
    )['total'] or 0
    
    # Recent orders (last 7 days)
    recent_orders = Order.objects.filter(
        tenant=tenant,
        order_date__gte=last_7_days
    ).order_by('-order_date')[:5]
    
    recent_orders_data = []
    for order in recent_orders:
        recent_orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}" if order.customer else 'Unknown',
            'total': float(order.total_amount),
            'status': order.status,
            'date': order.order_date.strftime('%Y-%m-%d')
        })
    
    # Low stock items
    low_stock_items = StockItem.objects.filter(
        tenant=tenant,
        quantity__lte=10  # Assuming 10 is low stock threshold
    ).select_related('product_variant__product')[:5]
    
    low_stock_data = []
    for item in low_stock_items:
        low_stock_data.append({
            'id': item.id,
            'product_name': item.product_variant.product.name,
            'sku': item.product_variant.sku,
            'quantity': item.quantity,
            'reorder_point': item.reorder_point
        })
    
    # Top products (by sales)
    top_products = OrderLine.objects.filter(
        order__tenant=tenant,
        order__status='completed'
    ).values(
        'product_variant__product__name'
    ).annotate(
        total_sales=Sum('line_total'),
        total_quantity=Sum('quantity')
    ).order_by('-total_sales')[:5]
    
    top_products_data = []
    for product in top_products:
        top_products_data.append({
            'name': product['product_variant__product__name'],
            'sales': float(product['total_sales']),
            'quantity': product['total_quantity']
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'sales_chart': {
                'labels': [item['date'] for item in sales_data],
                'data': [item['sales'] for item in sales_data]
            },
            'metrics': {
                'total_products': total_products,
                'total_orders': total_orders,
                'total_inventory_value': float(total_inventory_value),
                'revenue_30_days': sum([item['sales'] for item in sales_data])
            },
            'recent_orders': recent_orders_data,
            'low_stock_items': low_stock_data,
            'top_products': top_products_data
        }
    })


@login_required
def products_data(request):
    """Get products data for the current tenant"""
    tenant = request.user.tenant
    
    products = Product.objects.filter(tenant=tenant).select_related('category')
    products_data = []
    
    for product in products:
        # Get stock information
        stock_items = StockItem.objects.filter(
            product_variant__product=product,
            tenant=tenant
        )
        total_stock = sum([item.quantity for item in stock_items])
        
        # Get variants
        variants = ProductVariant.objects.filter(product=product, tenant=tenant)
        variants_data = []
        for variant in variants:
            variants_data.append({
                'id': variant.id,
                'sku': variant.sku,
                'name': variant.name,
                'selling_price': float(variant.selling_price),
                'cost_price': float(variant.cost_price)
            })
        
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'category': product.category.name if product.category else 'Uncategorized',
            'brand': product.brand,
            'total_stock': total_stock,
            'variants': variants_data
        })
    
    return JsonResponse({
        'success': True,
        'data': products_data
    })


@login_required
def orders_data(request):
    """Get orders data for the current tenant"""
    tenant = request.user.tenant
    
    orders = Order.objects.filter(tenant=tenant).select_related('customer').order_by('-order_date')
    orders_data = []
    
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}" if order.customer else 'Unknown',
            'customer_email': order.customer.email if order.customer else '',
            'total_amount': float(order.total_amount),
            'status': order.status,
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'shipping_amount': float(order.shipping_amount),
            'tax_amount': float(order.tax_amount)
        })
    
    return JsonResponse({
        'success': True,
        'data': orders_data
    })


@login_required
def inventory_data(request):
    """Get inventory data for the current tenant"""
    tenant = request.user.tenant
    
    stock_items = StockItem.objects.filter(tenant=tenant).select_related(
        'product_variant__product', 'warehouse'
    )
    inventory_data = []
    
    for item in stock_items:
        inventory_data.append({
            'id': item.id,
            'product_name': item.product_variant.product.name,
            'sku': item.product_variant.sku,
            'warehouse': item.warehouse.name,
            'quantity': item.quantity,
            'reorder_point': item.reorder_point,
            'cost_price': float(item.product_variant.cost_price),
            'selling_price': float(item.product_variant.selling_price),
            'location': item.location,
            'last_updated': item.last_updated.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': inventory_data
    })


@login_required
def user_management_data(request):
    """Get user management data for the current tenant"""
    tenant = request.user.tenant
    
    users = tenant.users.all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': getattr(user, 'role', 'user'),
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({
        'success': True,
        'data': users_data
    })
