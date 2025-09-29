#!/usr/bin/env python
"""
Standalone ML Model Training Pipeline
Trains models using the generated datasets without Django dependencies
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import xgboost as xgb
import lightgbm as lgb

# Import our custom models
from models.forecasting import DemandForecaster, ProphetForecaster
from models.optimization import InventoryOptimizer, AdvancedInventoryOptimizer


class StandaloneMLTrainer:
    """
    Standalone ML trainer with state-of-the-art techniques
    """
    
    def __init__(self, data_dir: str = "ml/data", models_dir: str = "ml/models"):
        self.data_dir = data_dir
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.training_results = {}
        self.best_models = {}
        
    def load_training_data(self) -> Dict[str, pd.DataFrame]:
        """Load all training datasets"""
        print("📊 Loading training datasets...")
        
        datasets = {}
        data_files = {
            'sales': 'sales_dataset.csv',
            'inventory': 'inventory_dataset.csv',
            'transactions': 'transactions_dataset.csv',
            'external_factors': 'external_factors_dataset.csv',
            'tenant_metrics': 'tenant_metrics_dataset.csv',
            'product_analytics': 'product_analytics_dataset.csv',
            'demand_patterns': 'demand_patterns_dataset.csv'
        }
        
        for name, filename in data_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['date'] = pd.to_datetime(df['date'])
                datasets[name] = df
                print(f"  ✅ Loaded {name}: {len(df)} records")
            else:
                print(f"  ❌ File not found: {filepath}")
        
        return datasets
    
    def prepare_features(self, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Prepare comprehensive feature set for ML training"""
        print("🔧 Preparing features for ML training...")
        
        # Start with sales data as base
        sales_df = datasets['sales'].copy()
        
        # Merge with inventory data
        if 'inventory' in datasets:
            inventory_features = datasets['inventory'].groupby(['date', 'product_id']).agg({
                'stock_level': 'mean',
                'is_low_stock': 'any',
                'inventory_value': 'sum'
            }).reset_index()
            
            sales_df = sales_df.merge(
                inventory_features, 
                on=['date', 'product_id'], 
                how='left'
            )
        
        # Merge with external factors
        if 'external_factors' in datasets:
            sales_df = sales_df.merge(
                datasets['external_factors'], 
                on='date', 
                how='left'
            )
        
        # Merge with product analytics
        if 'product_analytics' in datasets:
            product_features = datasets['product_analytics'][
                ['product_id', 'category', 'profit_margin', 'price_elasticity', 'customer_rating']
            ]
            sales_df = sales_df.merge(product_features, on='product_id', how='left')
        
        # Feature engineering
        sales_df = self._engineer_features(sales_df)
        
        # Remove rows with missing values
        sales_df = sales_df.dropna()
        
        print(f"  ✅ Feature preparation complete: {len(sales_df)} records, {len(sales_df.columns)} features")
        
        return sales_df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering"""
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
            df[f'quantity_lag_{lag}'] = df.groupby('product_id')['quantity_sold'].shift(lag)
            df[f'revenue_lag_{lag}'] = df.groupby('product_id')['revenue'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'quantity_rolling_mean_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).mean().reset_index(0, drop=True)
            df[f'quantity_rolling_std_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).std().reset_index(0, drop=True)
        
        # Price features
        df['price_elasticity'] = df['revenue'] / df['quantity_sold']
        df['profit_per_unit'] = df['unit_price'] - df['cost_price']
        df['profit_margin'] = df['profit_per_unit'] / df['unit_price']
        
        # Target variable (next day's demand)
        df['target_quantity'] = df.groupby('product_id')['quantity_sold'].shift(-1)
        
        return df
    
    def train_demand_forecasting_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train advanced demand forecasting models"""
        print("🎯 Training demand forecasting models...")
        
        # Prepare features and target
        feature_columns = [col for col in df.columns 
                          if col not in ['date', 'product_id', 'target_quantity', 'quantity_sold', 'revenue', 'tenant_id', 'tenant_name', 'product_name', 'product_sku', 'category', 'supplier', 'order_number', 'customer_name', 'order_status', 'payment_status', 'demand_pattern', 'business_type']]
        
        X = df[feature_columns]
        y = df['target_quantity']
        
        # Remove rows with missing target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models
        models = {
            'xgboost': xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            ),
            'lightgbm': lgb.LGBMRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            ),
            'elastic_net': ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                random_state=42
            )
        }
        
        # Train models
        trained_models = {}
        results = {}
        
        for name, model in models.items():
            print(f"  🔄 Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            cv_std = cv_scores.std()
            
            trained_models[name] = model
            results[name] = {
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'cv_mae': cv_mae,
                'cv_std': cv_std,
                'feature_importance': self._get_feature_importance(model, feature_columns)
            }
            
            print(f"    ✅ {name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")
        
        # Create ensemble model
        print("  🔄 Training ensemble model...")
        ensemble = VotingRegressor([
            ('xgboost', trained_models['xgboost']),
            ('lightgbm', trained_models['lightgbm']),
            ('random_forest', trained_models['random_forest'])
        ])
        
        ensemble.fit(X_train_scaled, y_train)
        y_pred_ensemble = ensemble.predict(X_test_scaled)
        
        ensemble_mae = mean_absolute_error(y_test, y_pred_ensemble)
        ensemble_rmse = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
        ensemble_r2 = r2_score(y_test, y_pred_ensemble)
        
        trained_models['ensemble'] = ensemble
        results['ensemble'] = {
            'mae': ensemble_mae,
            'rmse': ensemble_rmse,
            'r2': ensemble_r2,
            'feature_importance': None
        }
        
        print(f"    ✅ Ensemble: MAE={ensemble_mae:.2f}, RMSE={ensemble_rmse:.2f}, R²={ensemble_r2:.3f}")
        
        # Find best model
        best_model_name = min(results.keys(), key=lambda x: results[x]['mae'])
        best_model = trained_models[best_model_name]
        
        print(f"  🏆 Best model: {best_model_name} (MAE: {results[best_model_name]['mae']:.2f})")
        
        return {
            'models': trained_models,
            'scaler': scaler,
            'feature_columns': feature_columns,
            'results': results,
            'best_model_name': best_model_name,
            'best_model': best_model,
            'test_data': (X_test, y_test)
        }
    
    def train_inventory_optimization_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train inventory optimization models"""
        print("🎯 Training inventory optimization models...")
        
        # Group by product for optimization
        product_groups = df.groupby('product_id')
        
        optimization_results = {}
        
        for product_id, product_data in product_groups:
            if len(product_data) < 30:  # Skip products with insufficient data
                continue
            
            print(f"  🔄 Optimizing product {product_id}...")
            
            # Calculate demand statistics
            demand_mean = product_data['quantity_sold'].mean()
            demand_std = product_data['quantity_sold'].std()
            
            # Get product info
            cost_price = product_data['cost_price'].iloc[0]
            selling_price = product_data['unit_price'].iloc[0]
            
            # Create optimizer
            optimizer = InventoryOptimizer()
            
            # Simulate inventory data
            inventory_data = pd.DataFrame({
                'quantity': [demand_mean * 30],  # 30 days of stock
                'cost_price': [cost_price],
                'selling_price': [selling_price]
            })
            
            # Simulate demand data
            demand_data = pd.DataFrame({
                'quantity': product_data['quantity_sold'].values
            })
            
            # Optimize
            optimization_result = optimizer.optimize_product(
                inventory_data, demand_data, horizon=30, service_level=0.95
            )
            
            optimization_results[product_id] = optimization_result
        
        print(f"  ✅ Optimized {len(optimization_results)} products")
        
        return optimization_results
    
    def _get_feature_importance(self, model, feature_columns: List[str]) -> Dict[str, float]:
        """Get feature importance from model"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                return {}
            
            return dict(zip(feature_columns, importance))
        except:
            return {}
    
    def save_models(self, forecasting_results: Dict, optimization_results: Dict, 
                   output_dir: str = "ml/models") -> Dict[str, str]:
        """Save all trained models"""
        print("💾 Saving trained models...")
        
        os.makedirs(output_dir, exist_ok=True)
        saved_models = {}
        
        # Save forecasting models
        for name, model in forecasting_results['models'].items():
            model_path = os.path.join(output_dir, f'forecasting_{name}.pkl')
            joblib.dump(model, model_path)
            saved_models[f'forecasting_{name}'] = model_path
            print(f"  ✅ Saved forecasting model: {name}")
        
        # Save scaler
        scaler_path = os.path.join(output_dir, 'scaler.pkl')
        joblib.dump(forecasting_results['scaler'], scaler_path)
        saved_models['scaler'] = scaler_path
        
        # Save optimization results
        optimization_path = os.path.join(output_dir, 'optimization_results.pkl')
        joblib.dump(optimization_results, optimization_path)
        saved_models['optimization'] = optimization_path
        
        # Save training results
        results_path = os.path.join(output_dir, 'training_results.json')
        with open(results_path, 'w') as f:
            json.dump(forecasting_results['results'], f, indent=2, default=str)
        saved_models['results'] = results_path
        
        print(f"  ✅ All models saved to {output_dir}")
        
        return saved_models
    
    def generate_training_report(self, forecasting_results: Dict, optimization_results: Dict) -> str:
        """Generate comprehensive training report"""
        print("📊 Generating training report...")
        
        report = {
            'training_date': datetime.now().isoformat(),
            'forecasting_models': {
                'total_models': len(forecasting_results['models']),
                'best_model': forecasting_results['best_model_name'],
                'model_performance': forecasting_results['results']
            },
            'optimization_results': {
                'products_optimized': len(optimization_results),
                'avg_reorder_point': np.mean([r['reorder_point'] for r in optimization_results.values()]),
                'avg_reorder_quantity': np.mean([r['reorder_quantity'] for r in optimization_results.values()]),
                'avg_service_level': np.mean([r['service_level'] for r in optimization_results.values()])
            }
        }
        
        report_path = os.path.join(self.data_dir, 'training_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"  ✅ Training report saved: {report_path}")
        
        return report_path


def main():
    """Main training function"""
    print("🚀 Starting Standalone ML Model Training")
    print("=" * 60)
    
    # Initialize trainer
    trainer = StandaloneMLTrainer()
    
    # Load data
    datasets = trainer.load_training_data()
    
    if not datasets:
        print("❌ No datasets found. Please run dataset generation first.")
        return
    
    # Prepare features
    features_df = trainer.prepare_features(datasets)
    
    if len(features_df) == 0:
        print("❌ No features prepared. Check data quality.")
        return
    
    # Train models
    print("\n🎯 Training Demand Forecasting Models...")
    forecasting_results = trainer.train_demand_forecasting_models(features_df)
    
    print("\n🎯 Training Inventory Optimization Models...")
    optimization_results = trainer.train_inventory_optimization_models(features_df)
    
    # Save models
    print("\n💾 Saving Models...")
    saved_models = trainer.save_models(forecasting_results, optimization_results)
    
    # Generate report
    print("\n📊 Generating Training Report...")
    report_path = trainer.generate_training_report(forecasting_results, optimization_results)
    
    print("\n" + "=" * 60)
    print("✅ ML Model Training Completed Successfully!")
    print(f"\n🏆 Best Forecasting Model: {forecasting_results['best_model_name']}")
    print(f"📊 Model Performance:")
    for name, metrics in forecasting_results['results'].items():
        print(f"  • {name}: MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}, R²={metrics['r2']:.3f}")
    
    print(f"\n🎯 Optimization Results:")
    print(f"  • Products Optimized: {len(optimization_results)}")
    print(f"  • Average Reorder Point: {np.mean([r['reorder_point'] for r in optimization_results.values()]):.1f}")
    print(f"  • Average Service Level: {np.mean([r['service_level'] for r in optimization_results.values()]):.3f}")
    
    print(f"\n💾 Saved Models:")
    for name, path in saved_models.items():
        print(f"  • {name}: {path}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Test predictions: python ml/scripts/test_standalone_predictions.py")
    print(f"  2. Start ML service: uvicorn ml.main:app --reload --port 8001")


if __name__ == '__main__':
    main()
