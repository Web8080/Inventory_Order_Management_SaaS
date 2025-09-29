from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Tenant, User, Domain, TenantSettings
from .payment_models import SubscriptionPlan, Subscription, PaymentMethod, Invoice, UsageRecord


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'is_active', 'user_count', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['delete_tenant', 'deactivate_tenant', 'activate_tenant']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'plan', 'is_active')
        }),
        ('Billing', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id', 'subscription_status')
        }),
        ('Settings', {
            'fields': ('timezone', 'currency')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        return obj.user_count
    user_count.short_description = 'Users'
    
    def delete_tenant(self, request, queryset):
        """Delete selected tenants and all their data"""
        deleted_count = 0
        for tenant in queryset:
            # Delete all related data first using correct relationship names
            # Only delete relationships that actually exist
            try:
                tenant.users.all().delete()
            except:
                pass
                
            try:
                tenant.product_set.all().delete()
            except:
                pass
                
            try:
                tenant.order_set.all().delete()
            except:
                pass
                
            try:
                tenant.stockitem_set.all().delete()
            except:
                pass
                
            try:
                tenant.warehouse_set.all().delete()
            except:
                pass
                
            try:
                tenant.category_set.all().delete()
            except:
                pass
                
            try:
                tenant.supplier_set.all().delete()
            except:
                pass
                
            try:
                tenant.integration_set.all().delete()
            except:
                pass
                
            try:
                tenant.shopifystore_set.all().delete()
            except:
                pass
                
            try:
                tenant.woocommercestore_set.all().delete()
            except:
                pass
                
            # Payment models (these have specific relationship names)
            try:
                if hasattr(tenant, 'subscription'):
                    tenant.subscription.delete()
            except:
                pass
                
            try:
                tenant.payment_methods.all().delete()
            except:
                pass
                
            try:
                tenant.invoices.all().delete()
            except:
                pass
                
            try:
                tenant.usage_records.all().delete()
            except:
                pass
                
            try:
                tenant.domain_set.all().delete()
            except:
                pass
            
            # Delete tenant settings
            try:
                if hasattr(tenant, 'settings'):
                    tenant.settings.delete()
            except:
                pass
            
            # Delete the tenant
            tenant.delete()
            deleted_count += 1
        
        self.message_user(request, f'Successfully deleted {deleted_count} tenant(s) and all their data.')
    delete_tenant.short_description = "Delete selected tenants and all their data"
    
    def deactivate_tenant(self, request, queryset):
        """Deactivate selected tenants"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} tenant(s).')
    deactivate_tenant.short_description = "Deactivate selected tenants"
    
    def activate_tenant(self, request, queryset):
        """Activate selected tenants"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} tenant(s).')
    activate_tenant.short_description = "Activate selected tenants"
    
    def delete_model(self, request, obj):
        """Handle individual tenant deletion"""
        # Delete all related data first using correct relationship names
        # Only delete relationships that actually exist
        try:
            obj.users.all().delete()
        except:
            pass
            
        try:
            obj.product_set.all().delete()
        except:
            pass
            
        try:
            obj.order_set.all().delete()
        except:
            pass
            
        try:
            obj.stockitem_set.all().delete()
        except:
            pass
            
        try:
            obj.warehouse_set.all().delete()
        except:
            pass
            
        try:
            obj.category_set.all().delete()
        except:
            pass
            
        try:
            obj.supplier_set.all().delete()
        except:
            pass
            
        try:
            obj.integration_set.all().delete()
        except:
            pass
            
        try:
            obj.shopifystore_set.all().delete()
        except:
            pass
            
        try:
            obj.woocommercestore_set.all().delete()
        except:
            pass
            
        # Payment models (these have specific relationship names)
        try:
            if hasattr(obj, 'subscription'):
                obj.subscription.delete()
        except:
            pass
            
        try:
            obj.payment_methods.all().delete()
        except:
            pass
            
        try:
            obj.invoices.all().delete()
        except:
            pass
            
        try:
            obj.usage_records.all().delete()
        except:
            pass
            
        try:
            obj.domain_set.all().delete()
        except:
            pass
        
        # Delete tenant settings
        try:
            if hasattr(obj, 'settings'):
                obj.settings.delete()
        except:
            pass
        
        # Delete the tenant
        super().delete_model(request, obj)
        self.message_user(request, f'Successfully deleted tenant "{obj.name}" and all its data.')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'tenant', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Tenant & Role', {'fields': ('tenant', 'role', 'is_tenant_admin')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant', 'role'),
        }),
    )
    
    ordering = ['email']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary', 'is_verified', 'created_at']
    list_filter = ['is_primary', 'is_verified', 'created_at']
    search_fields = ['domain', 'tenant__name']
    readonly_fields = ['created_at']


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'low_stock_threshold', 'ml_forecasting_enabled', 'shopify_enabled']
    list_filter = ['ml_forecasting_enabled', 'shopify_enabled', 'woocommerce_enabled']
    search_fields = ['tenant__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Inventory Settings', {
            'fields': ('low_stock_threshold', 'auto_reorder_enabled', 'reorder_lead_time_days')
        }),
        ('ML Settings', {
            'fields': ('ml_forecasting_enabled', 'forecast_horizon_days', 'confidence_threshold')
        }),
        ('Integration Settings', {
            'fields': ('shopify_enabled', 'shopify_webhook_secret', 'woocommerce_enabled')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'low_stock_alerts', 'order_notifications')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'price_monthly', 'price_yearly', 'max_products', 'max_users', 'is_active']
    list_filter = ['is_active', 'name']
    search_fields = ['display_name', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'plan', 'status', 'billing_cycle', 'is_active', 'trial_end', 'current_period_end']
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['tenant__name', 'stripe_customer_id', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_customer_id', 'stripe_subscription_id']
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'type', 'brand', 'last4', 'is_default', 'created_at']
    list_filter = ['type', 'brand', 'is_default']
    search_fields = ['tenant__name', 'stripe_payment_method_id']
    readonly_fields = ['created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'subscription', 'amount_due', 'amount_paid', 'status', 'invoice_date', 'is_paid']
    list_filter = ['status', 'currency', 'invoice_date']
    search_fields = ['tenant__name', 'stripe_invoice_id']
    readonly_fields = ['created_at', 'updated_at', 'stripe_invoice_id']
    
    def is_paid(self, obj):
        return obj.is_paid
    is_paid.boolean = True


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'metric', 'quantity', 'timestamp']
    list_filter = ['metric', 'timestamp']
    search_fields = ['tenant__name']
    readonly_fields = ['timestamp']