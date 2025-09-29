from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import twofa_views
from . import payment_views
from . import import_views
from . import trial_views
from . import admin_approval_views
from . import onboarding_views
from . import settings_views
from . import security_views
from . import dashboard_views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Tenant sign-in
    path('signin/', views.tenant_signin, name='tenant_signin'),
    path('signup/', views.tenant_signup, name='tenant_signup'),
    
    # Legal pages
    path('legal/terms/', views.terms_of_service, name='terms_of_service'),
    path('legal/privacy/', views.privacy_policy, name='privacy_policy'),
    
    # Payment and subscription
    path('payment/setup/', payment_views.payment_setup, name='payment_setup'),
    path('payment/create-subscription/', payment_views.create_subscription, name='create_subscription'),
    path('payment/pending-approval/', payment_views.pending_approval, name='pending_approval'),
    path('payment/management/', payment_views.subscription_management, name='subscription_management'),
    path('payment/cancel/', payment_views.cancel_subscription, name='cancel_subscription'),
    path('payment/reactivate/', payment_views.reactivate_subscription, name='reactivate_subscription'),
    path('payment/webhook/', payment_views.stripe_webhook, name='stripe_webhook'),
    
    # Data import
    path('import/', import_views.data_import_page, name='data_import'),
    path('import/upload/', import_views.upload_csv, name='upload_csv'),
    path('import/download-template/<str:template_type>/', import_views.download_template, name='download_template'),
    path('import/status/', import_views.import_status, name='import_status'),
    
    # Manual Entry
    path('import/manual-products/', import_views.manual_products, name='manual_products'),
    path('import/manual-inventory/', import_views.manual_inventory, name='manual_inventory'),
    path('import/manual-customers/', import_views.manual_customers, name='manual_customers'),
    path('import/manual-suppliers/', import_views.manual_suppliers, name='manual_suppliers'),
    
    # Trial management
    path('trial/status/', trial_views.trial_status, name='trial_status'),
    path('trial/upgrade/', trial_views.upgrade_trial, name='upgrade_trial'),
    path('trial/extend/', trial_views.extend_trial, name='extend_trial'),
    path('trial/dashboard/', trial_views.trial_dashboard, name='trial_dashboard'),
    path('trial-expired/', trial_views.trial_expired, name='trial_expired'),
    
    # Admin approval (staff only)
    path('admin/pending-subscriptions/', admin_approval_views.pending_subscriptions, name='pending_subscriptions'),
    path('admin/approve-subscription/<int:subscription_id>/', admin_approval_views.approve_subscription, name='approve_subscription'),
    path('admin/reject-subscription/<int:subscription_id>/', admin_approval_views.reject_subscription, name='reject_subscription'),
    path('admin/subscription-details/<int:subscription_id>/', admin_approval_views.subscription_details, name='subscription_details'),
    path('admin/subscription-analytics/', admin_approval_views.subscription_analytics, name='subscription_analytics'),
    
    # Onboarding
    path('onboarding/', onboarding_views.onboarding_page, name='onboarding'),
    path('onboarding/status/', onboarding_views.onboarding_status, name='onboarding_status'),
    path('onboarding/complete-step/', onboarding_views.complete_onboarding_step, name='complete_onboarding_step'),
    
    # Settings
    path('settings/', settings_views.settings_page, name='settings'),
    path('settings/get/', settings_views.get_tenant_settings, name='get_tenant_settings'),
    path('settings/update-tenant/', settings_views.update_tenant_info, name='update_tenant_info'),
    path('settings/update-profile/', settings_views.update_user_profile, name='update_user_profile'),
    path('settings/update-settings/', settings_views.update_tenant_settings, name='update_tenant_settings'),
    path('settings/change-password/', security_views.change_password, name='change_password'),
    
    # Dashboard Data
    path('dashboard/data/', dashboard_views.dashboard_data, name='dashboard_data'),
    path('dashboard/products/', dashboard_views.products_data, name='products_data'),
    path('dashboard/orders/', dashboard_views.orders_data, name='orders_data'),
    path('dashboard/inventory/', dashboard_views.inventory_data, name='inventory_data'),
    path('dashboard/users/', dashboard_views.user_management_data, name='user_management_data'),
    
    # Tenant management
    path('', include(router.urls)),
    
    # 2FA URLs
    path('2fa/setup/', twofa_views.setup_2fa, name='setup_2fa'),
    path('2fa/verify/', twofa_views.verify_2fa_login, name='verify_2fa_login'),
    path('2fa/verify-setup/', twofa_views.verify_2fa_setup, name='verify_2fa_setup'),
    path('2fa/disable/', twofa_views.disable_2fa, name='disable_2fa'),
    path('api/2fa/verify/', twofa_views.api_verify_2fa, name='api_verify_2fa'),
]
