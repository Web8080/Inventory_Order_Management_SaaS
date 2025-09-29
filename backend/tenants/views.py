from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tenant, User, TenantSettings
from .serializers import (
    TenantSerializer, UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, TenantSettingsSerializer
)
from .twofa_views import create_2fa_session


class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tenants"""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tenants based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        elif user.tenant:
            return Tenant.objects.filter(id=user.tenant.id)
        return Tenant.objects.none()
    
    @extend_schema(
        summary="Get current tenant",
        description="Get the current tenant information for the authenticated user"
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current tenant information"""
        if not request.user.tenant:
            return Response(
                {'error': 'No tenant associated with user'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(request.user.tenant)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get tenant settings",
        description="Get the settings for the current tenant"
    )
    @action(detail=True, methods=['get'])
    def settings(self, request, pk=None):
        """Get tenant settings"""
        tenant = self.get_object()
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        serializer = TenantSettingsSerializer(settings)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update tenant settings",
        description="Update the settings for the current tenant"
    )
    @action(detail=True, methods=['put', 'patch'])
    def update_settings(self, request, pk=None):
        """Update tenant settings"""
        tenant = self.get_object()
        settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
        serializer = TenantSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on tenant"""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        elif user.tenant:
            return User.objects.filter(tenant=user.tenant)
        return User.objects.none()
    
    @extend_schema(
        summary="Get tenant users",
        description="Get all users for the current tenant"
    )
    @action(detail=False, methods=['get'])
    def tenant_users(self, request):
        """Get all users for the current tenant"""
        if not request.user.tenant:
            return Response(
                {'error': 'No tenant associated with user'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        users = User.objects.filter(tenant=request.user.tenant)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    """User registration view"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Register a new user and create a tenant if needed",
        request=UserRegistrationSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """User profile management"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get user profile",
        description="Get the profile of the authenticated user",
        responses={200: UserProfileSerializer}
    )
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update user profile",
        description="Update the profile of the authenticated user",
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Change password",
        description="Change the password of the authenticated user",
        request={
            'type': 'object',
            'properties': {
                'old_password': {'type': 'string'},
                'new_password': {'type': 'string'},
                'confirm_password': {'type': 'string'}
            },
            'required': ['old_password', 'new_password', 'confirm_password']
        }
    )
    def post(self, request):
        """Change user password"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            return Response(
                {'error': 'All password fields are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'})


def tenant_signin(request):
    """Tenant sign-in page and authentication"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not all([email, password]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'tenants/signin.html')
        
        try:
            # Authenticate user - Django will find the user by email
            user = authenticate(request, email=email, password=password)
            
            if user and user.is_active and user.tenant:
                # Check if user has 2FA enabled
                from .twofa_models import TwoFactorAuth
                try:
                    two_fa = TwoFactorAuth.objects.get(user=user, tenant=user.tenant)
                    if two_fa.is_enabled:
                        # Create 2FA session and redirect to verification
                        two_fa_session = create_2fa_session(user)
                        return redirect(f'/tenants/2fa/verify/?session_key={two_fa_session.session_key}')
                except TwoFactorAuth.DoesNotExist:
                    pass
                
                # No 2FA or not enabled, login directly
                login(request, user, backend='tenants.backends.EmailBackend')
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('/')  # Redirect to frontend
            else:
                messages.error(request, 'Invalid credentials or account not found.')
        
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')
    
    return render(request, 'tenants/signin.html')


def tenant_signup(request):
    """Tenant registration and onboarding"""
    if request.method == 'POST':
        try:
            # Extract form data
            company_name = request.POST.get('company_name', '').strip()
            industry = request.POST.get('industry', '').strip()
            company_size = request.POST.get('company_size', '').strip()
            website = request.POST.get('website', '').strip()
            
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            signup_type = request.POST.get('signup_type', 'trial').strip()
            plan = request.POST.get('plan', 'professional').strip()
            terms = request.POST.get('terms', False)
            
            # Validation
            if not all([company_name, industry, first_name, last_name, email, password, terms]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'tenants/signup.html')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'tenants/signup.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'tenants/signup.html')
            
            # Create tenant
            tenant_slug = company_name.lower().replace(' ', '').replace('&', '').replace('-', '')
            # Ensure unique slug
            original_slug = tenant_slug
            counter = 1
            while Tenant.objects.filter(slug=tenant_slug).exists():
                tenant_slug = f"{original_slug}{counter}"
                counter += 1
            
            tenant = Tenant.objects.create(
                name=company_name,
                slug=tenant_slug,
                plan=plan,
                is_active=True
            )
            
            # Create tenant settings
            TenantSettings.objects.create(
                tenant=tenant,
                low_stock_threshold=10,
                auto_reorder_enabled=True,
                ml_forecasting_enabled=True,
                email_notifications=True,
                low_stock_alerts=True,
                order_notifications=True
            )
            
            # Create admin user
            user = User.objects.create_user(
                username=f"{tenant_slug}_admin",
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                tenant=tenant,
                role='owner',
                is_tenant_admin=True,
                is_active=True
            )
            
            # Create default warehouse
            from inventory.models import Warehouse
            warehouse = Warehouse.objects.create(
                tenant=tenant,
                name=f"{company_name} Main Warehouse",
                code='MAIN',
                address="123 Main Street, City, State 12345",
                contact_person=f"{first_name} {last_name}",
                phone=phone or "555-0123",
                email=email,
                is_active=True,
                is_default=True
            )
            
            # Handle file uploads
            data_files = request.FILES.getlist('data_files')
            if data_files:
                # Process uploaded CSV files
                from .utils import process_csv_import
                process_csv_import(tenant, data_files)
            
            # Handle subscription creation based on signup type
            from .payment_models import SubscriptionPlan, Subscription
            from django.utils import timezone
            from datetime import timedelta
            
            if signup_type == 'trial':
                # Create trial subscription automatically
                try:
                    trial_plan = SubscriptionPlan.objects.get(name='professional')
                except SubscriptionPlan.DoesNotExist:
                    trial_plan = SubscriptionPlan.objects.filter(is_active=True).first()
                
                if trial_plan:
                    trial_end = timezone.now() + timedelta(days=14)  # 14-day trial
                    subscription = Subscription.objects.create(
                        tenant=tenant,
                        plan=trial_plan,
                        status='trial',
                        billing_cycle='monthly',
                        trial_start=timezone.now(),
                        trial_end=trial_end,
                        current_period_start=timezone.now(),
                        current_period_end=trial_end,
                        requires_approval=False,
                    )
                    
                    # Update tenant with subscription info
                    tenant.subscription_status = 'trial'
                    tenant.save()
                
                # Login the user with specific backend
                login(request, user, backend='tenants.backends.EmailBackend')
                
                # Show trial success page
                return render(request, 'tenants/trial_success.html', {
                    'user': user,
                    'tenant': tenant,
                    'subscription': subscription
                })
            else:
                # For paid subscriptions, redirect to payment setup
                login(request, user, backend='tenants.backends.EmailBackend')
                return redirect('/tenants/payment/setup/')
            
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
    
    return render(request, 'tenants/signup.html')


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'legal/terms_of_service.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'legal/privacy_policy.html')