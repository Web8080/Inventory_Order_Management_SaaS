"""
Trial management views
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

from .models import Tenant
from .payment_models import Subscription
from .trial_management import check_trial_status, get_trial_warning_level, create_trial_expired_page_context


@login_required
def trial_status(request):
    """Get trial status for the current user's tenant"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
    
    tenant = request.user.tenant
    
    try:
        subscription = tenant.subscription
        trial_info = {
            'is_trial': subscription.status == 'trial',
            'trial_active': subscription.is_trial_active,
            'days_left': subscription.days_left_in_trial,
            'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None,
            'plan_name': subscription.plan.display_name,
            'features': subscription.plan.features,
            'max_products': subscription.plan.max_products,
            'max_users': subscription.plan.max_users,
        }
        
        return JsonResponse({
            'success': True,
            'trial_info': trial_info
        })
        
    except Subscription.DoesNotExist:
        return JsonResponse({
            'success': True,
            'trial_info': {
                'is_trial': False,
                'trial_active': False,
                'days_left': 0,
                'trial_end': None,
                'plan_name': 'No Plan',
                'features': [],
                'max_products': 0,
                'max_users': 0,
            }
        })


@login_required
def upgrade_trial(request):
    """Upgrade from trial to paid subscription"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
    
    tenant = request.user.tenant
    
    try:
        subscription = tenant.subscription
        
        if subscription.status != 'trial':
            return JsonResponse({'error': 'No active trial found.'}, status=400)
        
        # Redirect to payment setup
        return JsonResponse({
            'success': True,
            'redirect_url': '/tenants/payment/setup/'
        })
        
    except Subscription.DoesNotExist:
        return JsonResponse({'error': 'No subscription found.'}, status=400)


@login_required
def extend_trial(request):
    """Extend trial period (admin function)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied.'}, status=403)
    
    tenant_id = request.POST.get('tenant_id')
    days = int(request.POST.get('days', 7))
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    try:
        subscription = tenant.subscription
        
        if subscription.status == 'trial':
            # Extend trial
            subscription.trial_end = subscription.trial_end + timedelta(days=days)
            subscription.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Trial extended by {days} days.',
                'new_end_date': subscription.trial_end.isoformat()
            })
        else:
            return JsonResponse({'error': 'Tenant is not on trial.'}, status=400)
            
    except Subscription.DoesNotExist:
        return JsonResponse({'error': 'No subscription found.'}, status=400)


@login_required
def trial_dashboard(request):
    """Trial dashboard with usage statistics"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        return JsonResponse({'error': 'No tenant associated with your account.'}, status=400)
    
    tenant = request.user.tenant
    
    try:
        subscription = tenant.subscription
        
        # Get usage statistics
        from products.models import Product
        from inventory.models import StockItem
        from orders.models import Order
        
        usage_stats = {
            'products_count': Product.objects.filter(tenant=tenant).count(),
            'inventory_items': StockItem.objects.filter(tenant=tenant).count(),
            'orders_count': Order.objects.filter(tenant=tenant).count(),
            'users_count': tenant.user_count,
        }
        
        # Check if approaching limits
        plan = subscription.plan
        warnings = []
        
        if plan.max_products and usage_stats['products_count'] >= plan.max_products * 0.8:
            warnings.append(f'Approaching product limit ({usage_stats["products_count"]}/{plan.max_products})')
        
        if plan.max_users and usage_stats['users_count'] >= plan.max_users * 0.8:
            warnings.append(f'Approaching user limit ({usage_stats["users_count"]}/{plan.max_users})')
        
        return JsonResponse({
            'success': True,
            'usage_stats': usage_stats,
            'plan_limits': {
                'max_products': plan.max_products,
                'max_users': plan.max_users,
            },
            'warnings': warnings,
            'trial_info': {
                'is_trial': subscription.status == 'trial',
                'days_left': subscription.days_left_in_trial,
                'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None,
            }
        })
        
    except Subscription.DoesNotExist:
        return JsonResponse({'error': 'No subscription found.'}, status=400)


@login_required
def trial_expired(request):
    """Show trial expired page"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        return redirect('/tenants/signin/')
    
    tenant = request.user.tenant
    context = create_trial_expired_page_context(tenant)
    
    return render(request, 'tenants/trial_expired.html', context)
