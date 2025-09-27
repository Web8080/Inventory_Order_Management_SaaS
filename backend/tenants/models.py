import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class Tenant(models.Model):
    """Multi-tenant organization model"""
    
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=100, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-z0-9-]+$',
            message='Slug can only contain lowercase letters, numbers, and hyphens'
        )]
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Billing information
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, default='inactive')
    
    # Settings
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=3, default='USD')
    
    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        return self.users.count()
    
    @property
    def is_premium(self):
        return self.plan in ['premium', 'enterprise']


class User(AbstractUser):
    """Extended user model with tenant relationship"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('clerk', 'Clerk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='clerk')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_tenant_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.tenant.name if self.tenant else 'No Tenant'})"
    
    @property
    def is_owner(self):
        return self.role == 'owner' or self.is_tenant_admin
    
    @property
    def can_manage_users(self):
        return self.role in ['owner', 'manager'] or self.is_tenant_admin
    
    @property
    def can_manage_products(self):
        return self.role in ['owner', 'manager', 'clerk']
    
    @property
    def can_manage_orders(self):
        return self.role in ['owner', 'manager', 'clerk']


class Domain(models.Model):
    """Custom domain for tenants"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tenant_domains'
        ordering = ['-is_primary', 'domain']
    
    def __str__(self):
        return f"{self.domain} -> {self.tenant.name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary domain per tenant
            Domain.objects.filter(tenant=self.tenant, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class TenantSettings(models.Model):
    """Tenant-specific settings and configuration"""
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    
    # Inventory settings
    low_stock_threshold = models.IntegerField(default=10)
    auto_reorder_enabled = models.BooleanField(default=False)
    reorder_lead_time_days = models.IntegerField(default=7)
    
    # ML settings
    ml_forecasting_enabled = models.BooleanField(default=True)
    forecast_horizon_days = models.IntegerField(default=30)
    confidence_threshold = models.FloatField(default=0.8)
    
    # Integration settings
    shopify_enabled = models.BooleanField(default=False)
    shopify_webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    woocommerce_enabled = models.BooleanField(default=False)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    low_stock_alerts = models.BooleanField(default=True)
    order_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_settings'
    
    def __str__(self):
        return f"Settings for {self.tenant.name}"