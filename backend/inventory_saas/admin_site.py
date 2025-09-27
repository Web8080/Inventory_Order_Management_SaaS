from django.contrib import admin
from django.urls import path
from .admin_index import custom_admin_index


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with integrated dashboard and reports"""
    
    def get_urls(self):
        """Override to add custom admin index"""
        urls = super().get_urls()
        # Replace the default index with our custom one
        custom_urls = [
            path('', custom_admin_index, name='index'),
        ]
        return custom_urls + urls[1:]  # Skip the default index


# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')

# Register all models with the custom admin site
from django.contrib.auth.models import Group, User as DjangoUser
from django.contrib.auth.admin import GroupAdmin, UserAdmin as DjangoUserAdmin

# Register default Django models
admin_site.register(Group, GroupAdmin)
admin_site.register(DjangoUser, DjangoUserAdmin)

# Register all our custom models
from tenants.admin import TenantAdmin, UserAdmin, DomainAdmin, TenantSettingsAdmin
from tenants.models import Tenant, User, Domain, TenantSettings

admin_site.register(Tenant, TenantAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Domain, DomainAdmin)
admin_site.register(TenantSettings, TenantSettingsAdmin)

from products.admin import CategoryAdmin, SupplierAdmin, ProductAdmin, ProductVariantAdmin, ProductImageAdmin
from products.models import Category, Supplier, Product, ProductVariant, ProductImage

admin_site.register(Category, CategoryAdmin)
admin_site.register(Supplier, SupplierAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(ProductVariant, ProductVariantAdmin)
admin_site.register(ProductImage, ProductImageAdmin)

from orders.admin import OrderAdmin, OrderLineAdmin, OrderStatusHistoryAdmin, OrderFulfillmentAdmin
from orders.models import Order, OrderLine, OrderStatusHistory, OrderFulfillment

admin_site.register(Order, OrderAdmin)
admin_site.register(OrderLine, OrderLineAdmin)
admin_site.register(OrderStatusHistory, OrderStatusHistoryAdmin)
admin_site.register(OrderFulfillment, OrderFulfillmentAdmin)

from inventory.admin import WarehouseAdmin, StockItemAdmin, StockTransactionAdmin
from inventory.models import Warehouse, StockItem, StockTransaction

admin_site.register(Warehouse, WarehouseAdmin)
admin_site.register(StockItem, StockItemAdmin)
admin_site.register(StockTransaction, StockTransactionAdmin)

from integrations.admin import (
    IntegrationAdmin, IntegrationMappingAdmin, IntegrationSyncAdmin,
    IntegrationWebhookAdmin, IntegrationLogAdmin, ShopifyStoreAdmin, WooCommerceStoreAdmin
)
from integrations.models import (
    Integration, IntegrationMapping, IntegrationSync,
    IntegrationWebhook, IntegrationLog, ShopifyStore, WooCommerceStore
)

admin_site.register(Integration, IntegrationAdmin)
admin_site.register(IntegrationMapping, IntegrationMappingAdmin)
admin_site.register(IntegrationSync, IntegrationSyncAdmin)
admin_site.register(IntegrationWebhook, IntegrationWebhookAdmin)
admin_site.register(IntegrationLog, IntegrationLogAdmin)
admin_site.register(ShopifyStore, ShopifyStoreAdmin)
admin_site.register(WooCommerceStore, WooCommerceStoreAdmin)
