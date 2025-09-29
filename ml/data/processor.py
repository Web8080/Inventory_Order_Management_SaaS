"""
Advanced Data Processing Pipeline for ML Models
Handles data extraction, cleaning, feature engineering, and preparation for ML training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_saas.settings')
import django
django.setup()

from tenants.models import Tenant
from products.models import Product, Category, Supplier
from orders.models import Order, OrderLine
from inventory.models import StockItem, StockTransaction, Warehouse


class DataProcessor:
    """
    Advanced data processor for ML pipeline
    Handles data extraction, cleaning, feature engineering, and preparation
    """
    
    def __init__(self):
        self.data_cache = {}
        self.feature_columns = []
        self.scalers = {}
        
    async def get_current_inventory(self, tenant_id: str, product_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """Get current inventory data for ML processing"""
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Build query
            query = StockItem.objects.filter(tenant=tenant)
            if product_ids:
                query = query.filter(product_id__in=product_ids)
            
            # Get data
            stock_items = query.select_related('product', 'warehouse', 'variant').all()
            
            if not stock_items:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for item in stock_items:
                data.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'product_sku': item.product.sku,
                    'variant_id': str(item.variant.id) if item.variant else None,
                    'warehouse_id': str(item.warehouse.id),
                    'warehouse_name': item.warehouse.name,
                    'quantity': item.quantity,
                    'reserved_quantity': item.reserved_quantity,
                    'available_quantity': item.available_quantity,
                    'cost_price': item.product.cost_price,
                    'selling_price': item.variant.selling_price if item.variant else item.product.selling_price,
                    'reorder_point': item.variant.reorder_point if item.variant else 10,
                    'reorder_quantity': item.variant.reorder_quantity if item.variant else 50,
                    'is_low_stock': item.is_low_stock,
                    'last_updated': item.last_updated,
                    'created_at': item.created_at
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Error getting inventory data: {e}")
            return pd.DataFrame()
    
    async def get_historical_sales(self, tenant_id: str, product_ids: Optional[List[str]] = None, 
                                 days: int = 365) -> pd.DataFrame:
        """Get historical sales data for ML training"""
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = OrderLine.objects.filter(
                order__tenant=tenant,
                order__created_at__gte=start_date,
                order__order_type='sale'
            ).select_related('order', 'product', 'variant')
            
            if product_ids:
                query = query.filter(product_id__in=product_ids)
            
            # Get data
            order_lines = query.all()
            
            if not order_lines:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for line in order_lines:
                data.append({
                    'date': line.order.created_at.date(),
                    'product_id': str(line.product.id),
                    'product_name': line.product.name,
                    'product_sku': line.product.sku,
                    'variant_id': str(line.variant.id) if line.variant else None,
                    'quantity': line.quantity,
                    'unit_price': float(line.unit_price),
                    'line_total': float(line.line_total),
                    'order_id': str(line.order.id),
                    'order_number': line.order.order_number,
                    'customer_name': line.order.customer_name,
                    'order_status': line.order.status,
                    'payment_status': line.order.payment_status
                })
            
            df = pd.DataFrame(data)
            
            # Aggregate by date and product
            if not df.empty:
                df = df.groupby(['date', 'product_id', 'product_name', 'product_sku']).agg({
                    'quantity': 'sum',
                    'line_total': 'sum',
                    'unit_price': 'mean'
                }).reset_index()
                
                df['revenue'] = df['line_total']
                df['quantity_sold'] = df['quantity']
            
            return df
            
        except Exception as e:
            print(f"Error getting sales data: {e}")
            return pd.DataFrame()
    
    async def get_training_data(self, tenant_id: str, product_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """Get comprehensive training data combining sales, inventory, and external factors"""
        try:
            # Get sales data
            sales_df = await self.get_historical_sales(tenant_id, product_ids)
            
            if sales_df.empty:
                return pd.DataFrame()
            
            # Get inventory data
            inventory_df = await self.get_current_inventory(tenant_id, product_ids)
            
            # Get external factors (generate synthetic for now)
            external_df = self._generate_external_factors(sales_df['date'].min(), sales_df['date'].max())
            
            # Merge datasets
            training_df = sales_df.copy()
            
            # Add inventory features
            if not inventory_df.empty:
                inventory_features = inventory_df[['product_id', 'quantity', 'cost_price', 'selling_price']]
                training_df = training_df.merge(
                    inventory_features, 
                    on='product_id', 
                    how='left',
                    suffixes=('', '_inventory')
                )
            
            # Add external factors
            training_df = training_df.merge(external_df, on='date', how='left')
            
            # Feature engineering
            training_df = self._engineer_features(training_df)
            
            return training_df
            
        except Exception as e:
            print(f"Error getting training data: {e}")
            return pd.DataFrame()
    
    def _generate_external_factors(self, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
        """Generate synthetic external factors for training"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate realistic external factors
        np.random.seed(42)  # For reproducibility
        
        factors_data = []
        for date in date_range:
            # Seasonal patterns
            day_of_year = date.timetuple().tm_yday
            month = date.month
            
            # Temperature (seasonal pattern)
            temperature = 20 + 10 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 2)
            
            # Precipitation (higher in winter)
            precipitation = max(0, 5 + 3 * np.sin(2 * np.pi * day_of_year / 365 + np.pi) + np.random.normal(0, 1))
            
            # Economic index (trending upward with some volatility)
            economic_index = 100 + 0.1 * (date - date_range[0]).days + np.random.normal(0, 2)
            
            # Marketing spend (higher on weekends and holidays)
            is_weekend = date.weekday() >= 5
            is_holiday = month in [12, 1, 7]  # December, January, July
            marketing_spend = 1000 + 500 * is_weekend + 1000 * is_holiday + np.random.normal(0, 200)
            
            # Competitor activity (random but correlated with season)
            competitor_activity = 0.5 + 0.3 * np.sin(2 * np.pi * month / 12) + np.random.normal(0, 0.1)
            
            factors_data.append({
                'date': date,
                'temperature': round(temperature, 1),
                'precipitation': round(precipitation, 1),
                'economic_index': round(economic_index, 1),
                'marketing_spend': round(marketing_spend, 0),
                'competitor_activity': round(competitor_activity, 2),
                'is_weekend': is_weekend,
                'is_holiday': is_holiday
            })
        
        return pd.DataFrame(factors_data)
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering for ML models"""
        df = df.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['product_id', 'date'])
        
        # Time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek
        df['dayofyear'] = df['date'].dt.dayofyear
        df['week'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['dayofweek'].isin([5, 6])
        df['is_month_start'] = df['day'] <= 7
        df['is_month_end'] = df['day'] >= 25
        
        # Cyclical encoding for time features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
        df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
        df['dayofyear_sin'] = np.sin(2 * np.pi * df['dayofyear'] / 365)
        df['dayofyear_cos'] = np.cos(2 * np.pi * df['dayofyear'] / 365)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            df[f'quantity_lag_{lag}'] = df.groupby('product_id')['quantity_sold'].shift(lag)
            df[f'revenue_lag_{lag}'] = df.groupby('product_id')['revenue'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'quantity_rolling_mean_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).mean().reset_index(0, drop=True)
            df[f'quantity_rolling_std_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).std().reset_index(0, drop=True)
            df[f'quantity_rolling_min_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).min().reset_index(0, drop=True)
            df[f'quantity_rolling_max_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(window).max().reset_index(0, drop=True)
            
            df[f'revenue_rolling_mean_{window}'] = df.groupby('product_id')['revenue'].rolling(window).mean().reset_index(0, drop=True)
            df[f'revenue_rolling_std_{window}'] = df.groupby('product_id')['revenue'].rolling(window).std().reset_index(0, drop=True)
        
        # Price features
        if 'unit_price' in df.columns:
            df['price_elasticity'] = df['revenue'] / df['quantity_sold']
            df['price_change'] = df.groupby('product_id')['unit_price'].pct_change()
            df['price_volatility'] = df.groupby('product_id')['unit_price'].rolling(30).std().reset_index(0, drop=True)
        
        # Demand features
        df['demand_trend'] = df.groupby('product_id')['quantity_sold'].rolling(30).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        ).reset_index(0, drop=True)
        
        # Seasonality features
        df['seasonal_factor'] = df.groupby(['product_id', 'month'])['quantity_sold'].transform('mean')
        df['seasonal_factor'] = df['seasonal_factor'] / df.groupby('product_id')['quantity_sold'].transform('mean')
        
        # External factor interactions
        if 'temperature' in df.columns:
            df['temp_demand_interaction'] = df['temperature'] * df['quantity_sold']
        if 'marketing_spend' in df.columns:
            df['marketing_demand_interaction'] = df['marketing_spend'] * df['quantity_sold']
        
        # Product-specific features
        if 'cost_price' in df.columns and 'selling_price' in df.columns:
            df['profit_margin'] = (df['selling_price'] - df['cost_price']) / df['selling_price']
            df['profit_per_unit'] = df['selling_price'] - df['cost_price']
        
        # Target variable (next day's demand)
        df['target_quantity'] = df.groupby('product_id')['quantity_sold'].shift(-1)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        return df
    
    def get_product_features(self, product_id: str) -> Dict[str, Any]:
        """Get comprehensive product features for ML models"""
        try:
            product = Product.objects.get(id=product_id)
            
            # Basic product features
            features = {
                'product_id': str(product.id),
                'name': product.name,
                'sku': product.sku,
                'description': product.description,
                'cost_price': float(product.cost_price),
                'selling_price': float(product.selling_price),
                'weight': float(product.weight) if product.weight else 0,
                'dimensions': product.dimensions,
                'is_active': product.is_active,
                'created_at': product.created_at,
                'updated_at': product.updated_at
            }
            
            # Category features
            if product.category:
                features.update({
                    'category_id': str(product.category.id),
                    'category_name': product.category.name,
                    'category_description': product.category.description
                })
            
            # Supplier features
            if product.supplier:
                features.update({
                    'supplier_id': str(product.supplier.id),
                    'supplier_name': product.supplier.name,
                    'supplier_contact': product.supplier.contact_email
                })
            
            # Stock features
            stock_items = StockItem.objects.filter(product=product)
            if stock_items.exists():
                total_quantity = sum(item.quantity for item in stock_items)
                total_reserved = sum(item.reserved_quantity for item in stock_items)
                low_stock_count = sum(1 for item in stock_items if item.is_low_stock)
                
                features.update({
                    'total_stock': total_quantity,
                    'total_reserved': total_reserved,
                    'available_stock': total_quantity - total_reserved,
                    'low_stock_count': low_stock_count,
                    'warehouse_count': stock_items.count()
                })
            
            # Sales features (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_sales = OrderLine.objects.filter(
                product=product,
                order__created_at__gte=thirty_days_ago,
                order__order_type='sale'
            )
            
            if recent_sales.exists():
                total_sold = sum(line.quantity for line in recent_sales)
                total_revenue = sum(float(line.line_total) for line in recent_sales)
                avg_daily_sales = total_sold / 30
                
                features.update({
                    'recent_sales_quantity': total_sold,
                    'recent_revenue': total_revenue,
                    'avg_daily_sales': avg_daily_sales,
                    'sales_frequency': recent_sales.count()
                })
            
            return features
            
        except Exception as e:
            print(f"Error getting product features: {e}")
            return {}
    
    def create_training_dataset(self, tenant_id: str, output_path: str = None) -> str:
        """Create comprehensive training dataset and save to file"""
        try:
            # Get training data
            training_df = await self.get_training_data(tenant_id)
            
            if training_df.empty:
                print("No training data available")
                return None
            
            # Save to file
            if output_path is None:
                output_path = f"ml/data/training_dataset_{tenant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save dataset
            training_df.to_csv(output_path, index=False)
            
            # Create dataset summary
            summary = {
                'created_at': datetime.now().isoformat(),
                'tenant_id': tenant_id,
                'total_records': len(training_df),
                'date_range': {
                    'start': training_df['date'].min().isoformat(),
                    'end': training_df['date'].max().isoformat()
                },
                'products': training_df['product_id'].nunique(),
                'features': list(training_df.columns),
                'target_variable': 'target_quantity',
                'file_path': output_path
            }
            
            summary_path = output_path.replace('.csv', '_summary.json')
            import json
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"Training dataset created: {output_path}")
            print(f"Dataset summary: {summary_path}")
            print(f"Records: {len(training_df)}, Products: {training_df['product_id'].nunique()}")
            
            return output_path
            
        except Exception as e:
            print(f"Error creating training dataset: {e}")
            return None
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data quality and return quality metrics"""
        quality_report = {
            'total_records': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_records': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'numeric_summary': df.describe().to_dict() if not df.empty else {},
            'quality_score': 0
        }
        
        # Calculate quality score
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        duplicate_cells = df.duplicated().sum() * len(df.columns)
        
        quality_score = max(0, 1 - (missing_cells + duplicate_cells) / total_cells)
        quality_report['quality_score'] = quality_score
        
        return quality_report
