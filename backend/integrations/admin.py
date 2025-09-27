from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from .models import (
    Integration, IntegrationMapping, IntegrationSync, 
    IntegrationWebhook, IntegrationLog, ShopifyStore, WooCommerceStore
)


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration_type', 'status', 'is_enabled', 'last_sync_at']
    list_filter = ['integration_type', 'status', 'is_enabled', 'created_at']
    search_fields = ['name', 'integration_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'status', 'is_enabled')
        }),
        ('Connection Details', {
            'fields': ('api_key', 'api_secret', 'webhook_secret', 'base_url'),
            'classes': ('collapse',)
        }),
        ('Sync Settings', {
            'fields': (
                'auto_sync_products', 'auto_sync_orders', 'auto_sync_inventory',
                'sync_frequency_minutes'
            )
        }),
        ('Last Sync', {
            'fields': ('last_sync_at', 'last_sync_status', 'last_sync_error'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'test_connection', 'sync_now', 'export_integration_logs', 
        'reset_integration', 'enable_integration', 'disable_integration'
    ]
    
    def test_connection(self, request, queryset):
        # This would test the integration connection
        self.message_user(request, f'Connection test initiated for {queryset.count()} integrations.')
    test_connection.short_description = "Test connection for selected integrations"
    
    def sync_now(self, request, queryset):
        # This would trigger immediate sync
        self.message_user(request, f'Sync initiated for {queryset.count()} integrations.')
    sync_now.short_description = "Sync selected integrations now"
    
    def export_integration_logs(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="integration_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Integration', 'Level', 'Message', 'Details', 'Created At'])
        
        for integration in queryset:
            for log in integration.logs.all()[:100]:  # Limit to recent logs
                writer.writerow([
                    integration.name,
                    log.level,
                    log.message,
                    str(log.details),
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        return response
    export_integration_logs.short_description = "Export integration logs to CSV"
    
    def reset_integration(self, request, queryset):
        # This would reset integration settings
        self.message_user(request, f'Reset initiated for {queryset.count()} integrations.')
    reset_integration.short_description = "Reset selected integrations"
    
    def enable_integration(self, request, queryset):
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f'{updated} integrations enabled.')
    enable_integration.short_description = "Enable selected integrations"
    
    def disable_integration(self, request, queryset):
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'{updated} integrations disabled.')
    disable_integration.short_description = "Disable selected integrations"


@admin.register(IntegrationMapping)
class IntegrationMappingAdmin(admin.ModelAdmin):
    list_display = ['integration', 'mapping_type', 'local_field', 'external_field', 'is_required']
    list_filter = ['integration__integration_type', 'mapping_type', 'is_required']
    search_fields = ['integration__name', 'local_field', 'external_field']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Mapping Information', {
            'fields': ('integration', 'mapping_type', 'local_field', 'external_field', 'is_required')
        }),
        ('Mapping Rules', {
            'fields': ('transformation', 'default_value'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntegrationSync)
class IntegrationSyncAdmin(admin.ModelAdmin):
    list_display = [
        'integration', 'sync_type', 'status', 'records_processed', 
        'records_successful', 'started_at', 'completed_at'
    ]
    list_filter = ['sync_type', 'status', 'started_at']
    search_fields = ['integration__name', 'sync_type']
    readonly_fields = ['id', 'started_at', 'completed_at', 'created_at']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('integration', 'sync_type', 'status')
        }),
        ('Sync Results', {
            'fields': ('records_processed', 'records_successful', 'records_failed', 'error_message')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntegrationWebhook)
class IntegrationWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'integration', 'event_type', 'status', 'received_at', 'processed_at'
    ]
    list_filter = ['event_type', 'status', 'received_at']
    search_fields = ['integration__name', 'event_type', 'payload']
    readonly_fields = ['id', 'received_at', 'processed_at']
    date_hierarchy = 'received_at'
    ordering = ['-received_at']
    
    fieldsets = (
        ('Webhook Information', {
            'fields': ('integration', 'event_type', 'status')
        }),
        ('Payload', {
            'fields': ('payload', 'headers'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('received_at', 'processed_at', 'error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = [
        'integration', 'level', 'message', 'sync', 'webhook', 'created_at'
    ]
    list_filter = ['level', 'integration__integration_type', 'created_at']
    search_fields = ['integration__name', 'message', 'details']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Log Information', {
            'fields': ('integration', 'level', 'message')
        }),
        ('Context', {
            'fields': ('sync', 'webhook', 'details'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShopifyStore)
class ShopifyStoreAdmin(admin.ModelAdmin):
    list_display = [
        'shop_name', 'shop_domain', 'shop_currency', 'connected_at'
    ]
    list_filter = ['shop_currency', 'connected_at']
    search_fields = ['shop_name', 'shop_domain', 'shop_email']
    readonly_fields = ['id', 'connected_at', 'updated_at']
    
    fieldsets = (
        ('Store Information', {
            'fields': ('integration', 'shop_name', 'shop_domain', 'shop_email', 'shop_phone')
        }),
        ('Store Settings', {
            'fields': ('shop_currency', 'shop_timezone'),
            'classes': ('collapse',)
        }),
        ('Authentication', {
            'fields': ('access_token', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'connected_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WooCommerceStore)
class WooCommerceStoreAdmin(admin.ModelAdmin):
    list_display = [
        'store_name', 'store_url', 'store_currency', 'connected_at'
    ]
    list_filter = ['store_currency', 'connected_at']
    search_fields = ['store_name', 'store_url', 'store_description']
    readonly_fields = ['id', 'connected_at', 'updated_at']
    
    fieldsets = (
        ('Store Information', {
            'fields': ('integration', 'store_name', 'store_url', 'store_description')
        }),
        ('Store Settings', {
            'fields': ('store_currency',),
            'classes': ('collapse',)
        }),
        ('Authentication', {
            'fields': ('consumer_key', 'consumer_secret'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'connected_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )