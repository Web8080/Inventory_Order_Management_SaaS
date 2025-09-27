from django.contrib import admin
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count


@staff_member_required
def custom_admin_index(request):
    """Custom admin index with dashboard buttons and stats"""
    
    # Import models here to avoid circular imports
    from tenants.models import Tenant, User
    from products.models import Product
    from orders.models import Order
    from inventory.models import StockItem
    from integrations.models import Integration
    
    # Calculate quick stats
    try:
        total_tenants = Tenant.objects.count()
        total_users = User.objects.filter(is_active=True).count()
        total_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
    except Exception as e:
        # If there are any database issues, set defaults
        total_tenants = 0
        total_users = 0
        total_products = 0
        total_orders = 0
    
    # Get the default admin index context
    app_list = admin.site.get_app_list(request)
    
    context = {
        'total_tenants': total_tenants,
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'title': 'Site administration',
        'app_list': app_list,
        'user': request.user,
        'has_permission': request.user.has_perm('admin.view_admin'),
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
        'site_url': admin.site.site_url,
        'is_popup': False,
        'is_nav_sidebar_enabled': False,
    }
    
    return render(request, 'admin/admin_index.html', context)


# Override the admin site's index view
admin.site.index_template = 'admin/admin_index.html'
admin.site.index = custom_admin_index
