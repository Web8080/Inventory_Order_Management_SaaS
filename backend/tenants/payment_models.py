"""
Payment models for subscription management
"""

from django.db import models
from django.contrib.auth import get_user_model
from .models import Tenant

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans available for tenants"""
    
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    max_products = models.IntegerField(null=True, blank=True)  # None = unlimited
    max_users = models.IntegerField(null=True, blank=True)  # None = unlimited
    features = models.JSONField(default=list)  # List of features
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.display_name} - ${self.price_monthly}/month"
    
    @property
    def is_unlimited_products(self):
        return self.max_products is None


class Subscription(models.Model):
    """Tenant subscription information"""
    
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('pending_approval', 'Pending Admin Approval'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    
    # Stripe information
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    
    # Trial information
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Billing information
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Admin approval
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey('tenants.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_subscriptions')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tenant.name} - {self.plan.display_name}"
    
    @property
    def is_trial_active(self):
        if not self.trial_end:
            return False
        from django.utils import timezone
        return timezone.now() < self.trial_end
    
    @property
    def is_active(self):
        return self.status in ['trial', 'active']
    
    @property
    def days_left_in_trial(self):
        if not self.is_trial_active:
            return 0
        from django.utils import timezone
        delta = self.trial_end - timezone.now()
        return delta.days


class PaymentMethod(models.Model):
    """Payment methods for tenants"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payment_methods')
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20)  # card, bank_account, etc.
    is_default = models.BooleanField(default=False)
    
    # Card information (if applicable)
    brand = models.CharField(max_length=20, blank=True)  # visa, mastercard, etc.
    last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.brand and self.last4:
            return f"{self.brand.upper()} ****{self.last4}"
        return f"Payment Method {self.id}"


class Invoice(models.Model):
    """Invoice records for subscriptions"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    
    # Stripe information
    stripe_invoice_id = models.CharField(max_length=100, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Invoice details
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Dates
    invoice_date = models.DateTimeField()
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # PDF and receipt
    invoice_pdf_url = models.URLField(blank=True)
    receipt_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} - {self.tenant.name}"
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def is_overdue(self):
        if not self.due_date or self.is_paid:
            return False
        from django.utils import timezone
        return timezone.now() > self.due_date


class UsageRecord(models.Model):
    """Usage tracking for billing"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='usage_records')
    metric = models.CharField(max_length=50)  # products, users, api_calls, etc.
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tenant.name} - {self.metric}: {self.quantity}"
    
    class Meta:
        ordering = ['-timestamp']
