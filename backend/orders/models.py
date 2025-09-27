import uuid
from django.db import models
from django.utils import timezone
from decimal import Decimal
from tenants.managers import TenantAwareModel


class Order(TenantAwareModel):
    """Orders (sales and purchases)"""
    
    ORDER_TYPES = [
        ('sale', 'Sales Order'),
        ('purchase', 'Purchase Order'),
        ('return', 'Return Order'),
        ('transfer', 'Transfer Order'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Customer/Supplier information
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    
    # Supplier information (for purchase orders)
    supplier = models.ForeignKey(
        'products.Supplier', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    # Financial information
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment information
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    
    # Shipping information
    shipping_address = models.TextField(blank=True, null=True)
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Dates
    order_date = models.DateTimeField(default=timezone.now)
    required_date = models.DateTimeField(null=True, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    
    # Notes and metadata
    notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    # User tracking
    created_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_orders'
    )
    updated_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_orders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_type', 'status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.get_order_type_display()}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not set
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calculate totals
        self.calculate_totals()
        
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number"""
        prefix = {
            'sale': 'SO',
            'purchase': 'PO',
            'return': 'RO',
            'transfer': 'TO',
        }.get(self.order_type, 'OR')
        
        # Get the next number for this tenant and order type
        last_order = Order.objects.filter(
            tenant=self.tenant,
            order_type=self.order_type
        ).order_by('-id').first()
        
        if last_order and last_order.order_number:
            try:
                last_number = int(last_order.order_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}-{next_number:06d}"
    
    def calculate_totals(self):
        """Calculate order totals from line items"""
        lines = self.order_lines.all()
        self.subtotal = sum(line.line_total for line in lines)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount - self.discount_amount
    
    @property
    def line_count(self):
        """Get number of line items"""
        return self.order_lines.count()
    
    @property
    def total_quantity(self):
        """Get total quantity of items"""
        return sum(line.quantity for line in self.order_lines.all())


class OrderLine(TenantAwareModel):
    """Order line items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='order_lines')
    variant = models.ForeignKey(
        'products.ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='order_lines',
        null=True, 
        blank=True
    )
    
    # Quantity and pricing
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Fulfillment
    quantity_fulfilled = models.IntegerField(default=0)
    quantity_shipped = models.IntegerField(default=0)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_lines'
        ordering = ['created_at']
    
    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"{self.order.order_number} - {self.product.name}{variant_str} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate line total
        subtotal = self.quantity * self.unit_price
        if self.discount_percentage > 0:
            self.discount_amount = subtotal * (self.discount_percentage / 100)
        self.line_total = subtotal - self.discount_amount
        
        super().save(*args, **kwargs)
    
    @property
    def remaining_quantity(self):
        """Get remaining quantity to fulfill"""
        return self.quantity - self.quantity_fulfilled
    
    @property
    def is_fully_fulfilled(self):
        """Check if line is fully fulfilled"""
        return self.quantity_fulfilled >= self.quantity


class OrderStatusHistory(TenantAwareModel):
    """Order status change history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, blank=True, null=True)
    to_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey('tenants.User', on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order.order_number}: {self.from_status} -> {self.to_status}"


class OrderFulfillment(TenantAwareModel):
    """Order fulfillment tracking"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='fulfillments')
    warehouse = models.ForeignKey('inventory.Warehouse', on_delete=models.CASCADE, related_name='fulfillments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Shipping information
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_carrier = models.CharField(max_length=100, blank=True, null=True)
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dates
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # User tracking
    fulfilled_by = models.ForeignKey(
        'tenants.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='fulfilled_orders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_fulfillments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.warehouse.name}"


class OrderFulfillmentLine(TenantAwareModel):
    """Fulfillment line items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fulfillment = models.ForeignKey(OrderFulfillment, on_delete=models.CASCADE, related_name='fulfillment_lines')
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name='fulfillment_lines')
    quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_fulfillment_lines'
        unique_together = ['fulfillment', 'order_line']
    
    def __str__(self):
        return f"{self.fulfillment.order.order_number} - {self.order_line.product.name} x{self.quantity}"