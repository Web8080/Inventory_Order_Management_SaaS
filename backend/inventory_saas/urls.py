"""
URL configuration for inventory_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .admin_views import admin_dashboard
from .admin_reports import admin_reports, export_sales_report, export_inventory_report, export_tenant_report, export_integration_report
from .admin_index import custom_admin_index  # This will override the admin index
from django.contrib import admin

urlpatterns = [
    # Root URL - redirect to frontend
    path("", lambda request: redirect('http://localhost:5173/'), name="home"),
    
    # Custom admin views (must come before admin.site.urls)
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin/reports/", admin_reports, name="admin_reports"),
    path("admin/reports/export/sales/", export_sales_report, name="export_sales_report"),
    path("admin/reports/export/inventory/", export_inventory_report, name="export_inventory_report"),
    path("admin/reports/export/tenants/", export_tenant_report, name="export_tenant_report"),
    path("admin/reports/export/integrations/", export_integration_report, name="export_integration_report"),
    
    # Django admin - handle both with and without trailing slash
    path("admin", lambda request: redirect('/admin/'), name="admin_redirect"),
    path("admin/", admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/auth/', include('tenants.urls')),
    # path('api/products/', include('products.urls')),
    # path('api/orders/', include('orders.urls')),
    # path('api/inventory/', include('inventory.urls')),
    # path('api/integrations/', include('integrations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
