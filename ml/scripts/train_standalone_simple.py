#!/usr/bin/env python
"""
Standalone Simple ML Training
Trains models without any external dependencies
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

# ML imports (scikit-learn only)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class StandaloneSimpleTrainer:
    """
    Standalone simple ML trainer
    """
    
    def __init__(self, data_dir: str = "ml/data", models_dir: str = "ml/models"):
        self.data_dir = data_dir
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.training_results = {}
        
    def load_training_data(self):
        """Load training datasets"""
        print("📊 Loading training datasets...")
        
        datasets = {}
        data_files = {
            'sales': 'sales_dataset.csv',
            'inventory': 'inventory_dataset.csv',
            'external_factors': 'external_factors_dataset.csv',
            'product_analytics': 'product_analytics_dataset.csv'
        }
        
        for name, filename in data_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                # Only add date column if it exists
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                datasets[name] = df
                print(f"  ✅ Loaded {name}: {len(df)} records")
            else:
                print(f"  ❌ File not found: {filepath}")
        
        return datasets
    
    def prepare_features(self, datasets):
        """Prepare features for ML training"""
        print("🔧 Preparing features for ML training...")
        
        # Start with sales data
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
        
        # Feature engineering
        sales_df = self._engineer_features(sales_df)
        
        # Remove rows with missing values
        sales_df = sales_df.dropna()
        
        print(f"  ✅ Feature preparation complete: {len(sales_df)} records, {len(sales_df.columns)} features")
        
        return sales_df
    
    def _engineer_features(self, df):
        """Feature engineering"""
        df = df.copy()
        
        # Time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek
        df['dayofyear'] = df['date'].dt.dayofyear
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
    
    def train_models(self, df):
        """Train ML models"""
        print("🎯 Training ML models...")
        
        # Prepare features and target
        feature_columns = [col for col in df.columns 
                          if col not in ['date', 'product_id', 'target_quantity', 'quantity_sold', 'revenue', 
                                       'tenant_id', 'tenant_name', 'product_name', 'product_sku', 'category', 
                                       'supplier', 'order_number', 'customer_name', 'order_status', 
                                       'payment_status', 'demand_pattern', 'business_type']]
        
        X = df[feature_columns]
        y = df['target_quantity']
        
        # Remove rows with missing target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        print(f"  📊 Training data: {len(X)} samples, {len(feature_columns)} features")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'extra_trees': ExtraTreesRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'elastic_net': ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                random_state=42,
                max_iter=1000
            ),
            'ridge': Ridge(
                alpha=1.0,
                random_state=42
            )
        }
        
        # Train models
        trained_models = {}
        results = {}
        
        for name, model in models.items():
            print(f"  🔄 Training {name}...")
            
            try:
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3, scoring='neg_mean_absolute_error')
                cv_mae = -cv_scores.mean()
                cv_std = cv_scores.std()
                
                trained_models[name] = model
                results[name] = {
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'cv_mae': cv_mae,
                    'cv_std': cv_std
                }
                
                print(f"    ✅ {name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")
                
            except Exception as e:
                print(f"    ❌ {name}: Error - {e}")
        
        # Create ensemble model
        print("  🔄 Training ensemble model...")
        try:
            ensemble = VotingRegressor([
                ('random_forest', trained_models['random_forest']),
                ('extra_trees', trained_models['extra_trees']),
                ('gradient_boosting', trained_models['gradient_boosting'])
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
                'r2': ensemble_r2
            }
            
            print(f"    ✅ Ensemble: MAE={ensemble_mae:.2f}, RMSE={ensemble_rmse:.2f}, R²={ensemble_r2:.3f}")
            
        except Exception as e:
            print(f"    ❌ Ensemble: Error - {e}")
        
        # Find best model
        if results:
            best_model_name = min(results.keys(), key=lambda x: results[x]['mae'])
            best_model = trained_models[best_model_name]
            
            print(f"  🏆 Best model: {best_model_name} (MAE: {results[best_model_name]['mae']:.2f})")
        else:
            best_model_name = None
            best_model = None
            print(f"  ❌ No models trained successfully")
        
        return {
            'models': trained_models,
            'scaler': scaler,
            'feature_columns': feature_columns,
            'results': results,
            'best_model_name': best_model_name,
            'best_model': best_model,
            'test_data': (X_test, y_test)
        }
    
    def create_inventory_optimizer(self, df):
        """Create simple inventory optimization rules"""
        print("🎯 Creating inventory optimization rules...")
        
        optimization_rules = {}
        
        # Group by product
        for product_id, product_data in df.groupby('product_id'):
            if len(product_data) < 10:
                continue
                
            # Calculate demand statistics
            demand_mean = product_data['quantity_sold'].mean()
            demand_std = product_data['quantity_sold'].std()
            cost_price = product_data['cost_price'].iloc[0]
            selling_price = product_data['unit_price'].iloc[0]
            
            # Simple EOQ calculation
            holding_cost = cost_price * 0.2  # 20% of cost
            ordering_cost = 50  # Fixed ordering cost
            lead_time = 7  # 7 days
            
            # EOQ
            eoq = np.sqrt(2 * demand_mean * ordering_cost / holding_cost)
            
            # Safety stock (95% service level)
            safety_stock = 1.96 * demand_std * np.sqrt(lead_time)
            
            # Reorder point
            reorder_point = demand_mean * lead_time + safety_stock
            
            optimization_rules[product_id] = {
                'reorder_point': reorder_point,
                'reorder_quantity': eoq,
                'safety_stock': safety_stock,
                'service_level': 0.95,
                'demand_mean': demand_mean,
                'demand_std': demand_std,
                'cost_price': cost_price,
                'selling_price': selling_price
            }
        
        print(f"  ✅ Created optimization rules for {len(optimization_rules)} products")
        return optimization_rules
    
    def save_models(self, forecasting_results, optimization_rules):
        """Save all trained models"""
        print("💾 Saving trained models...")
        
        os.makedirs(self.models_dir, exist_ok=True)
        saved_models = {}
        
        # Save forecasting models
        for name, model in forecasting_results['models'].items():
            model_path = os.path.join(self.models_dir, f'forecasting_{name}.pkl')
            joblib.dump(model, model_path)
            saved_models[f'forecasting_{name}'] = model_path
            print(f"  ✅ Saved forecasting model: {name}")
        
        # Save scaler
        scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
        joblib.dump(forecasting_results['scaler'], scaler_path)
        saved_models['scaler'] = scaler_path
        
        # Save optimization rules
        optimization_path = os.path.join(self.models_dir, 'optimization_rules.pkl')
        joblib.dump(optimization_rules, optimization_path)
        saved_models['optimization'] = optimization_path
        
        # Save training results
        results_path = os.path.join(self.models_dir, 'training_results.json')
        with open(results_path, 'w') as f:
            json.dump(forecasting_results['results'], f, indent=2, default=str)
        saved_models['results'] = results_path
        
        # Save feature columns
        features_path = os.path.join(self.models_dir, 'feature_columns.json')
        with open(features_path, 'w') as f:
            json.dump(forecasting_results['feature_columns'], f, indent=2)
        saved_models['features'] = features_path
        
        print(f"  ✅ All models saved to {self.models_dir}")
        
        return saved_models
    
    def generate_report(self, forecasting_results, optimization_rules):
        """Generate training report"""
        print("📊 Generating training report...")
        
        report = {
            'training_date': datetime.now().isoformat(),
            'forecasting_models': {
                'total_models': len(forecasting_results['models']),
                'best_model': forecasting_results['best_model_name'],
                'model_performance': forecasting_results['results']
            },
            'optimization_rules': {
                'products_optimized': len(optimization_rules),
                'avg_reorder_point': np.mean([r['reorder_point'] for r in optimization_rules.values()]),
                'avg_reorder_quantity': np.mean([r['reorder_quantity'] for r in optimization_rules.values()]),
                'avg_service_level': np.mean([r['service_level'] for r in optimization_rules.values()])
            }
        }
        
        report_path = os.path.join(self.data_dir, 'training_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"  ✅ Training report saved: {report_path}")
        
        return report_path


def main():
    """Main training function"""
    print("🚀 Starting Standalone Simple ML Training")
    print("=" * 60)
    
    # Initialize trainer
    trainer = StandaloneSimpleTrainer()
    
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
    forecasting_results = trainer.train_models(features_df)
    
    print("\n🎯 Creating Inventory Optimization Rules...")
    optimization_rules = trainer.create_inventory_optimizer(features_df)
    
    # Save models
    print("\n💾 Saving Models...")
    saved_models = trainer.save_models(forecasting_results, optimization_rules)
    
    # Generate report
    print("\n📊 Generating Training Report...")
    report_path = trainer.generate_report(forecasting_results, optimization_rules)
    
    print("\n" + "=" * 60)
    print("✅ ML Model Training Completed Successfully!")
    
    if forecasting_results['best_model_name']:
        print(f"\n🏆 Best Forecasting Model: {forecasting_results['best_model_name']}")
        print(f"📊 Model Performance:")
        for name, metrics in forecasting_results['results'].items():
            print(f"  • {name}: MAE={metrics['mae']:.2f}, RMSE={metrics['rmse']:.2f}, R²={metrics['r2']:.3f}")
    
    print(f"\n🎯 Optimization Results:")
    print(f"  • Products Optimized: {len(optimization_rules)}")
    if optimization_rules:
        print(f"  • Average Reorder Point: {np.mean([r['reorder_point'] for r in optimization_rules.values()]):.1f}")
        print(f"  • Average Service Level: {np.mean([r['service_level'] for r in optimization_rules.values()]):.3f}")
    
    print(f"\n💾 Saved Models:")
    for name, path in saved_models.items():
        print(f"  • {name}: {path}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Integrate models into main application")
    print(f"  2. Create API endpoints for predictions")
    print(f"  3. Update frontend to show AI insights")


if __name__ == '__main__':
    main()
