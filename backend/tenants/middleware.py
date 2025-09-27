from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant requests.
    Extracts tenant information from request and sets it in thread-local storage.
    """
    
    def process_request(self, request):
        """Process the request to identify the tenant"""
        tenant = None
        
        # Try to get tenant from subdomain
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        
        if subdomain and subdomain != 'www' and subdomain != 'localhost':
            try:
                tenant = Tenant.objects.get(slug=subdomain, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        # Try to get tenant from custom domain
        if not tenant:
            try:
                from .models import Domain
                domain = Domain.objects.get(domain=host, is_verified=True)
                tenant = domain.tenant
            except Domain.DoesNotExist:
                pass
        
        # Try to get tenant from header (for API requests)
        if not tenant:
            tenant_header = request.META.get('HTTP_X_TENANT_ID')
            if tenant_header:
                try:
                    tenant = Tenant.objects.get(id=tenant_header, is_active=True)
                except (Tenant.DoesNotExist, ValueError):
                    pass
        
        # Try to get tenant from authenticated user
        if not tenant and hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                tenant = request.user.tenant
        
        # Set tenant in request for use in views
        request.tenant = tenant
        
        # Store in thread-local storage for use in models
        import threading
        _thread_locals = threading.local()
        _thread_locals.tenant = tenant
        
        return None
    
    def process_response(self, request, response):
        """Clean up thread-local storage"""
        import threading
        _thread_locals = threading.local()
        if hasattr(_thread_locals, 'tenant'):
            delattr(_thread_locals, 'tenant')
        return response


def get_current_tenant():
    """Get the current tenant from thread-local storage"""
    import threading
    _thread_locals = threading.local()
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage"""
    import threading
    _thread_locals = threading.local()
    _thread_locals.tenant = tenant
