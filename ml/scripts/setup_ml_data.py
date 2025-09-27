#!/usr/bin/env python
"""
Script to set up ML dataset for demand forecasting
This creates synthetic sales data for training ML models
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_saas.settings')
import django
django.setup()

from tenants.models import Tenant
from products.models import Product
from orders.models import Order, OrderLine
from inventory.models import StockItem


def generate_synthetic_sales_data(tenant, products, days=365):
    """Generate synthetic sales data for ML training"""
    
    print(f"Generating {days} days of synthetic sales data...")
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    sales_data = []
    
    for product in products:
        print(f"Generating data for {product.name}...")
        
        # Base sales pattern (different for each product)
        base_daily_sales = random.uniform(0.5, 5.0)
        
        # Seasonal patterns
        seasonal_amplitude = random.uniform(0.2, 0.8)
        seasonal_phase = random.uniform(0, 2 * np.pi)
        
        # Trend (some products growing, some declining)
        trend = random.uniform(-0.001, 0.002)  # Daily growth/decline rate
        
        # Random noise
        noise_std = base_daily_sales * 0.3
        
        for i, date in enumerate(date_range):
            # Calculate seasonal component
            day_of_year = date.timetuple().tm_yday
            seasonal = seasonal_amplitude * np.sin(2 * np.pi * day_of_year / 365 + seasonal_phase)
            
            # Calculate trend component
            trend_component = trend * i
            
            # Calculate base sales with all components
            daily_sales = base_daily_sales + seasonal + trend_component
            
            # Add random noise
            daily_sales += np.random.normal(0, noise_std)
            
            # Ensure non-negative sales
            daily_sales = max(0, daily_sales)
            
            # Round to integer (can't sell fractional items)
            daily_sales = int(round(daily_sales))
            
            # Skip days with zero sales (realistic)
            if daily_sales > 0:
                sales_data.append({
                    'date': date,
                    'product_id': product.id,
                    'product_sku': product.sku,
                    'product_name': product.name,
                    'quantity_sold': daily_sales,
                    'revenue': daily_sales * product.selling_price,
                    'day_of_week': date.weekday(),
                    'month': date.month,
                    'quarter': (date.month - 1) // 3 + 1,
                    'is_weekend': date.weekday() >= 5,
                    'is_holiday': self._is_holiday(date)
                })
    
    return pd.DataFrame(sales_data)


def _is_holiday(date):
    """Check if date is a holiday (simplified)"""
    # Major US holidays
    holidays = [
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas
        (11, 24), # Black Friday (approximate)
    ]
    
    return (date.month, date.day) in holidays


def generate_inventory_data(tenant, products):
    """Generate inventory level data"""
    
    print("Generating inventory level data...")
    
    inventory_data = []
    
    for product in products:
        # Get current stock
        try:
            stock_item = StockItem.objects.get(tenant=tenant, product=product)
            current_stock = stock_item.quantity
        except StockItem.DoesNotExist:
            current_stock = random.randint(10, 100)
        
        # Generate historical inventory levels
        for days_ago in range(365, 0, -1):
            date = datetime.now() - timedelta(days=days_ago)
            
            # Simulate inventory changes
            # Random stock adjustments, deliveries, etc.
            if random.random() < 0.1:  # 10% chance of stock change
                change = random.randint(-20, 50)
                current_stock = max(0, current_stock + change)
            
            inventory_data.append({
                'date': date,
                'product_id': product.id,
                'product_sku': product.sku,
                'stock_level': current_stock,
                'reorder_point': product.reorder_point,
                'is_low_stock': current_stock <= product.reorder_point,
                'stock_value': current_stock * product.cost_price
            })
    
    return pd.DataFrame(inventory_data)


def generate_external_factors():
    """Generate external factors that might affect demand"""
    
    print("Generating external factors data...")
    
    # Economic indicators, weather, events, etc.
    factors_data = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for date in date_range:
        factors_data.append({
            'date': date,
            'temperature': random.uniform(20, 80),  # Fahrenheit
            'precipitation': random.uniform(0, 2),  # Inches
            'economic_index': random.uniform(0.8, 1.2),  # Economic health
            'marketing_spend': random.uniform(1000, 5000),  # Daily marketing spend
            'competitor_price_index': random.uniform(0.9, 1.1),  # Relative to our prices
            'is_holiday': _is_holiday(date),
            'is_weekend': date.weekday() >= 5,
            'is_month_end': date.day >= 28,
            'is_quarter_end': date.month in [3, 6, 9, 12] and date.day >= 28
        })
    
    return pd.DataFrame(factors_data)


def save_datasets(sales_df, inventory_df, factors_df):
    """Save datasets to files"""
    
    # Create data directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save datasets
    sales_file = os.path.join(data_dir, 'sales_data.csv')
    inventory_file = os.path.join(data_dir, 'inventory_data.csv')
    factors_file = os.path.join(data_dir, 'external_factors.csv')
    
    sales_df.to_csv(sales_file, index=False)
    inventory_df.to_csv(inventory_file, index=False)
    factors_df.to_csv(factors_file, index=False)
    
    print(f"Datasets saved:")
    print(f"- Sales data: {sales_file} ({len(sales_df)} records)")
    print(f"- Inventory data: {inventory_file} ({len(inventory_df)} records)")
    print(f"- External factors: {factors_file} ({len(factors_df)} records)")
    
    # Create dataset summary
    summary = {
        'generated_at': datetime.now().isoformat(),
        'sales_records': len(sales_df),
        'inventory_records': len(inventory_df),
        'factors_records': len(factors_df),
        'date_range': {
            'start': sales_df['date'].min().isoformat(),
            'end': sales_df['date'].max().isoformat()
        },
        'products': sales_df['product_sku'].nunique(),
        'total_revenue': sales_df['revenue'].sum(),
        'avg_daily_sales': sales_df.groupby('date')['quantity_sold'].sum().mean()
    }
    
    summary_file = os.path.join(data_dir, 'dataset_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"- Dataset summary: {summary_file}")
    
    return summary


def create_feature_engineering_script():
    """Create a feature engineering script for ML models"""
    
    script_content = '''
"""
Feature engineering for demand forecasting
This script creates features from the raw datasets for ML model training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def load_datasets():
    """Load the generated datasets"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    sales_df = pd.read_csv(os.path.join(data_dir, 'sales_data.csv'))
    inventory_df = pd.read_csv(os.path.join(data_dir, 'inventory_data.csv'))
    factors_df = pd.read_csv(os.path.join(data_dir, 'external_factors.csv'))
    
    # Convert date columns
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    inventory_df['date'] = pd.to_datetime(inventory_df['date'])
    factors_df['date'] = pd.to_datetime(factors_df['date'])
    
    return sales_df, inventory_df, factors_df

def create_features(sales_df, inventory_df, factors_df):
    """Create features for ML model training"""
    
    # Start with sales data
    features_df = sales_df.copy()
    
    # Add inventory features
    inventory_features = inventory_df[['date', 'product_id', 'stock_level', 'is_low_stock']]
    features_df = features_df.merge(
        inventory_features, 
        on=['date', 'product_id'], 
        how='left'
    )
    
    # Add external factors
    factors_features = factors_df[['date', 'temperature', 'precipitation', 'economic_index', 'marketing_spend']]
    features_df = features_df.merge(factors_features, on='date', how='left')
    
    # Create lag features
    for lag in [1, 7, 14, 30]:
        features_df[f'sales_lag_{lag}'] = features_df.groupby('product_id')['quantity_sold'].shift(lag)
    
    # Create rolling statistics
    for window in [7, 14, 30]:
        features_df[f'sales_rolling_mean_{window}'] = features_df.groupby('product_id')['quantity_sold'].rolling(window).mean().reset_index(0, drop=True)
        features_df[f'sales_rolling_std_{window}'] = features_df.groupby('product_id')['quantity_sold'].rolling(window).std().reset_index(0, drop=True)
    
    # Create price features
    features_df['price_elasticity'] = features_df['revenue'] / features_df['quantity_sold']
    
    # Create time-based features
    features_df['day_of_week'] = features_df['date'].dt.dayofweek
    features_df['month'] = features_df['date'].dt.month
    features_df['quarter'] = features_df['date'].dt.quarter
    features_df['is_weekend'] = features_df['day_of_week'].isin([5, 6])
    features_df['is_month_start'] = features_df['date'].dt.day <= 7
    features_df['is_month_end'] = features_df['date'].dt.day >= 25
    
    # Create target variable (next day's sales)
    features_df['target_sales'] = features_df.groupby('product_id')['quantity_sold'].shift(-1)
    
    # Remove rows with NaN values
    features_df = features_df.dropna()
    
    return features_df

def save_features(features_df):
    """Save engineered features"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    features_file = os.path.join(data_dir, 'engineered_features.csv')
    
    features_df.to_csv(features_file, index=False)
    print(f"Engineered features saved to: {features_file}")
    print(f"Features shape: {features_df.shape}")
    
    return features_file

