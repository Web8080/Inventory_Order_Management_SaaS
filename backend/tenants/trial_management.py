"""
Trial management and access control system
"""

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import timedelta

from .models import Tenant
from .payment_models import Subscription


def check_trial_status(tenant):
    """Check if tenant's trial is active, expired, or needs renewal"""
    try:
        subscription = tenant.subscription
        
        if subscription.status == 'trial':
            now = timezone.now()
            
            if subscription.trial_end and now > subscription.trial_end:
                # Trial expired
                subscription.status = 'expired'
                subscription.save()
                
                # Update tenant status
                tenant.subscription_status = 'expired'
                tenant.save()
                
                return {
                    'status': 'expired',
                    'days_remaining': 0,
                    'trial_end': subscription.trial_end,
                    'message': 'Your free trial has expired. Please upgrade to continue using the platform.'
                }
            else:
                # Trial still active
                days_remaining = (subscription.trial_end - now).days if subscription.trial_end else 0
                
                return {
                    'status': 'active',
                    'days_remaining': max(0, days_remaining),
                    'trial_end': subscription.trial_end,
                    'message': f'Free trial active - {days_remaining} days remaining'
                }
        elif subscription.status == 'active':
            return {
                'status': 'active',
                'days_remaining': None,
                'trial_end': None,
                'message': 'Active subscription'
            }
        else:
            return {
                'status': 'expired',
                'days_remaining': 0,
                'trial_end': None,
                'message': 'No active subscription. Please upgrade to continue.'
            }
            
    except Subscription.DoesNotExist:
        return {
            'status': 'no_subscription',
            'days_remaining': 0,
            'trial_end': None,
            'message': 'No subscription found. Please contact support.'
        }


def is_access_allowed(tenant):
    """Check if tenant has access to the platform"""
    trial_status = check_trial_status(tenant)
    return trial_status['status'] in ['active', 'trial']


def get_trial_warning_level(tenant):
    """Get warning level based on trial days remaining"""
    trial_status = check_trial_status(tenant)
    
    if trial_status['status'] != 'active':
        return 'expired'
    
    days_remaining = trial_status['days_remaining']
    
    if days_remaining <= 0:
        return 'expired'
    elif days_remaining <= 3:
        return 'critical'
    elif days_remaining <= 7:
        return 'warning'
    else:
        return 'normal'


def create_trial_expired_page_context(tenant):
    """Create context for trial expired page"""
    trial_status = check_trial_status(tenant)
    
    return {
        'tenant': tenant,
        'trial_status': trial_status,
        'upgrade_url': '/tenants/payment/setup/',
        'contact_url': '/tenants/contact/',
    }
