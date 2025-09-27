from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import secrets
from .models import User
from .2fa_models import TwoFactorAuth, TwoFactorSession


@login_required
def setup_2fa(request):
    """Setup 2FA for the current user"""
    try:
        two_fa, created = TwoFactorAuth.objects.get_or_create(
            user=request.user,
            tenant=request.user.tenant
        )
        
        if not two_fa.secret_key:
            two_fa.generate_secret_key()
        
        qr_code = two_fa.generate_qr_code()
        
        context = {
            'qr_code': qr_code,
            'secret_key': two_fa.secret_key,
            'user_email': request.user.email,
            'tenant_name': request.user.tenant.name
        }
        
        return render(request, '2fa/setup.html', context)
    
    except Exception as e:
        messages.error(request, f"Error setting up 2FA: {str(e)}")
        return redirect('admin:index')


@login_required
def verify_2fa_setup(request):
    """Verify 2FA setup with token"""
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user, tenant=request.user.tenant)
            
            if two_fa.verify_token(token):
                two_fa.is_enabled = True
                backup_codes = two_fa.generate_backup_codes()
                two_fa.save()
                
                messages.success(request, "2FA has been successfully enabled!")
                messages.info(request, f"Your backup codes: {', '.join(backup_codes)}")
                messages.warning(request, "Please save these backup codes in a safe place!")
                
                return redirect('admin:index')
            else:
                messages.error(request, "Invalid token. Please try again.")
        
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, "2FA setup not found. Please try again.")
        except Exception as e:
            messages.error(request, f"Error verifying 2FA: {str(e)}")
    
    return redirect('setup_2fa')


@login_required
def disable_2fa(request):
    """Disable 2FA for the current user"""
    if request.method == 'POST':
        try:
            two_fa = TwoFactorAuth.objects.get(user=request.user, tenant=request.user.tenant)
            two_fa.is_enabled = False
            two_fa.secret_key = ''
            two_fa.backup_codes = []
            two_fa.save()
            
            messages.success(request, "2FA has been disabled.")
        
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, "2FA not found.")
        except Exception as e:
            messages.error(request, f"Error disabling 2FA: {str(e)}")
    
    return redirect('admin:index')


def verify_2fa_login(request):
    """Verify 2FA token during login"""
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        session_key = request.POST.get('session_key', '')
        
        try:
            # Find the 2FA session
            two_fa_session = TwoFactorSession.objects.get(
                session_key=session_key,
                is_verified=False
            )
            
            if two_fa_session.is_expired():
                messages.error(request, "Session expired. Please login again.")
                return redirect('admin:login')
            
            # Verify the token
            two_fa = TwoFactorAuth.objects.get(
                user=two_fa_session.user,
                tenant=two_fa_session.user.tenant
            )
            
            if two_fa.verify_token(token) or two_fa.verify_backup_code(token):
                # Mark session as verified
                two_fa_session.is_verified = True
                two_fa_session.save()
                
                # Login the user
                login(request, two_fa_session.user)
                messages.success(request, "Login successful!")
                
                # Redirect to admin
                return redirect('admin:index')
            else:
                messages.error(request, "Invalid token. Please try again.")
        
        except TwoFactorSession.DoesNotExist:
            messages.error(request, "Invalid session. Please login again.")
            return redirect('admin:login')
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, "2FA not configured for this user.")
            return redirect('admin:login')
        except Exception as e:
            messages.error(request, f"Error verifying 2FA: {str(e)}")
    
    return render(request, '2fa/verify.html')


@csrf_exempt
def api_verify_2fa(request):
    """API endpoint for 2FA verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token', '').strip()
            session_key = data.get('session_key', '')
            
            # Find the 2FA session
            two_fa_session = TwoFactorSession.objects.get(
                session_key=session_key,
                is_verified=False
            )
            
            if two_fa_session.is_expired():
                return JsonResponse({'success': False, 'error': 'Session expired'})
            
            # Verify the token
            two_fa = TwoFactorAuth.objects.get(
                user=two_fa_session.user,
                tenant=two_fa_session.user.tenant
            )
            
            if two_fa.verify_token(token) or two_fa.verify_backup_code(token):
                # Mark session as verified
                two_fa_session.is_verified = True
                two_fa_session.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '2FA verification successful',
                    'user_id': str(two_fa_session.user.id)
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid token'})
        
        except TwoFactorSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid session'})
        except TwoFactorAuth.DoesNotExist:
            return JsonResponse({'success': False, 'error': '2FA not configured'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def create_2fa_session(user):
    """Create a 2FA session for a user"""
    session_key = secrets.token_hex(20)
    
    two_fa_session = TwoFactorSession.objects.create(
        user=user,
        tenant=user.tenant,
        session_key=session_key,
        expires_at=timezone.now() + timezone.timedelta(minutes=30)
    )
    
    return two_fa_session
