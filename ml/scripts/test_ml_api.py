#!/usr/bin/env python
"""
Test ML API Integration
Tests the ML API endpoints to ensure they're working correctly
"""

import requests
import json
import os
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/ml"

def test_ml_api():
    """Test all ML API endpoints"""
    print("🧪 Testing ML API Integration")
    print("=" * 50)
    
    # Test 1: AI Insights
    print("\n1. Testing AI Insights...")
    try:
        response = requests.get(f"{BASE_URL}/insights/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ AI Insights: {data['insights']['models_status']['loaded']}")
            print(f"   📊 Models loaded: {data['insights']['models_status']['forecasting_models']}")
            print(f"   🎯 Products optimized: {data['insights']['models_status']['optimization_rules']}")
        else:
            print(f"   ❌ AI Insights failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ AI Insights error: {e}")
    
    # Test 2: Model Performance
    print("\n2. Testing Model Performance...")
    try:
        response = requests.get(f"{BASE_URL}/performance/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Model Performance loaded")
            if 'performance' in data and data['performance']:
                best_model = list(data['performance'].keys())[0]
                mae = data['performance'][best_model]['mae']
                print(f"   📈 Best model: {best_model} (MAE: {mae:.2f})")
        else:
            print(f"   ❌ Model Performance failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model Performance error: {e}")
    
    # Test 3: Demand Prediction
    print("\n3. Testing Demand Prediction...")
    try:
        prediction_data = {
            "product_id": "prod-1",
            "unit_price": 699.99,
            "cost_price": 400.00,
            "quantity_sold": 15,
            "revenue": 10499.85,
            "days_ahead": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/predict/demand/",
            json=prediction_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data['prediction']['predicted_demand']
            confidence = data['prediction']['confidence']
            print(f"   ✅ Demand Prediction: {prediction} units")
            print(f"   🎯 Confidence: {confidence:.1%}")
        else:
            print(f"   ❌ Demand Prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Demand Prediction error: {e}")
    
    # Test 4: Optimization Recommendations
    print("\n4. Testing Optimization Recommendations...")
    try:
        response = requests.get(f"{BASE_URL}/optimize/prod-1/")
        if response.status_code == 200:
            data = response.json()
            recommendations = data['recommendations']
            print(f"   ✅ Optimization Recommendations:")
            print(f"   📦 Reorder Point: {recommendations['reorder_point']} units")
            print(f"   📈 Reorder Quantity: {recommendations['reorder_quantity']} units")
            print(f"   🛡️ Safety Stock: {recommendations['safety_stock']} units")
            print(f"   🎯 Service Level: {recommendations['service_level']:.1%}")
        else:
            print(f"   ❌ Optimization Recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Optimization Recommendations error: {e}")
    
    # Test 5: Bulk Predictions
    print("\n5. Testing Bulk Predictions...")
    try:
        bulk_data = {
            "products": [
                {
                    "product_id": "prod-1",
                    "unit_price": 699.99,
                    "cost_price": 400.00,
                    "quantity_sold": 15,
                    "revenue": 10499.85
                },
                {
                    "product_id": "prod-2",
                    "unit_price": 1299.99,
                    "cost_price": 800.00,
                    "quantity_sold": 8,
                    "revenue": 10399.92
                }
            ],
            "days_ahead": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/predict/demand/bulk/",
            json=bulk_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            predictions = data['predictions']
            print(f"   ✅ Bulk Predictions: {len(predictions)} products")
            for pred in predictions:
                product_id = pred['product_id']
                demand = pred['prediction']['predicted_demand']
                print(f"   📊 {product_id}: {demand} units")
        else:
            print(f"   ❌ Bulk Predictions failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Bulk Predictions error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ML API Testing Completed!")


def test_with_authentication():
    """Test ML API with authentication (if needed)"""
    print("\n🔐 Testing with Authentication...")
    
    # You would need to implement authentication here
    # For now, we'll test without authentication
    
    print("   ℹ️ Authentication not implemented yet - testing without auth")


if __name__ == "__main__":
    print("🚀 Starting ML API Tests")
    print(f"📍 Testing against: {BASE_URL}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Django server is running")
    except:
        print("❌ Django server is not running. Please start it with: python manage.py runserver")
        exit(1)
    
    # Run tests
    test_ml_api()
    test_with_authentication()
    
    print("\n📋 Test Summary:")
    print("   • AI Insights endpoint")
    print("   • Model Performance endpoint") 
    print("   • Demand Prediction endpoint")
    print("   • Optimization Recommendations endpoint")
    print("   • Bulk Predictions endpoint")
    
    print("\n🚀 Next Steps:")
    print("   1. Integrate ML API into frontend")
    print("   2. Add authentication to ML endpoints")
    print("   3. Create real-time prediction dashboard")
    print("   4. Add model retraining capabilities")
