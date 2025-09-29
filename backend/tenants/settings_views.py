"""
Settings views for tenant configuration
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone

from .models import Tenant, TenantSettings


@login_required
def get_tenant_settings(request):
    """Get current tenant settings"""
    tenant = request.user.tenant
    
    # Get or create tenant settings
    settings, created = TenantSettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            'low_stock_threshold': 10,
            'auto_reorder_enabled': False,
            'email_notifications': True,
            'low_stock_alerts': True,
            'order_notifications': True,
        }
    )
    
    return JsonResponse({
        'tenant': {
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'plan': tenant.plan,
            'timezone': tenant.timezone,
            'currency': tenant.currency,
            'created_at': tenant.created_at.isoformat(),
        },
        'user': {
            'id': request.user.id,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': getattr(request.user, 'phone', ''),
            'role': getattr(request.user, 'role', 'owner'),
        },
        'settings': {
            'low_stock_threshold': settings.low_stock_threshold,
            'auto_reorder_enabled': settings.auto_reorder_enabled,
            'reorder_lead_time_days': settings.reorder_lead_time_days,
            'ml_forecasting_enabled': settings.ml_forecasting_enabled,
            'forecast_horizon_days': settings.forecast_horizon_days,
            'confidence_threshold': settings.confidence_threshold,
            'shopify_enabled': settings.shopify_enabled,
            'woocommerce_enabled': settings.woocommerce_enabled,
            'email_notifications': settings.email_notifications,
            'low_stock_alerts': settings.low_stock_alerts,
            'order_notifications': settings.order_notifications,
        }
    })


@login_required
@require_http_methods(["POST"])
def update_tenant_info(request):
    """Update tenant information"""
    tenant = request.user.tenant
    
    try:
        # Update tenant fields
        tenant.name = request.POST.get('company_name', tenant.name)
        tenant.timezone = request.POST.get('timezone', tenant.timezone)
        tenant.currency = request.POST.get('currency', tenant.currency)
        tenant.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Company information updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_user_profile(request):
    """Update user profile information"""
    user = request.user
    
    try:
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        if hasattr(user, 'phone'):
            user.phone = request.POST.get('phone', getattr(user, 'phone', ''))
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_tenant_settings(request):
    """Update tenant settings"""
    tenant = request.user.tenant
    
    try:
        # Get or create tenant settings
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        
        # Update settings fields
        settings.low_stock_threshold = int(request.POST.get('low_stock_threshold', settings.low_stock_threshold))
        settings.auto_reorder_enabled = request.POST.get('auto_reorder_enabled') == 'true'
        settings.reorder_lead_time_days = int(request.POST.get('reorder_lead_time_days', settings.reorder_lead_time_days))
        settings.ml_forecasting_enabled = request.POST.get('ml_forecasting_enabled') == 'true'
        settings.forecast_horizon_days = int(request.POST.get('forecast_horizon_days', settings.forecast_horizon_days))
        settings.confidence_threshold = float(request.POST.get('confidence_threshold', settings.confidence_threshold))
        settings.shopify_enabled = request.POST.get('shopify_enabled') == 'true'
        settings.woocommerce_enabled = request.POST.get('woocommerce_enabled') == 'true'
        settings.email_notifications = request.POST.get('email_notifications') == 'true'
        settings.low_stock_alerts = request.POST.get('low_stock_alerts') == 'true'
        settings.order_notifications = request.POST.get('order_notifications') == 'true'
        settings.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def settings_page(request):
    """Render settings page with real data"""
    tenant = request.user.tenant
    
    # Get or create tenant settings
    settings, created = TenantSettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            'low_stock_threshold': 10,
            'auto_reorder_enabled': False,
            'email_notifications': True,
            'low_stock_alerts': True,
            'order_notifications': True,
        }
    )
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'settings': settings,
    }
    
    return render(request, 'tenants/settings.html', context)
