from django.contrib import admin
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
import json


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with analytics and KPIs"""
    
    # Import models here to avoid circular imports
    from tenants.models import Tenant, User
    from products.models import Product
    from orders.models import Order, OrderLine
    from inventory.models import StockItem
    from integrations.models import Integration
    
    # Calculate statistics
    total_tenants = Tenant.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    # Count low stock items using the property
    low_stock_items = sum(1 for item in StockItem.objects.all() if item.is_low_stock)
    active_integrations = Integration.objects.filter(is_enabled=True).count()
    
    # Sales data for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    sales_data = []
    sales_labels = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        daily_sales = Order.objects.filter(
            created_at__date=date.date(),
            order_type='sale'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        sales_data.append(float(daily_sales))
        sales_labels.append(date.strftime('%m/%d'))
    
    # Top products by sales
    top_products = OrderLine.objects.filter(
        order__order_type='sale',
        order__created_at__gte=thirty_days_ago
    ).values('product__name').annotate(
        total_sales=Sum('line_total')
    ).order_by('-total_sales')[:6]
    
    product_labels = [p['product__name'] for p in top_products]
    product_data = [float(p['total_sales']) for p in top_products]
    
    # Recent activities
    recent_activities = []
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]
    for order in recent_orders:
        recent_activities.append({
            'icon': '🛒',
            'title': f'New {order.get_order_type_display()} order #{order.order_number}',
            'time': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'color': '#667eea'
        })
    
    # Recent users
    recent_users = User.objects.order_by('-created_at')[:3]
    for user in recent_users:
        recent_activities.append({
            'icon': '👤',
            'title': f'New user registered: {user.email}',
            'time': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'color': '#764ba2'
        })
    
    # Low stock alerts - get items with low stock using the property
    all_stock_items = StockItem.objects.all()
    low_stock = [item for item in all_stock_items if item.is_low_stock][:3]
    for item in low_stock:
        recent_activities.append({
            'icon': '⚠️',
            'title': f'Low stock alert: {item.product.name}',
            'time': item.last_updated.strftime('%Y-%m-%d %H:%M'),
            'color': '#f5576c'
        })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]
    
    context = {
        'total_tenants': total_tenants,
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'low_stock_items': low_stock_items,
        'active_integrations': active_integrations,
        'sales_data': json.dumps(sales_data),
        'sales_labels': json.dumps(sales_labels),
        'product_data': json.dumps(product_data),
        'product_labels': json.dumps(product_labels),
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin/index.html', context)
