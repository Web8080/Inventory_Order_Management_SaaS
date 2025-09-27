from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'integrations', views.IntegrationViewSet)
router.register(r'syncs', views.IntegrationSyncViewSet)
router.register(r'webhooks', views.IntegrationWebhookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('shopify/webhook/', views.ShopifyWebhookView.as_view(), name='shopify_webhook'),
    path('woocommerce/webhook/', views.WooCommerceWebhookView.as_view(), name='woocommerce_webhook'),
    path('import/', views.ImportView.as_view(), name='import_data'),
]
