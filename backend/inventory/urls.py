from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'stock-items', views.StockItemViewSet)
router.register(r'stock-transactions', views.StockTransactionViewSet)
router.register(r'stock-alerts', views.StockAlertViewSet)
router.register(r'stock-adjustments', views.StockAdjustmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('adjust/', views.StockAdjustmentView.as_view(), name='stock_adjust'),
    path('low-stock/', views.LowStockView.as_view(), name='low_stock'),
]

