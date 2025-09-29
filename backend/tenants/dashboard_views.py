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
            order__created_at__gte=day_start,
            order__created_at__lt=day_end,
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
    # Total inventory value (sum of quantity * cost_price from variants)
    total_inventory_value = 0
    stock_items = StockItem.objects.filter(tenant=tenant).select_related('variant')
    for item in stock_items:
        if item.variant and item.variant.cost_price:
            total_inventory_value += float(item.quantity * item.variant.cost_price)
    
    # Recent orders (last 7 days)
    recent_orders = Order.objects.filter(
        tenant=tenant,
        created_at__gte=last_7_days
    ).order_by('-created_at')[:5]
    
    recent_orders_data = []
    for order in recent_orders:
        recent_orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name or 'Unknown',
            'total': float(order.total_amount),
            'status': order.status,
            'date': order.created_at.strftime('%Y-%m-%d')
        })
    
    # Low stock items
    low_stock_items = StockItem.objects.filter(
        tenant=tenant,
        quantity__lte=10  # Assuming 10 is low stock threshold
    ).select_related('variant__product')[:5]
    
    low_stock_data = []
    for item in low_stock_items:
        low_stock_data.append({
            'id': item.id,
            'product_name': item.variant.product.name if item.variant else item.product.name,
            'sku': item.variant.sku if item.variant else 'N/A',
            'quantity': item.quantity,
            'reorder_point': item.variant.reorder_point if item.variant else 10
        })
    
    # Top products (by sales)
    top_products = OrderLine.objects.filter(
        order__tenant=tenant,
        order__status='completed'
    ).values(
        'variant__product__name'
    ).annotate(
        total_sales=Sum('line_total'),
        total_quantity=Sum('quantity')
    ).order_by('-total_sales')[:5]
    
    top_products_data = []
    for product in top_products:
        top_products_data.append({
            'name': product['variant__product__name'],
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
    
    # Get all product variants with their products
    variants = ProductVariant.objects.filter(
        product__tenant=tenant
    ).select_related('product', 'product__category')
    
    products_data = []
    
    for variant in variants:
        # Get stock information for this variant
        stock_items = StockItem.objects.filter(
            variant=variant,
            tenant=tenant
        )
        total_stock = sum([item.quantity for item in stock_items])
        reorder_point = stock_items.first().variant.reorder_point if stock_items.exists() and stock_items.first().variant else 10
        
        products_data.append({
            'id': variant.id,
            'sku': variant.sku,
            'name': variant.name or variant.product.name,
            'description': variant.product.description,
            'category': variant.product.category.name if variant.product.category else 'Uncategorized',
            'brand': 'N/A',  # Product model doesn't have brand field
            'selling_price': float(variant.selling_price),
            'cost_price': float(variant.cost_price),
            'stock': total_stock,
            'reorder_point': reorder_point,
            'product_id': variant.product.id
        })
    
    return JsonResponse({
        'success': True,
        'data': products_data
    })


@login_required
def orders_data(request):
    """Get orders data for the current tenant"""
    tenant = request.user.tenant
    
    orders = Order.objects.filter(tenant=tenant).order_by('-created_at')
    orders_data = []
    
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name or 'Unknown',
            'customer_email': order.customer_email or '',
            'total_amount': float(order.total_amount),
            'status': order.status,
            'order_date': order.created_at.strftime('%Y-%m-%d'),
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
        'variant__product', 'warehouse'
    )
    inventory_data = []
    
    for item in stock_items:
        inventory_data.append({
            'id': item.id,
            'product_name': item.variant.product.name if item.variant else item.product.name,
            'sku': item.variant.sku if item.variant else 'N/A',
            'warehouse': item.warehouse.name,
            'quantity': item.quantity,
            'reorder_point': item.variant.reorder_point if item.variant else 10,
            'cost_price': float(item.variant.cost_price) if item.variant else 0.0,
            'selling_price': float(item.variant.selling_price) if item.variant else 0.0,
            'location': item.warehouse.name,
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
