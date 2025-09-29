"""
Management command to set up default subscription plans
"""

from django.core.management.base import BaseCommand
from tenants.payment_models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Set up default subscription plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'starter',
                'display_name': 'Starter Plan',
                'description': 'Perfect for small businesses getting started with inventory management.',
                'price_monthly': 29.00,
                'price_yearly': 278.40,  # 20% discount
                'max_products': 1000,
                'max_users': 2,
                'features': [
                    'Up to 1,000 products',
                    '2 user accounts',
                    'Basic inventory tracking',
                    'Order management',
                    'Email support',
                    'Mobile app access',
                    'Basic reporting',
                    'CSV import/export'
                ],
                'stripe_price_id_monthly': 'price_starter_monthly',
                'stripe_price_id_yearly': 'price_starter_yearly',
            },
            {
                'name': 'professional',
                'display_name': 'Professional Plan',
                'description': 'Advanced features for growing businesses with AI-powered insights.',
                'price_monthly': 79.00,
                'price_yearly': 758.40,  # 20% discount
                'max_products': 10000,
                'max_users': 10,
                'features': [
                    'Up to 10,000 products',
                    '10 user accounts',
                    'AI-powered demand forecasting',
                    'Advanced analytics & reporting',
                    'Priority email support',
                    'API access',
                    'Third-party integrations',
                    'Advanced inventory optimization',
                    'Multi-warehouse support',
                    'Custom fields & categories',
                    'Automated reorder points',
                    'Performance dashboards'
                ],
                'stripe_price_id_monthly': 'price_professional_monthly',
                'stripe_price_id_yearly': 'price_professional_yearly',
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise Plan',
                'description': 'Complete solution for large enterprises with custom features.',
                'price_monthly': 199.00,
                'price_yearly': 1910.40,  # 20% discount
                'max_products': None,  # Unlimited
                'max_users': None,  # Unlimited
                'features': [
                    'Unlimited products',
                    'Unlimited users',
                    'Advanced AI & machine learning',
                    'Custom integrations',
                    '24/7 phone & email support',
                    'Dedicated account manager',
                    'Custom reporting & dashboards',
                    'White-label options',
                    'Advanced security features',
                    'SSO integration',
                    'Custom workflows',
                    'Priority feature requests',
                    'Training & onboarding',
                    'SLA guarantee'
                ],
                'stripe_price_id_monthly': 'price_enterprise_monthly',
                'stripe_price_id_yearly': 'price_enterprise_yearly',
            }
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully set up subscription plans!')
        )
