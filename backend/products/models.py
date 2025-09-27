import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from tenants.managers import TenantAwareModel


class Category(TenantAwareModel):
    """Product categories"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        unique_together = ['tenant', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """Get the full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Supplier(TenantAwareModel):
    """Product suppliers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
        unique_together = ['tenant', 'name']
    
    def __str__(self):
        return self.name


class Product(TenantAwareModel):
    """Product catalog"""
    
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('lb', 'Pound'),
        ('liter', 'Liter'),
        ('gallon', 'Gallon'),
        ('box', 'Box'),
        ('case', 'Case'),
        ('dozen', 'Dozen'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pricing
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margin_percentage = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Inventory settings
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    reorder_point = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)
    max_stock_level = models.IntegerField(null=True, blank=True)
    
    # Product details
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)  # LxWxH
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_tracked = models.BooleanField(default=True)  # Whether to track inventory
    
    # Images
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['name']
        unique_together = ['tenant', 'sku']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def current_stock(self):
        """Get current stock level"""
        if not self.is_tracked:
            return None
        return self.stock_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        if not self.is_tracked:
            return False
        return self.current_stock <= self.reorder_point
    
    @property
    def stock_value(self):
        """Calculate total stock value"""
        if not self.is_tracked:
            return 0
        return self.current_stock * self.cost_price
    
    def calculate_margin(self):
        """Calculate margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Auto-calculate margin on save"""
        if self.cost_price and self.selling_price:
            self.margin_percentage = self.calculate_margin()
        super().save(*args, **kwargs)


class ProductVariant(TenantAwareModel):
    """Product variants (size, color, etc.)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)  # e.g., "Red", "Large", "XL"
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reorder_point = models.IntegerField(null=True, blank=True)
    reorder_quantity = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
        unique_together = ['tenant', 'sku']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def current_stock(self):
        """Get current stock level for this variant"""
        return self.stock_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0


class ProductImage(TenantAwareModel):
    """Product images"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per product
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)