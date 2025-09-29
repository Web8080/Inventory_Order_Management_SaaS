"""
ML API URLs
"""

from django.urls import path
from . import views

urlpatterns = [
    # Demand prediction endpoints
    path('predict/demand/', views.predict_demand, name='ml_predict_demand'),
    path('predict/demand/bulk/', views.bulk_predict_demand, name='ml_bulk_predict_demand'),
    
    # Optimization endpoints
    path('optimize/<str:product_id>/', views.get_optimization_recommendations, name='ml_optimize_product'),
    
    # Insights and performance endpoints
    path('insights/', views.get_ai_insights, name='ml_ai_insights'),
    path('performance/', views.get_model_performance, name='ml_model_performance'),
]
