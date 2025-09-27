import uuid
from django.db import models
from django.utils import timezone
from tenants.managers import TenantAwareModel


class Integration(TenantAwareModel):
    """Third-party integrations"""
    
    INTEGRATION_TYPES = [
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('quickbooks', 'QuickBooks'),
        ('xero', 'Xero'),
    ]
    
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # Connection details
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_secret = models.CharField(max_length=255, blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.URLField(blank=True, null=True)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True)
    
    # Sync settings
    auto_sync_products = models.BooleanField(default=True)
    auto_sync_orders = models.BooleanField(default=True)
    auto_sync_inventory = models.BooleanField(default=True)
    sync_frequency_minutes = models.IntegerField(default=60)
    
    # Last sync information
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True, null=True)
    last_sync_error = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integrations'
        unique_together = ['tenant', 'integration_type']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"


class IntegrationMapping(TenantAwareModel):
    """Field mappings between our system and external systems"""
    
    MAPPING_TYPES = [
        ('product', 'Product'),
        ('order', 'Order'),
        ('customer', 'Customer'),
        ('inventory', 'Inventory'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='mappings')
    mapping_type = models.CharField(max_length=20, choices=MAPPING_TYPES)
    local_field = models.CharField(max_length=100)
    external_field = models.CharField(max_length=100)
    transformation = models.CharField(max_length=255, blank=True, null=True)  # JSON transformation rules
    is_required = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_mappings'
        unique_together = ['integration', 'mapping_type', 'local_field']
        ordering = ['mapping_type', 'local_field']
    
    def __str__(self):
        return f"{self.integration.name} - {self.local_field} -> {self.external_field}"


class IntegrationSync(TenantAwareModel):
    """Sync operations between systems"""
    
    SYNC_TYPES = [
        ('products', 'Products'),
        ('orders', 'Orders'),
        ('inventory', 'Inventory'),
        ('customers', 'Customers'),
    ]
    
    DIRECTION_CHOICES = [
        ('import', 'Import'),
        ('export', 'Export'),
        ('bidirectional', 'Bidirectional'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='syncs')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Sync details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Error information
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Sync parameters
    sync_parameters = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_syncs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.integration.name} - {self.get_sync_type_display()} ({self.get_direction_display()})"


class IntegrationWebhook(TenantAwareModel):
    """Webhook events from external systems"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='webhooks')
    event_type = models.CharField(max_length=100)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Webhook data
    payload = models.JSONField()
    headers = models.JSONField(default=dict, blank=True)
    
    # Processing information
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_webhooks'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['integration', 'status']),
            models.Index(fields=['event_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.integration.name} - {self.event_type} ({self.status})"


class IntegrationLog(TenantAwareModel):
    """Integration activity logs"""
    
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # Context
    sync = models.ForeignKey(
        IntegrationSync, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='logs'
    )
    webhook = models.ForeignKey(
        IntegrationWebhook, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='logs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'integration_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['integration', 'level']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.integration.name} - {self.level}: {self.message[:50]}"


class ShopifyStore(TenantAwareModel):
    """Shopify store configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.OneToOneField(Integration, on_delete=models.CASCADE, related_name='shopify_store')
    
    # Store details
    shop_domain = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    shop_email = models.EmailField(blank=True, null=True)
    shop_phone = models.CharField(max_length=20, blank=True, null=True)
    shop_currency = models.CharField(max_length=3, default='USD')
    shop_timezone = models.CharField(max_length=50, default='UTC')
    
    # OAuth tokens
    access_token = models.TextField()
    scope = models.TextField(blank=True, null=True)
    
    # Store settings
    auto_fulfill_orders = models.BooleanField(default=False)
    sync_inventory_levels = models.BooleanField(default=True)
    sync_product_updates = models.BooleanField(default=True)
    
    # Webhook subscriptions
    webhook_orders_create = models.BooleanField(default=True)
    webhook_orders_updated = models.BooleanField(default=True)
    webhook_orders_paid = models.BooleanField(default=True)
    webhook_orders_cancelled = models.BooleanField(default=True)
    webhook_products_create = models.BooleanField(default=True)
    webhook_products_update = models.BooleanField(default=True)
    webhook_inventory_levels_update = models.BooleanField(default=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shopify_stores'
    
    def __str__(self):
        return f"Shopify: {self.shop_name}"


class WooCommerceStore(TenantAwareModel):
    """WooCommerce store configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.OneToOneField(Integration, on_delete=models.CASCADE, related_name='woocommerce_store')
    
    # Store details
    store_url = models.URLField()
    store_name = models.CharField(max_length=255)
    store_description = models.TextField(blank=True, null=True)
    store_currency = models.CharField(max_length=3, default='USD')
    
    # API credentials
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    
    # Store settings
    auto_fulfill_orders = models.BooleanField(default=False)
    sync_inventory_levels = models.BooleanField(default=True)
    sync_product_updates = models.BooleanField(default=True)
    
    # Webhook settings
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    webhook_orders_created = models.BooleanField(default=True)
    webhook_orders_updated = models.BooleanField(default=True)
    webhook_orders_deleted = models.BooleanField(default=True)
    webhook_products_created = models.BooleanField(default=True)
    webhook_products_updated = models.BooleanField(default=True)
    webhook_products_deleted = models.BooleanField(default=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'woocommerce_stores'
    
    def __str__(self):
        return f"WooCommerce: {self.store_name}"