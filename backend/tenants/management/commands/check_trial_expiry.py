"""
Management command to check and expire trials automatically
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from tenants.models import Tenant
from tenants.payment_models import Subscription


class Command(BaseCommand):
    help = 'Check and expire trials that have passed their end date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be expired without actually expiring them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        # Find trials that should be expired
        expired_trials = Subscription.objects.filter(
            status='trial',
            trial_end__lt=now
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would expire {expired_trials.count()} trials')
            )
            
            for subscription in expired_trials:
                tenant = subscription.tenant
                self.stdout.write(
                    f'  - {tenant.name} (trial ended: {subscription.trial_end})'
                )
        else:
            expired_count = 0
            
            for subscription in expired_trials:
                # Update subscription status
                subscription.status = 'expired'
                subscription.save()
                
                # Update tenant status
                tenant = subscription.tenant
                tenant.subscription_status = 'expired'
                tenant.save()
                
                expired_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Expired trial for {tenant.name}')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully expired {expired_count} trials')
            )
        
        # Also check for trials expiring soon (within 3 days)
        soon_expiring = Subscription.objects.filter(
            status='trial',
            trial_end__gte=now,
            trial_end__lte=now + timezone.timedelta(days=3)
        )
        
        if soon_expiring.exists():
            self.stdout.write(
                self.style.WARNING(f'{soon_expiring.count()} trials expiring within 3 days:')
            )
            
            for subscription in soon_expiring:
                tenant = subscription.tenant
                days_left = (subscription.trial_end - now).days
                self.stdout.write(
                    f'  - {tenant.name} (expires in {days_left} days)'
                )
