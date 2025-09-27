from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta
import csv
import json


@staff_member_required
def admin_reports(request):
    """Admin reports dashboard"""
    
    # Import models here to avoid circular imports
    from tenants.models import Tenant, User
    from products.models import Product, Category, Supplier
    from orders.models import Order, OrderLine
    from inventory.models import StockItem, StockTransaction
    from integrations.models import Integration
    
    # Get date range from request
    start_date = request.GET.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Convert to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Sales Report
    sales_orders = Order.objects.filter(
        order_type='sale',
        created_at__date__range=[start_dt.date(), end_dt.date()]
    )
    
    total_sales = sales_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_orders.count()
    avg_order_value = sales_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    # Top Products
    top_products = OrderLine.objects.filter(
        order__order_type='sale',
        order__created_at__date__range=[start_dt.date(), end_dt.date()]
    ).values('product__name', 'product__sku').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('line_total')
    ).order_by('-total_revenue')[:10]
    
    # Tenant Performance
    tenant_performance = Tenant.objects.annotate(
        total_orders=Count('order_set'),
        total_revenue=Sum('order_set__total_amount', filter=Q(order_set__order_type='sale'))
    ).order_by('-total_revenue')[:10]
    
    # Inventory Report - get items with low stock using the property
    all_stock_items = StockItem.objects.all()
    low_stock_items = [item for item in all_stock_items if item.is_low_stock]
    # Calculate total inventory value by multiplying quantity * cost_price for each item
    total_inventory_value = 0
    for item in all_stock_items:
        if hasattr(item, 'product') and item.product and hasattr(item.product, 'cost_price'):
            total_inventory_value += item.quantity * item.product.cost_price
    
    # Integration Status
    integration_status = Integration.objects.values('integration_type').annotate(
        total=Count('id'),
        active=Count('id', filter=Q(is_enabled=True))
    )
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'tenant_performance': tenant_performance,
        'low_stock_items': low_stock_items,
        'total_inventory_value': total_inventory_value,
        'integration_status': integration_status,
    }
    
    return render(request, 'admin/reports.html', context)


@staff_member_required
def export_sales_report(request):
    """Export sales report to CSV"""
    from orders.models import Order
    
    start_date = request.GET.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    orders = Order.objects.filter(
        order_type='sale',
        created_at__date__range=[start_dt.date(), end_dt.date()]
    ).select_related('tenant')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Order Number', 'Tenant', 'Customer Name', 'Customer Email', 
        'Order Date', 'Total Amount', 'Payment Status', 'Order Status'
    ])
    
    for order in orders:
        writer.writerow([
            order.order_number,
            order.tenant.name if order.tenant else 'N/A',
            order.customer_name,
            order.customer_email,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.total_amount,
            order.get_payment_status_display(),
            order.get_status_display()
        ])
    
    return response


@staff_member_required
def export_inventory_report(request):
    """Export inventory report to CSV"""
    from inventory.models import StockItem
    stock_items = StockItem.objects.select_related('product', 'warehouse').all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inventory_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Product SKU', 'Product Name', 'Category', 'Warehouse', 
        'Current Stock', 'Reserved', 'Available', 'Reorder Point', 
        'Status', 'Last Updated'
    ])
    
    for item in stock_items:
        writer.writerow([
            item.product.sku,
            item.product.name,
            item.product.category.name if item.product.category else 'N/A',
            item.warehouse.name,
            item.quantity,
            item.reserved_quantity,
            item.quantity - item.reserved_quantity,
            item.reorder_point,
            'Low Stock' if item.is_low_stock else 'In Stock',
            item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@staff_member_required
def export_tenant_report(request):
    """Export tenant performance report to CSV"""
    from tenants.models import Tenant
    tenants = Tenant.objects.annotate(
        total_users=Count('users'),
        total_orders=Count('orders'),
        total_revenue=Sum('orders__total_amount', filter=Q(orders__order_type='sale')),
        total_products=Count('products')
    ).order_by('-total_revenue')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tenant_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Tenant Name', 'Plan', 'Status', 'Users', 'Products', 
        'Orders', 'Total Revenue', 'Created Date'
    ])
    
    for tenant in tenants:
        writer.writerow([
            tenant.name,
            tenant.get_plan_display(),
            'Active' if tenant.is_active else 'Inactive',
            tenant.total_users,
            tenant.total_products,
            tenant.total_orders,
            tenant.total_revenue or 0,
            tenant.created_at.strftime('%Y-%m-%d')
        ])
    
    return response


@staff_member_required
def export_integration_report(request):
    """Export integration status report to CSV"""
    from integrations.models import Integration
    integrations = Integration.objects.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="integration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Integration Name', 'Type', 'Status', 'Enabled', 
        'Last Sync', 'Sync Status', 'Created Date'
    ])
    
    for integration in integrations:
        writer.writerow([
            integration.name,
            integration.get_integration_type_display(),
            integration.get_status_display(),
            'Yes' if integration.is_enabled else 'No',
            integration.last_sync_at.strftime('%Y-%m-%d %H:%M:%S') if integration.last_sync_at else 'Never',
            integration.last_sync_status or 'N/A',
            integration.created_at.strftime('%Y-%m-%d')
        ])
    
    return response
