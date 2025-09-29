"""
Middleware for trial access control and tenant management
"""

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from threading import local

from .trial_management import is_access_allowed, check_trial_status, get_trial_warning_level

# Thread-local storage for current tenant
_thread_locals = local()


def get_current_tenant():
    """Get the current tenant from thread-local storage"""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage"""
    _thread_locals.tenant = tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Legacy tenant middleware for backward compatibility
    """
    
    def process_request(self, request):
        # Set current tenant for authenticated users
        if request.user.is_authenticated and hasattr(request.user, 'tenant') and request.user.tenant:
            set_current_tenant(request.user.tenant)
        return None


class TrialAccessMiddleware(MiddlewareMixin):
    """
    Middleware to check trial status and restrict access for expired trials
    """
    
    # URLs that are always allowed (don't require trial access)
    ALLOWED_URLS = [
        '/tenants/signin/',
        '/tenants/signup/',
        '/tenants/payment/',
        '/tenants/legal/',
        '/admin/',
        '/api/auth/',
        '/static/',
        '/media/',
    ]
    
    # URLs that should redirect to trial expired page
    TRIAL_EXPIRED_URLS = [
        '/tenants/trial-expired/',
        '/tenants/payment/setup/',
    ]
    
    def process_request(self, request):
        # Skip middleware for anonymous users
        if not request.user.is_authenticated:
            return None
            
        # Skip middleware for admin users
        if request.user.is_staff:
            return None
            
        # Skip middleware for allowed URLs
        if any(request.path.startswith(url) for url in self.ALLOWED_URLS):
            return None
            
        # Skip middleware for trial expired URLs
        if any(request.path.startswith(url) for url in self.TRIAL_EXPIRED_URLS):
            return None
        
        # Check if user has a tenant
        if not hasattr(request.user, 'tenant') or not request.user.tenant:
            return None
            
        tenant = request.user.tenant
        
        # Check trial status
        if not is_access_allowed(tenant):
            # Trial expired or no access - redirect to trial expired page
            return redirect('/tenants/trial-expired/')
            
        return None
    
    def process_response(self, request, response):
        # Add trial status to response headers for frontend
        if (request.user.is_authenticated and 
            hasattr(request.user, 'tenant') and 
            request.user.tenant and
            not request.user.is_staff):
            
            tenant = request.user.tenant
            trial_status = check_trial_status(tenant)
            warning_level = get_trial_warning_level(tenant)
            
            # Add trial info to response headers
            response['X-Trial-Status'] = trial_status['status']
            response['X-Trial-Days-Remaining'] = str(trial_status['days_remaining'] or 0)
            response['X-Trial-Warning-Level'] = warning_level
        
        # Clean up thread-local storage
        if hasattr(_thread_locals, 'tenant'):
            delattr(_thread_locals, 'tenant')
            
        return response