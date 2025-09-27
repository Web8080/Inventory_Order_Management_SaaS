from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Tenant, User, Domain, TenantSettings


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'is_active', 'user_count', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']
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