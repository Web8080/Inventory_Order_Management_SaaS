from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import twofa_views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Tenant management
    path('', include(router.urls)),
    
    # 2FA URLs
    path('2fa/setup/', twofa_views.setup_2fa, name='setup_2fa'),
    path('2fa/verify-setup/', twofa_views.verify_2fa_setup, name='verify_2fa_setup'),
    path('2fa/disable/', twofa_views.disable_2fa, name='disable_2fa'),
    path('2fa/verify/', twofa_views.verify_2fa_login, name='verify_2fa_login'),
    path('api/2fa/verify/', twofa_views.api_verify_2fa, name='api_verify_2fa'),
]
