from rest_framework import serializers
from .models import (
    Integration, IntegrationMapping, IntegrationSync, 
    IntegrationWebhook, IntegrationLog, ShopifyStore, WooCommerceStore
)


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Integration model"""
    
    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'integration_type', 'status', 'is_enabled',
            'auto_sync_products', 'auto_sync_orders', 'auto_sync_inventory',
            'sync_frequency_minutes', 'last_sync_at', 'last_sync_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']


class IntegrationMappingSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationMapping model"""
    
    class Meta:
        model = IntegrationMapping
        fields = [
            'id', 'mapping_type', 'local_field', 'external_field',
            'transformation', 'is_required', 'default_value'
        ]


class IntegrationSyncSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationSync model"""
    
    class Meta:
        model = IntegrationSync
        fields = [
            'id', 'sync_type', 'direction', 'status', 'started_at',
            'completed_at', 'records_processed', 'records_successful',
            'records_failed', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IntegrationWebhookSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationWebhook model"""
    
    class Meta:
        model = IntegrationWebhook
        fields = [
            'id', 'event_type', 'external_id', 'status', 'processed_at',
            'error_message', 'retry_count', 'received_at'
        ]
        read_only_fields = ['id', 'received_at']


class ShopifyStoreSerializer(serializers.ModelSerializer):
    """Serializer for ShopifyStore model"""
    
    class Meta:
        model = ShopifyStore
        fields = [
            'id', 'shop_domain', 'shop_name', 'shop_email', 'shop_phone',
            'shop_currency', 'shop_timezone', 'auto_fulfill_orders',
            'sync_inventory_levels', 'sync_product_updates',
            'webhook_orders_create', 'webhook_orders_updated',
            'webhook_orders_paid', 'webhook_orders_cancelled',
            'webhook_products_create', 'webhook_products_update',
            'webhook_inventory_levels_update', 'connected_at', 'last_sync_at'
        ]
        read_only_fields = ['id', 'connected_at', 'last_sync_at']


class WooCommerceStoreSerializer(serializers.ModelSerializer):
    """Serializer for WooCommerceStore model"""
    
    class Meta:
        model = WooCommerceStore
        fields = [
            'id', 'store_url', 'store_name', 'store_description',
            'store_currency', 'auto_fulfill_orders', 'sync_inventory_levels',
            'sync_product_updates', 'webhook_orders_created',
            'webhook_orders_updated', 'webhook_orders_deleted',
            'webhook_products_created', 'webhook_products_updated',
            'webhook_products_deleted', 'connected_at', 'last_sync_at'
        ]
        read_only_fields = ['id', 'connected_at', 'last_sync_at']

