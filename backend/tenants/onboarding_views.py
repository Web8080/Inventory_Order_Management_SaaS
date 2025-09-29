"""
Onboarding views for new users
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count

from products.models import Product
from orders.models import Order
from inventory.models import StockItem
from .models import Tenant


@login_required
def onboarding_status(request):
    """Check if user needs onboarding"""
    tenant = request.user.tenant
    
    # Check if tenant has any data
    product_count = Product.objects.filter(tenant=tenant).count()
    order_count = Order.objects.filter(tenant=tenant).count()
    stock_count = StockItem.objects.filter(tenant=tenant).count()
    
    # If no data exists, user needs onboarding
    needs_onboarding = product_count == 0 and order_count == 0 and stock_count == 0
    
    return JsonResponse({
        'needs_onboarding': needs_onboarding,
        'product_count': product_count,
        'order_count': order_count,
        'stock_count': stock_count,
        'onboarding_steps': [
            {
                'id': 'welcome',
                'title': 'Welcome to InventoryFlow!',
                'description': 'Let\'s get you started with your inventory management journey.',
                'completed': not needs_onboarding
            },
            {
                'id': 'import_data',
                'title': 'Import Your Data',
                'description': 'Upload your existing products, inventory, and customer data.',
                'completed': product_count > 0 or stock_count > 0
            },
            {
                'id': 'setup_integrations',
                'title': 'Connect Integrations',
                'description': 'Link your e-commerce platforms and accounting software.',
                'completed': False  # TODO: Check actual integrations
            },
            {
                'id': 'explore_features',
                'title': 'Explore Features',
                'description': 'Learn about AI insights, analytics, and automation.',
                'completed': order_count > 0
            }
        ]
    })


@login_required
def onboarding_page(request):
    """Render onboarding page"""
    tenant = request.user.tenant
    return render(request, 'tenants/onboarding.html', {
        'tenant': tenant,
        'user': request.user
    })


@login_required
def complete_onboarding_step(request):
    """Mark an onboarding step as completed"""
    step_id = request.POST.get('step_id')
    
    # Here you could track completed steps in the database
    # For now, we'll just return success
    
    return JsonResponse({
        'success': True,
        'message': f'Step {step_id} completed successfully'
    })
