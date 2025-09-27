from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tenant, User, TenantSettings
from .serializers import (
    TenantSerializer, UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, TenantSettingsSerializer
)


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