from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Tenant, User, TenantSettings


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model"""
    user_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'plan', 'is_active', 'user_count',
            'stripe_customer_id', 'stripe_subscription_id', 'subscription_status',
            'timezone', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count']


class TenantSettingsSerializer(serializers.ModelSerializer):
    """Serializer for TenantSettings model"""
    
    class Meta:
        model = TenantSettings
        fields = [
            'low_stock_threshold', 'auto_reorder_enabled', 'reorder_lead_time_days',
            'ml_forecasting_enabled', 'forecast_horizon_days', 'confidence_threshold',
            'shopify_enabled', 'shopify_webhook_secret', 'woocommerce_enabled',
            'email_notifications', 'low_stock_alerts', 'order_notifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'tenant', 'tenant_name', 'role', 'phone', 'avatar',
            'is_tenant_admin', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tenant_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        """Get full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    tenant_name = serializers.CharField(write_only=True)
    tenant_slug = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'confirm_password',
            'phone', 'tenant_name', 'tenant_slug'
        ]
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate_tenant_slug(self, value):
        """Validate tenant slug uniqueness"""
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Tenant with this slug already exists")
        return value
    
    def create(self, validated_data):
        """Create user and tenant"""
        from django.db import transaction
        
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')
        tenant_name = validated_data.pop('tenant_name')
        tenant_slug = validated_data.pop('tenant_slug')
        
        with transaction.atomic():
            # Create tenant
            tenant = Tenant.objects.create(
                name=tenant_name,
                slug=tenant_slug,
                plan='free'
            )
            
            # Create tenant settings
            TenantSettings.objects.create(tenant=tenant)
            
            # Create user
            user = User.objects.create(
                tenant=tenant,
                role='owner',
                is_tenant_admin=True,
                **validated_data
            )
            user.set_password(password)
            user.save()
            
            return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'tenant_name', 'role', 'phone', 'avatar', 'is_tenant_admin',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'tenant_name', 'role', 'is_tenant_admin',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        """Get full name"""
        return f"{obj.first_name} {obj.last_name}".strip()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Validate login credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

