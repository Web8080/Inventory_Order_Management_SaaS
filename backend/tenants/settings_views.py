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
            'timezone': 'America/New_York',
            'currency': 'USD',
            'date_format': 'MM/DD/YYYY',
            'low_stock_threshold': 10,
            'auto_reorder': False,
            'email_notifications': True,
            'sms_notifications': False,
        }
    )
    
    return JsonResponse({
        'tenant': {
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'industry': tenant.industry,
            'company_size': tenant.company_size,
            'website': tenant.website,
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
            'timezone': settings.timezone,
            'currency': settings.currency,
            'date_format': settings.date_format,
            'low_stock_threshold': settings.low_stock_threshold,
            'auto_reorder': settings.auto_reorder,
            'email_notifications': settings.email_notifications,
            'sms_notifications': settings.sms_notifications,
            'default_reorder_point': settings.default_reorder_point,
            'tax_rate': float(settings.tax_rate) if settings.tax_rate else 0.0,
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
        tenant.industry = request.POST.get('industry', tenant.industry)
        tenant.company_size = request.POST.get('company_size', tenant.company_size)
        tenant.website = request.POST.get('website', tenant.website)
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
        settings.timezone = request.POST.get('timezone', settings.timezone)
        settings.currency = request.POST.get('currency', settings.currency)
        settings.date_format = request.POST.get('date_format', settings.date_format)
        settings.low_stock_threshold = int(request.POST.get('low_stock_threshold', settings.low_stock_threshold))
        settings.auto_reorder = request.POST.get('auto_reorder') == 'true'
        settings.email_notifications = request.POST.get('email_notifications') == 'true'
        settings.sms_notifications = request.POST.get('sms_notifications') == 'true'
        settings.default_reorder_point = int(request.POST.get('default_reorder_point', settings.default_reorder_point))
        settings.tax_rate = float(request.POST.get('tax_rate', settings.tax_rate or 0))
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
            'timezone': 'America/New_York',
            'currency': 'USD',
            'date_format': 'MM/DD/YYYY',
            'low_stock_threshold': 10,
            'auto_reorder': False,
            'email_notifications': True,
            'sms_notifications': False,
        }
    )
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'settings': settings,
    }
    
    return render(request, 'tenants/settings.html', context)
