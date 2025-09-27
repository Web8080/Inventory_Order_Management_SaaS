from django.db import models
from .middleware import get_current_tenant


class TenantAwareManager(models.Manager):
    """
    Manager that automatically filters querysets by the current tenant.
    """
    
    def get_queryset(self):
        """Filter queryset by current tenant"""
        tenant = get_current_tenant()
        if tenant:
            return super().get_queryset().filter(tenant=tenant)
        return super().get_queryset()
    
    def create(self, **kwargs):
        """Create object with current tenant"""
        tenant = get_current_tenant()
        if tenant and 'tenant' not in kwargs:
            kwargs['tenant'] = tenant
        return super().create(**kwargs)


class TenantAwareModel(models.Model):
    """
    Abstract base model that automatically adds tenant field and filtering.
    """
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    objects = TenantAwareManager()
    all_objects = models.Manager()  # Manager that doesn't filter by tenant
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Auto-assign tenant if not set"""
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
        super().save(*args, **kwargs)
