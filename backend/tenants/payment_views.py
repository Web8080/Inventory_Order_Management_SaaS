"""
Payment views for Stripe integration
"""

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json

from .models import Tenant
from .payment_models import SubscriptionPlan, Subscription, PaymentMethod, Invoice

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')


@login_required
def pending_approval(request):
    """Show pending approval page after payment"""
    tenant = request.user.tenant
    try:
        subscription = tenant.subscription
        context = {
            'tenant': tenant,
            'subscription': subscription,
        }
        return render(request, 'tenants/pending_approval.html', context)
    except Subscription.DoesNotExist:
        messages.error(request, "No subscription found.")
        return redirect('payment_setup')


@login_required
def payment_setup(request):
    """Payment setup page for new tenants"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        messages.error(request, 'No tenant associated with your account.')
        return redirect('/')
    
    tenant = request.user.tenant
    
    # Get available plans
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    # Check if tenant already has a subscription
    try:
        subscription = tenant.subscription
        if subscription.is_active:
            messages.info(request, 'You already have an active subscription.')
            return redirect('subscription_management')
    except Subscription.DoesNotExist:
        pass
    
    context = {
        'tenant': tenant,
        'plans': plans,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_...'),
    }
    
    return render(request, 'tenants/payment_setup.html', context)


@login_required
@require_http_methods(["POST"])
def create_subscription(request):
    """Create a new subscription with Stripe"""
    try:
        tenant = request.user.tenant
        plan_id = request.POST.get('plan_id')
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        payment_method_id = request.POST.get('payment_method_id')
        
        if not all([plan_id, payment_method_id]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Get the plan
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        
        # Create or get Stripe customer
        if not tenant.subscription.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=tenant.name,
                metadata={
                    'tenant_id': str(tenant.id),
                    'user_id': str(request.user.id),
                }
            )
            stripe_customer_id = customer.id
        else:
            stripe_customer_id = tenant.subscription.stripe_customer_id
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=stripe_customer_id,
        )
        
        # Set as default payment method
        stripe.Customer.modify(
            stripe_customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )
        
        # Get the appropriate price ID
        if billing_cycle == 'yearly':
            price_id = plan.stripe_price_id_yearly
        else:
            price_id = plan.stripe_price_id_monthly
        
        # Check if this is a trial signup (no payment required)
        is_trial_signup = request.POST.get('is_trial', 'false').lower() == 'true'
        
        if is_trial_signup:
            # Create trial subscription (no Stripe payment required)
            trial_end = timezone.now() + timedelta(days=14)  # 14-day trial
            
            # Create local subscription record for trial
            local_subscription, created = Subscription.objects.get_or_create(
                tenant=tenant,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'stripe_customer_id': stripe_customer_id,
                    'stripe_subscription_id': f'trial_{tenant.id}_{int(timezone.now().timestamp())}',
                    'stripe_payment_method_id': payment_method_id,
                    'trial_start': timezone.now(),
                    'trial_end': trial_end,
                    'current_period_start': timezone.now(),
                    'current_period_end': trial_end,
                    'status': 'trial',
                    'requires_approval': False,
                }
            )
            
            return JsonResponse({
                'success': True,
                'subscription_id': local_subscription.stripe_subscription_id,
                'is_trial': True,
                'redirect_url': '/tenants/trial/success/'
            })
        else:
            # Create paid subscription with Stripe
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{
                    'price': price_id,
                }],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
        
            # Create or update local subscription record for paid plan
            local_subscription, created = Subscription.objects.get_or_create(
                tenant=tenant,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'stripe_customer_id': stripe_customer_id,
                    'stripe_subscription_id': subscription.id,
                    'stripe_payment_method_id': payment_method_id,
                    'current_period_start': timezone.datetime.fromtimestamp(subscription.current_period_start),
                    'current_period_end': timezone.datetime.fromtimestamp(subscription.current_period_end),
                    'status': 'pending_approval',  # Requires admin approval
                    'requires_approval': True,
                }
            )
        
            if not created:
                # Update existing subscription
                local_subscription.plan = plan
                local_subscription.billing_cycle = billing_cycle
                local_subscription.stripe_customer_id = stripe_customer_id
                local_subscription.stripe_subscription_id = subscription.id
                local_subscription.stripe_payment_method_id = payment_method_id
                local_subscription.current_period_start = timezone.datetime.fromtimestamp(subscription.current_period_start)
                local_subscription.current_period_end = timezone.datetime.fromtimestamp(subscription.current_period_end)
                local_subscription.status = 'pending_approval'
                local_subscription.requires_approval = True
                local_subscription.save()
        
        # Save payment method
        payment_method_obj, created = PaymentMethod.objects.get_or_create(
            stripe_payment_method_id=payment_method_id,
            defaults={
                'tenant': tenant,
                'type': 'card',
                'is_default': True,
            }
        )
        
        return JsonResponse({
            'success': True,
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret,
            'is_trial': False,
            'redirect_url': '/tenants/payment/pending-approval/'
        })
        
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@login_required
def subscription_management(request):
    """Subscription management page"""
    if not hasattr(request.user, 'tenant') or not request.user.tenant:
        messages.error(request, 'No tenant associated with your account.')
        return redirect('/')
    
    tenant = request.user.tenant
    
    try:
        subscription = tenant.subscription
        payment_methods = tenant.payment_methods.all()
        recent_invoices = tenant.invoices.order_by('-created_at')[:10]
    except Subscription.DoesNotExist:
        subscription = None
        payment_methods = []
        recent_invoices = []
    
    context = {
        'tenant': tenant,
        'subscription': subscription,
        'payment_methods': payment_methods,
        'recent_invoices': recent_invoices,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_...'),
    }
    
    return render(request, 'tenants/subscription_management.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_subscription(request):
    """Cancel subscription at period end"""
    try:
        tenant = request.user.tenant
        subscription = tenant.subscription
        
        if not subscription.stripe_subscription_id:
            return JsonResponse({'error': 'No active subscription found'}, status=400)
        
        # Cancel subscription in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
        )
        
        # Update local record
        subscription.cancel_at_period_end = True
        subscription.save()
        
        return JsonResponse({'success': True})
        
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@login_required
@require_http_methods(["POST"])
def reactivate_subscription(request):
    """Reactivate a canceled subscription"""
    try:
        tenant = request.user.tenant
        subscription = tenant.subscription
        
        if not subscription.stripe_subscription_id:
            return JsonResponse({'error': 'No subscription found'}, status=400)
        
        # Reactivate subscription in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False,
        )
        
        # Update local record
        subscription.cancel_at_period_end = False
        subscription.save()
        
        return JsonResponse({'success': True})
        
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', 'whsec_...')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_invoice_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    
    return JsonResponse({'status': 'success'})


def handle_invoice_payment_succeeded(invoice):
    """Handle successful invoice payment"""
    try:
        # Find the subscription
        subscription = Subscription.objects.get(
            stripe_subscription_id=invoice['subscription']
        )
        
        # Create or update invoice record
        invoice_obj, created = Invoice.objects.get_or_create(
            stripe_invoice_id=invoice['id'],
            defaults={
                'tenant': subscription.tenant,
                'subscription': subscription,
                'amount_due': invoice['amount_due'] / 100,  # Convert from cents
                'amount_paid': invoice['amount_paid'] / 100,
                'currency': invoice['currency'],
                'status': invoice['status'],
                'invoice_date': timezone.datetime.fromtimestamp(invoice['created']),
                'due_date': timezone.datetime.fromtimestamp(invoice['due_date']) if invoice['due_date'] else None,
                'paid_at': timezone.now(),
                'invoice_pdf_url': invoice.get('invoice_pdf'),
                'receipt_url': invoice.get('receipt_url'),
            }
        )
        
        if not created:
            invoice_obj.amount_paid = invoice['amount_paid'] / 100
            invoice_obj.status = invoice['status']
            invoice_obj.paid_at = timezone.now()
            invoice_obj.save()
        
        # Update subscription status
        subscription.status = 'active'
        subscription.save()
        
    except Subscription.DoesNotExist:
        pass


def handle_invoice_payment_failed(invoice):
    """Handle failed invoice payment"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=invoice['subscription']
        )
        subscription.status = 'past_due'
        subscription.save()
    except Subscription.DoesNotExist:
        pass


def handle_subscription_updated(subscription_data):
    """Handle subscription updates"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_data['id']
        )
        
        subscription.current_period_start = timezone.datetime.fromtimestamp(
            subscription_data['current_period_start']
        )
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            subscription_data['current_period_end']
        )
        subscription.status = subscription_data['status']
        subscription.cancel_at_period_end = subscription_data['cancel_at_period_end']
        
        if subscription_data['canceled_at']:
            subscription.canceled_at = timezone.datetime.fromtimestamp(
                subscription_data['canceled_at']
            )
        
        subscription.save()
        
    except Subscription.DoesNotExist:
        pass


def handle_subscription_deleted(subscription_data):
    """Handle subscription deletion"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=subscription_data['id']
        )
        subscription.status = 'canceled'
        subscription.canceled_at = timezone.now()
        subscription.save()
    except Subscription.DoesNotExist:
        pass
