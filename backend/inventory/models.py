import uuid
from django.db import models
from django.utils import timezone
from tenants.managers import TenantAwareModel


class Warehouse(TenantAwareModel):
    """Warehouse locations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warehouses'
        unique_together = ['tenant', 'code']
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default warehouse per tenant
            Warehouse.objects.filter(tenant=self.tenant, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class StockItem(TenantAwareModel):
    """Stock levels for products in warehouses"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_items')
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='stock_items',
        null=True, 
        blank=True
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_items')
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)  # Reserved for pending orders
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_items'
        unique_together = ['tenant', 'product', 'variant', 'warehouse']
        ordering = ['product__name', 'warehouse__name']
    
    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"{self.product.name}{variant_str} - {self.warehouse.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Get available quantity (total - reserved)"""
        return self.quantity - self.reserved_quantity
    
    @property
    def is_low_stock(self):
        """Check if this stock item is low"""
        reorder_point = self.variant.reorder_point if self.variant else self.product.reorder_point
        return self.quantity <= reorder_point


class StockTransaction(TenantAwareModel):
    """Stock movement transactions"""
    
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('reserved', 'Reserved'),
        ('unreserved', 'Unreserved'),
    ]
    
    REASON_CHOICES = [
        ('purchase', 'Purchase Order'),
        ('sale', 'Sales Order'),
        ('return', 'Return'),
        ('adjustment', 'Manual Adjustment'),
        ('transfer', 'Warehouse Transfer'),
        ('damage', 'Damaged Goods'),
        ('expired', 'Expired Goods'),
        ('theft', 'Theft/Loss'),
        ('audit', 'Audit Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_transactions')
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='stock_transactions',
        null=True, 
        blank=True
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # Positive for in, negative for out
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reference_id = models.UUIDField(null=True, blank=True)  # Reference to order, etc.
    reference_type = models.CharField(max_length=50, blank=True, null=True)  # 'order', 'purchase', etc.
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey('tenants.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['warehouse', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name}: {self.quantity}"


class StockAlert(TenantAwareModel):
    """Low stock alerts"""
    
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstock', 'Overstock'),
        ('reorder', 'Reorder Required'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_alerts')
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='stock_alerts',
        null=True, 
        blank=True
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_quantity = models.IntegerField()
    threshold_quantity = models.IntegerField()
    message = models.TextField()
    acknowledged_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['alert_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"
    
    def acknowledge(self, user):
        """Acknowledge the alert"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class StockAdjustment(TenantAwareModel):
    """Manual stock adjustments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_adjustments')
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='stock_adjustments',
        null=True, 
        blank=True
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_adjustments')
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    adjustment_quantity = models.IntegerField()  # Calculated field
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.CASCADE, 
        related_name='requested_adjustments'
    )
    approved_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_adjustments'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_adjustments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Adjustment - {self.product.name}: {self.adjustment_quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate adjustment quantity
        self.adjustment_quantity = self.quantity_after - self.quantity_before
        super().save(*args, **kwargs)
    
    def approve(self, user):
        """Approve the adjustment and create stock transaction"""
        if self.status != 'pending':
            raise ValueError("Only pending adjustments can be approved")
        
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
        
        # Create stock transaction
        StockTransaction.objects.create(
            product=self.product,
            variant=self.variant,
            warehouse=self.warehouse,
            transaction_type='adjustment',
            quantity=self.adjustment_quantity,
            reason='adjustment',
            notes=self.notes,
            user=user
        )
        
        # Update stock item
        stock_item, created = StockItem.objects.get_or_create(
            product=self.product,
            variant=self.variant,
            warehouse=self.warehouse,
            defaults={'quantity': 0}
        )
        stock_item.quantity = self.quantity_after
        stock_item.save()
    
    def reject(self, user):
        """Reject the adjustment"""
        if self.status != 'pending':
            raise ValueError("Only pending adjustments can be rejected")
        
        self.status = 'rejected'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()