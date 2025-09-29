"""
Security views for tenant users
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json


@login_required
@require_http_methods(["POST"])
def change_password(request):
    """
    Change password for the current user
    """
    try:
        # Get form data
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate required fields
        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            })
        
        # Check if new passwords match
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'New passwords do not match'
            })
        
        # Verify current password
        if not check_password(current_password, request.user.password):
            return JsonResponse({
                'success': False,
                'message': 'Current password is incorrect'
            })
        
        # Validate new password
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'message': '; '.join(e.messages)
            })
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Re-authenticate user to maintain session
        user = authenticate(
            request=request,
            username=request.user.email,
            password=new_password
        )
        if user:
            login(request, user, backend='tenants.backends.EmailBackend')
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error changing password: {str(e)}'
        })


@login_required
def security_settings(request):
    """
    Security settings page
    """
    return render(request, 'tenants/security_settings.html', {
        'user': request.user
    })
