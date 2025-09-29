"""
Admin approval views for subscriptions
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q

from .payment_models import Subscription, SubscriptionPlan
from .models import Tenant


@staff_member_required
def pending_subscriptions(request):
    """List all subscriptions pending approval"""
    pending_subs = Subscription.objects.filter(
        status='pending_approval',
        requires_approval=True
    ).select_related('tenant', 'plan').order_by('-created_at')
    
    context = {
        'pending_subscriptions': pending_subs,
        'title': 'Pending Subscription Approvals'
    }
    return render(request, 'admin/pending_subscriptions.html', context)


@staff_member_required
@require_http_methods(["POST"])
def approve_subscription(request, subscription_id):
    """Approve a subscription"""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if subscription.status != 'pending_approval':
        return JsonResponse({'error': 'Subscription is not pending approval.'}, status=400)
    
    # Update subscription status
    subscription.status = 'active'
    subscription.approved_by = request.user
    subscription.approved_at = timezone.now()
    subscription.requires_approval = False
    subscription.save()
    
    # Update tenant status
    tenant = subscription.tenant
    tenant.subscription_status = 'active'
    tenant.save()
    
    # Send notification email (implement later)
    # send_approval_notification(tenant, subscription)
    
    messages.success(request, f'Subscription for {tenant.name} has been approved.')
    
    return JsonResponse({
        'success': True,
        'message': 'Subscription approved successfully.'
    })


@staff_member_required
@require_http_methods(["POST"])
def reject_subscription(request, subscription_id):
    """Reject a subscription"""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if subscription.status != 'pending_approval':
        return JsonResponse({'error': 'Subscription is not pending approval.'}, status=400)
    
    # Get rejection reason
    rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
    
    # Update subscription status
    subscription.status = 'canceled'
    subscription.approved_by = request.user
    subscription.approved_at = timezone.now()
    subscription.approval_notes = f'Rejected: {rejection_reason}'
    subscription.requires_approval = False
    subscription.save()
    
    # Update tenant status
    tenant = subscription.tenant
    tenant.subscription_status = 'rejected'
    tenant.save()
    
    # Send rejection notification email (implement later)
    # send_rejection_notification(tenant, subscription, rejection_reason)
    
    messages.warning(request, f'Subscription for {tenant.name} has been rejected.')
    
    return JsonResponse({
        'success': True,
        'message': 'Subscription rejected successfully.'
    })


@staff_member_required
def subscription_details(request, subscription_id):
    """View detailed subscription information"""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    # Get tenant usage statistics
    from products.models import Product
    from inventory.models import StockItem
    from orders.models import Order
    
    tenant = subscription.tenant
    usage_stats = {
        'products_count': Product.objects.filter(tenant=tenant).count(),
        'inventory_items': StockItem.objects.filter(tenant=tenant).count(),
        'orders_count': Order.objects.filter(tenant=tenant).count(),
        'users_count': tenant.user_count,
    }
    
    context = {
        'subscription': subscription,
        'tenant': tenant,
        'usage_stats': usage_stats,
        'title': f'Subscription Details - {tenant.name}'
    }
    return render(request, 'admin/subscription_details.html', context)


@staff_member_required
def subscription_analytics(request):
    """Analytics dashboard for subscription management"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Subscription statistics
    total_subscriptions = Subscription.objects.count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    pending_subscriptions = Subscription.objects.filter(status='pending_approval').count()
    trial_subscriptions = Subscription.objects.filter(status='trial').count()
    
    # Recent activity
    recent_approvals = Subscription.objects.filter(
        approved_at__gte=start_date,
        status='active'
    ).select_related('tenant', 'plan', 'approved_by').order_by('-approved_at')[:10]
    
    # Plan distribution
    plan_distribution = Subscription.objects.filter(
        status__in=['active', 'trial']
    ).values('plan__display_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly trends
    monthly_trends = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        monthly_count = Subscription.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'count': monthly_count
        })
    
    monthly_trends.reverse()
    
    context = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'recent_approvals': recent_approvals,
        'plan_distribution': plan_distribution,
        'monthly_trends': monthly_trends,
        'title': 'Subscription Analytics'
    }
    return render(request, 'admin/subscription_analytics.html', context)