if __name__ == '__main__':
    # Load datasets
    sales_df, inventory_df, factors_df = load_datasets()
    
    # Create features
    features_df = create_features(sales_df, inventory_df, factors_df)
    
    # Save features
    save_features(features_df)
    
    print("Feature engineering completed!")
'''
    
    script_file = os.path.join(os.path.dirname(__file__), 'feature_engineering.py')
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"Feature engineering script created: {script_file}")


def main():
    """Main function to set up ML data"""
    print("Setting up ML dataset for demand forecasting...")
    
    # Get demo tenant and products
    try:
        tenant = Tenant.objects.get(slug="demo-tenant")
        products = Product.objects.filter(tenant=tenant, is_active=True)
        
        if not products.exists():
            print("No products found. Please run the sample data setup first.")
            return
        
        print(f"Found {products.count()} products for ML data generation")
        
    except Tenant.DoesNotExist:
        print("Demo tenant not found. Please run the sample data setup first.")
        return
    
    # Generate datasets
    print("\n1. Generating sales data...")
    sales_df = generate_synthetic_sales_data(tenant, products)
    
    print("\n2. Generating inventory data...")
    inventory_df = generate_inventory_data(tenant, products)
    
    print("\n3. Generating external factors...")
    factors_df = generate_external_factors()
    
    print("\n4. Saving datasets...")
    summary = save_datasets(sales_df, inventory_df, factors_df)
    
    print("\n5. Creating feature engineering script...")
    create_feature_engineering_script()
    
    print("\n✅ ML dataset setup completed!")
    print(f"\nDataset summary:")
    print(f"- {summary['sales_records']} sales records")
    print(f"- {summary['inventory_records']} inventory records")
    print(f"- {summary['factors_records']} external factor records")
    print(f"- {summary['products']} products")
    print(f"- Total revenue: ${summary['total_revenue']:,.2f}")
    print(f"- Average daily sales: {summary['avg_daily_sales']:.1f} units")
    
    print(f"\nNext steps:")
    print(f"1. Run feature engineering: python ml/scripts/feature_engineering.py")
    print(f"2. Train ML models: python ml/models/forecasting.py")
    print(f"3. Start ML service: uvicorn ml.main:app --reload --port 8001")


if __name__ == '__main__':
    main()
