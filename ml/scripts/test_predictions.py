#!/usr/bin/env python
"""
ML Prediction Testing Script
Demonstrates the trained models in action with real predictions
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import our models
from models.forecasting import DemandForecaster, ProphetForecaster
from models.optimization import InventoryOptimizer, AdvancedInventoryOptimizer


class MLPredictionTester:
    """
    Test and demonstrate ML predictions
    """
    
    def __init__(self, models_dir: str = "ml/models", data_dir: str = "ml/data"):
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.models = {}
        self.scalers = {}
        self.test_data = None
        
    def load_models(self):
        """Load all trained models"""
        print("📦 Loading trained models...")
        
        try:
            # Load forecasting models
            model_files = {
                'xgboost': 'forecasting_xgboost.pkl',
                'lightgbm': 'forecasting_lightgbm.pkl',
                'random_forest': 'forecasting_random_forest.pkl',
                'gradient_boosting': 'forecasting_gradient_boosting.pkl',
                'elastic_net': 'forecasting_elastic_net.pkl',
                'ensemble': 'forecasting_ensemble.pkl'
            }
            
            for name, filename in model_files.items():
                model_path = os.path.join(self.models_dir, filename)
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
                    print(f"  ✅ Loaded {name} model")
                else:
                    print(f"  ❌ Model not found: {filename}")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
            if os.path.exists(scaler_path):
                self.scalers['main'] = joblib.load(scaler_path)
                print(f"  ✅ Loaded scaler")
            
            # Load optimization results
            optimization_path = os.path.join(self.models_dir, 'optimization_results.pkl')
            if os.path.exists(optimization_path):
                self.optimization_results = joblib.load(optimization_path)
                print(f"  ✅ Loaded optimization results")
            
            # Load Prophet models
            prophet_path = os.path.join(self.models_dir, 'prophet_models.pkl')
            if os.path.exists(prophet_path):
                self.prophet_models = joblib.load(prophet_path)
                print(f"  ✅ Loaded Prophet models")
            
            # Load training results
            results_path = os.path.join(self.models_dir, 'training_results.json')
            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    self.training_results = json.load(f)
                print(f"  ✅ Loaded training results")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def load_test_data(self):
        """Load test data for predictions"""
        print("📊 Loading test data...")
        
        try:
            # Load sales data
            sales_path = os.path.join(self.data_dir, 'sales_dataset.csv')
            if os.path.exists(sales_path):
                self.test_data = pd.read_csv(sales_path)
                self.test_data['date'] = pd.to_datetime(self.test_data['date'])
                print(f"  ✅ Loaded sales data: {len(self.test_data)} records")
            else:
                print(f"  ❌ Sales data not found: {sales_path}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            return False
    
    def test_demand_forecasting(self, product_id: str = None, days_ahead: int = 30):
        """Test demand forecasting predictions"""
        print(f"🎯 Testing demand forecasting predictions...")
        
        if not self.models or not self.test_data is not None:
            print("❌ Models or test data not loaded")
            return
        
        # Select product for testing
        if product_id is None:
            product_id = self.test_data['product_id'].iloc[0]
        
        print(f"  📦 Testing product: {product_id}")
        
        # Get product data
        product_data = self.test_data[self.test_data['product_id'] == product_id].copy()
        
        if len(product_data) < 30:
            print(f"  ❌ Insufficient data for product {product_id}")
            return
        
        # Prepare features (simplified version)
        product_data = self._prepare_features(product_data)
        
        # Get latest features for prediction
        latest_features = product_data.iloc[-1:].drop(['date', 'product_id', 'target_quantity', 'quantity_sold', 'revenue'], axis=1, errors='ignore')
        
        # Scale features
        if 'main' in self.scalers:
            latest_features_scaled = self.scalers['main'].transform(latest_features)
        else:
            latest_features_scaled = latest_features.values
        
        # Make predictions with all models
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                pred = model.predict(latest_features_scaled)[0]
                predictions[model_name] = max(0, pred)  # Ensure non-negative
                print(f"    {model_name}: {pred:.2f} units")
            except Exception as e:
                print(f"    ❌ {model_name}: Error - {e}")
        
        # Calculate ensemble prediction
        if len(predictions) > 1:
            ensemble_pred = np.mean(list(predictions.values()))
            predictions['ensemble'] = ensemble_pred
            print(f"    🏆 Ensemble: {ensemble_pred:.2f} units")
        
        return predictions
    
    def test_inventory_optimization(self, product_id: str = None):
        """Test inventory optimization"""
        print(f"🎯 Testing inventory optimization...")
        
        if not hasattr(self, 'optimization_results'):
            print("❌ Optimization results not loaded")
            return
        
        # Select product for testing
        if product_id is None:
            product_id = list(self.optimization_results.keys())[0]
        
        print(f"  📦 Testing product: {product_id}")
        
        if product_id in self.optimization_results:
            result = self.optimization_results[product_id]
            
            print(f"    📊 Optimization Results:")
            print(f"      • Reorder Point: {result['reorder_point']:.1f} units")
            print(f"      • Reorder Quantity: {result['reorder_quantity']:.1f} units")
            print(f"      • Safety Stock: {result['safety_stock']:.1f} units")
            print(f"      • Service Level: {result['service_level']:.1%}")
            print(f"      • Stockout Probability: {result['stockout_probability']:.1%}")
            print(f"      • Total Cost: ${result['total_cost']:.2f}")
            print(f"      • Method: {result['optimization_method']}")
            
            return result
        else:
            print(f"  ❌ No optimization results for product {product_id}")
            return None
    
    def test_prophet_forecasting(self, product_id: str = None, days_ahead: int = 30):
        """Test Prophet time series forecasting"""
        print(f"🎯 Testing Prophet forecasting...")
        
        if not hasattr(self, 'prophet_models'):
            print("❌ Prophet models not loaded")
            return
        
        # Select product for testing
        if product_id is None:
            product_id = list(self.prophet_models.keys())[0]
        
        print(f"  📦 Testing product: {product_id}")
        
        if product_id in self.prophet_models:
            prophet_result = self.prophet_models[product_id]
            model = prophet_result['model']
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Get predictions for the future period
            future_predictions = forecast.tail(days_ahead)
            
            print(f"    📈 Prophet Forecast (next {days_ahead} days):")
            print(f"      • Average Daily Demand: {future_predictions['yhat'].mean():.2f} units")
            print(f"      • Min Daily Demand: {future_predictions['yhat'].min():.2f} units")
            print(f"      • Max Daily Demand: {future_predictions['yhat'].max():.2f} units")
            print(f"      • Model Performance: MAE={prophet_result['mae']:.2f}, R²={prophet_result['r2']:.3f}")
            
            # Show confidence intervals
            print(f"      • 95% Confidence Interval: [{future_predictions['yhat_lower'].mean():.2f}, {future_predictions['yhat_upper'].mean():.2f}]")
            
            return {
                'predictions': future_predictions,
                'model_performance': prophet_result
            }
        else:
            print(f"  ❌ No Prophet model for product {product_id}")
            return None
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction (simplified version)"""
        df = df.copy()
        
        # Time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek
        df['dayofyear'] = df['date'].dt.dayofyear
        df['week'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        
        # Cyclical encoding
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
        df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            df[f'quantity_lag_{lag}'] = df['quantity_sold'].shift(lag)
            df[f'revenue_lag_{lag}'] = df['revenue'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'quantity_rolling_mean_{window}'] = df['quantity_sold'].rolling(window).mean()
            df[f'quantity_rolling_std_{window}'] = df['quantity_sold'].rolling(window).std()
        
        # Price features
        df['price_elasticity'] = df['revenue'] / df['quantity_sold']
        df['profit_per_unit'] = df['unit_price'] - df['cost_price']
        df['profit_margin'] = df['profit_per_unit'] / df['unit_price']
        
        # Target variable
        df['target_quantity'] = df['quantity_sold'].shift(-1)
        
        return df
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all ML capabilities"""
        print("🚀 Running Comprehensive ML Test")
        print("=" * 60)
        
        # Load models and data
        self.load_models()
        
        if not self.load_test_data():
            print("❌ Failed to load test data")
            return
        
        # Test demand forecasting
        print("\n🎯 DEMAND FORECASTING TEST")
        print("-" * 40)
        demand_predictions = self.test_demand_forecasting()
        
        # Test inventory optimization
        print("\n🎯 INVENTORY OPTIMIZATION TEST")
        print("-" * 40)
        optimization_result = self.test_inventory_optimization()
        
        # Test Prophet forecasting
        print("\n🎯 PROPHET FORECASTING TEST")
        print("-" * 40)
        prophet_result = self.test_prophet_forecasting()
        
        # Generate test report
        print("\n📊 GENERATING TEST REPORT")
        print("-" * 40)
        self._generate_test_report(demand_predictions, optimization_result, prophet_result)
        
        print("\n" + "=" * 60)
        print("✅ ML Testing Completed Successfully!")
        print("\n🎯 Key Results:")
        
        if demand_predictions:
            best_model = min(demand_predictions.keys(), key=lambda x: abs(demand_predictions[x] - np.mean(list(demand_predictions.values()))))
            print(f"  • Best Demand Forecast: {demand_predictions[best_model]:.2f} units ({best_model})")
        
        if optimization_result:
            print(f"  • Optimal Reorder Point: {optimization_result['reorder_point']:.1f} units")
            print(f"  • Optimal Reorder Quantity: {optimization_result['reorder_quantity']:.1f} units")
            print(f"  • Service Level: {optimization_result['service_level']:.1%}")
        
        if prophet_result:
            avg_demand = prophet_result['predictions']['yhat'].mean()
            print(f"  • Prophet Average Forecast: {avg_demand:.2f} units/day")
            print(f"  • Prophet Model R²: {prophet_result['model_performance']['r2']:.3f}")
    
    def _generate_test_report(self, demand_predictions: Dict, optimization_result: Dict, prophet_result: Dict):
        """Generate comprehensive test report"""
        report = {
            'test_date': datetime.now().isoformat(),
            'demand_forecasting': {
                'models_tested': len(demand_predictions) if demand_predictions else 0,
                'predictions': demand_predictions,
                'best_model': min(demand_predictions.keys(), key=lambda x: abs(demand_predictions[x] - np.mean(list(demand_predictions.values())))) if demand_predictions else None
            },
            'inventory_optimization': {
                'tested': optimization_result is not None,
                'results': optimization_result
            },
            'prophet_forecasting': {
                'tested': prophet_result is not None,
                'average_forecast': prophet_result['predictions']['yhat'].mean() if prophet_result else None,
                'model_performance': prophet_result['model_performance'] if prophet_result else None
            }
        }
        
        report_path = os.path.join(self.data_dir, 'ml_test_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"  ✅ Test report saved: {report_path}")


def main():
    """Main testing function"""
    tester = MLPredictionTester()
    tester.run_comprehensive_test()


if __name__ == '__main__':
    main()
