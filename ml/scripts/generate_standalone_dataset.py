#!/usr/bin/env python
"""
Standalone Dataset Generator for ML Training
Creates comprehensive, realistic datasets without Django dependencies
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')


class StandaloneDatasetGenerator:
    """
    Standalone dataset generator with sophisticated patterns for inventory management
    """
    
    def __init__(self):
        self.tenants = []
        self.products = []
        self.categories = []
        self.suppliers = []
        self.warehouses = []
        
    def generate_comprehensive_dataset(self, num_tenants: int = 5, days: int = 730) -> Dict[str, pd.DataFrame]:
        """
        Generate comprehensive dataset with multiple tenants and sophisticated patterns
        """
        print(f"🚀 Generating comprehensive dataset with {num_tenants} tenants and {days} days of data...")
        
        # Generate base entities
        self._generate_tenants(num_tenants)
        self._generate_categories()
        self._generate_suppliers()
        self._generate_warehouses()
        
        # Generate products for each tenant
        self._generate_products()
        
        # Generate comprehensive datasets
        datasets = {}
        
        print("📊 Generating sales data with advanced patterns...")
        datasets['sales'] = self._generate_advanced_sales_data(days)
        
        print("📦 Generating inventory data with realistic fluctuations...")
        datasets['inventory'] = self._generate_advanced_inventory_data(days)
        
        print("🔄 Generating stock transactions with complex patterns...")
        datasets['transactions'] = self._generate_advanced_transactions(days)
        
        print("📈 Generating external factors with realistic correlations...")
        datasets['external_factors'] = self._generate_advanced_external_factors(days)
        
        print("🏢 Generating tenant performance metrics...")
        datasets['tenant_metrics'] = self._generate_tenant_metrics()
        
        print("📋 Generating product performance analytics...")
        datasets['product_analytics'] = self._generate_product_analytics()
        
        print("🎯 Generating demand patterns with seasonality...")
        datasets['demand_patterns'] = self._generate_demand_patterns(days)
        
        return datasets
    
    def _generate_tenants(self, num_tenants: int):
        """Generate diverse tenants with different business models"""
        business_types = [
            {'name': 'TechGadgets Inc', 'type': 'electronics', 'scale': 'large'},
            {'name': 'Fashion Forward', 'type': 'fashion', 'scale': 'medium'},
            {'name': 'Home & Garden Co', 'type': 'home_garden', 'scale': 'medium'},
            {'name': 'Sports Central', 'type': 'sports', 'scale': 'small'},
            {'name': 'Beauty Essentials', 'type': 'beauty', 'scale': 'small'},
            {'name': 'Auto Parts Pro', 'type': 'automotive', 'scale': 'large'},
            {'name': 'Book World', 'type': 'books', 'scale': 'small'},
            {'name': 'Pet Paradise', 'type': 'pet_supplies', 'scale': 'medium'},
            {'name': 'Office Solutions', 'type': 'office', 'scale': 'medium'},
            {'name': 'Health & Wellness', 'type': 'health', 'scale': 'large'}
        ]
        
        for i in range(num_tenants):
            business = business_types[i % len(business_types)]
            
            tenant = {
                'id': f"tenant-{i+1}",
                'name': business['name'],
                'slug': f"{business['name'].lower().replace(' ', '-').replace('&', 'and')}-{i+1}",
                'type': business['type'],
                'scale': business['scale']
            }
            
            self.tenants.append(tenant)
            print(f"  ✅ Created tenant: {tenant['name']}")
    
    def _generate_categories(self):
        """Generate product categories"""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports & Fitness', 'description': 'Sports equipment and fitness gear'},
            {'name': 'Beauty & Personal Care', 'description': 'Beauty and personal care products'},
            {'name': 'Automotive', 'description': 'Auto parts and accessories'},
            {'name': 'Books & Media', 'description': 'Books, movies, and media'},
            {'name': 'Pet Supplies', 'description': 'Pet food and accessories'},
            {'name': 'Office Supplies', 'description': 'Office equipment and supplies'},
            {'name': 'Health & Wellness', 'description': 'Health and wellness products'}
        ]
        
        for cat_data in categories_data:
            category = {
                'id': f"cat-{len(self.categories)+1}",
                'name': cat_data['name'],
                'description': cat_data['description']
            }
            self.categories.append(category)
    
    def _generate_suppliers(self):
        """Generate suppliers with different characteristics"""
        suppliers_data = [
            {'name': 'Global Electronics Ltd', 'contact': 'supply@globalelec.com', 'reliability': 0.95},
            {'name': 'Fashion Forward Supply', 'contact': 'orders@fashionforward.com', 'reliability': 0.88},
            {'name': 'Home Depot Wholesale', 'contact': 'wholesale@homedepot.com', 'reliability': 0.92},
            {'name': 'Sports Equipment Co', 'contact': 'sales@sportseq.com', 'reliability': 0.85},
            {'name': 'Beauty Supply Chain', 'contact': 'orders@beautysupply.com', 'reliability': 0.90},
            {'name': 'Auto Parts Direct', 'contact': 'wholesale@autoparts.com', 'reliability': 0.93},
            {'name': 'Book Distributors Inc', 'contact': 'orders@bookdist.com', 'reliability': 0.87},
            {'name': 'Pet Supply Network', 'contact': 'sales@petsupply.com', 'reliability': 0.89},
            {'name': 'Office Solutions Plus', 'contact': 'orders@officesolutions.com', 'reliability': 0.91},
            {'name': 'Health Products Ltd', 'contact': 'wholesale@healthproducts.com', 'reliability': 0.94}
        ]
        
        for supp_data in suppliers_data:
            supplier = {
                'id': f"supp-{len(self.suppliers)+1}",
                'name': supp_data['name'],
                'contact_email': supp_data['contact'],
                'contact_phone': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'reliability': supp_data['reliability']
            }
            self.suppliers.append(supplier)
    
    def _generate_warehouses(self):
        """Generate warehouses with different capacities"""
        warehouse_data = [
            {'name': 'Main Distribution Center', 'capacity': 100000, 'is_default': True},
            {'name': 'East Coast Warehouse', 'capacity': 50000, 'is_default': False},
            {'name': 'West Coast Warehouse', 'capacity': 45000, 'is_default': False},
            {'name': 'Central Warehouse', 'capacity': 35000, 'is_default': False},
            {'name': 'Express Fulfillment Center', 'capacity': 25000, 'is_default': False}
        ]
        
        for wh_data in warehouse_data:
            warehouse = {
                'id': f"wh-{len(self.warehouses)+1}",
                'name': wh_data['name'],
                'code': wh_data['name'].replace(' ', '').upper()[:8],
                'capacity': wh_data['capacity'],
                'is_default': wh_data['is_default']
            }
            self.warehouses.append(warehouse)
    
    def _generate_products(self):
        """Generate diverse products for each tenant"""
        product_templates = {
            'electronics': [
                {'name': 'Smartphone', 'base_price': 699, 'cost_price': 400, 'demand_pattern': 'high'},
                {'name': 'Laptop', 'base_price': 1299, 'cost_price': 800, 'demand_pattern': 'medium'},
                {'name': 'Headphones', 'base_price': 199, 'cost_price': 80, 'demand_pattern': 'high'},
                {'name': 'Tablet', 'base_price': 499, 'cost_price': 250, 'demand_pattern': 'medium'},
                {'name': 'Smart Watch', 'base_price': 299, 'cost_price': 120, 'demand_pattern': 'high'}
            ],
            'fashion': [
                {'name': 'T-Shirt', 'base_price': 25, 'cost_price': 8, 'demand_pattern': 'high'},
                {'name': 'Jeans', 'base_price': 79, 'cost_price': 25, 'demand_pattern': 'medium'},
                {'name': 'Dress', 'base_price': 89, 'cost_price': 30, 'demand_pattern': 'medium'},
                {'name': 'Sneakers', 'base_price': 120, 'cost_price': 40, 'demand_pattern': 'high'},
                {'name': 'Jacket', 'base_price': 149, 'cost_price': 60, 'demand_pattern': 'seasonal'}
            ],
            'home_garden': [
                {'name': 'Garden Hose', 'base_price': 45, 'cost_price': 18, 'demand_pattern': 'seasonal'},
                {'name': 'Power Drill', 'base_price': 89, 'cost_price': 35, 'demand_pattern': 'medium'},
                {'name': 'Plant Pot', 'base_price': 15, 'cost_price': 5, 'demand_pattern': 'high'},
                {'name': 'LED Light Bulb', 'base_price': 8, 'cost_price': 3, 'demand_pattern': 'high'},
                {'name': 'Tool Set', 'base_price': 199, 'cost_price': 80, 'demand_pattern': 'low'}
            ]
        }
        
        for tenant in self.tenants:
            business_type = tenant['type']
            templates = product_templates.get(business_type, product_templates['electronics'])
            
            for i, template in enumerate(templates):
                # Add variation to prices
                price_variation = random.uniform(0.8, 1.2)
                base_price = template['base_price'] * price_variation
                cost_price = template['cost_price'] * price_variation
                
                product = {
                    'id': f"prod-{len(self.products)+1}",
                    'tenant_id': tenant['id'],
                    'tenant_name': tenant['name'],
                    'name': f"{template['name']} {i+1}",
                    'sku': f"{tenant['slug'].upper()[:4]}-{template['name'].upper().replace(' ', '')[:6]}-{i+1:03d}",
                    'description': f"High-quality {template['name'].lower()} for {business_type} market",
                    'category': random.choice(self.categories)['name'],
                    'supplier': random.choice(self.suppliers)['name'],
                    'cost_price': cost_price,
                    'selling_price': base_price,
                    'weight': random.uniform(0.1, 5.0),
                    'is_active': True,
                    'demand_pattern': template['demand_pattern'],
                    'business_type': business_type
                }
                
                self.products.append(product)
    
    def _generate_advanced_sales_data(self, days: int) -> pd.DataFrame:
        """Generate sophisticated sales data with realistic patterns"""
        print("  🔄 Generating sales data with seasonality, trends, and correlations...")
        
        sales_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for product in self.products:
            # Generate base demand with different patterns
            base_demand = self._generate_demand_pattern(
                date_range, product['demand_pattern'], product['business_type']
            )
            
            for i, date in enumerate(date_range):
                # Add random noise and special events
                daily_demand = base_demand[i]
                
                # Apply special events
                daily_demand = self._apply_special_events(daily_demand, date, product['business_type'])
                
                # Ensure non-negative demand
                daily_demand = max(0, int(daily_demand))
                
                if daily_demand > 0:
                    sales_data.append({
                        'date': date.date(),
                        'tenant_id': product['tenant_id'],
                        'tenant_name': product['tenant_name'],
                        'product_id': product['id'],
                        'product_name': product['name'],
                        'product_sku': product['sku'],
                        'category': product['category'],
                        'supplier': product['supplier'],
                        'quantity_sold': daily_demand,
                        'unit_price': product['selling_price'],
                        'revenue': product['selling_price'] * daily_demand,
                        'cost_price': product['cost_price'],
                        'profit': (product['selling_price'] - product['cost_price']) * daily_demand,
                        'order_number': f"SO-{product['tenant_id']}-{date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                        'customer_name': f"Customer {random.randint(1, 1000)}",
                        'order_status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
                        'payment_status': random.choice(['pending', 'paid', 'failed']),
                        'demand_pattern': product['demand_pattern'],
                        'business_type': product['business_type']
                    })
        
        return pd.DataFrame(sales_data)
    
    def _generate_demand_pattern(self, date_range: pd.DatetimeIndex, pattern: str, business_type: str) -> np.ndarray:
        """Generate sophisticated demand patterns"""
        n_days = len(date_range)
        
        # Base demand level
        if pattern == 'high':
            base_level = random.uniform(15, 25)
        elif pattern == 'medium':
            base_level = random.uniform(8, 15)
        elif pattern == 'low':
            base_level = random.uniform(2, 8)
        else:  # seasonal
            base_level = random.uniform(5, 20)
        
        # Create trend
        trend = np.linspace(0, random.uniform(-0.5, 0.5), n_days)
        
        # Create seasonality
        seasonal = np.zeros(n_days)
        for i, date in enumerate(date_range):
            # Annual seasonality
            annual_seasonal = 0.3 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
            
            # Weekly seasonality
            weekly_seasonal = 0.2 * np.sin(2 * np.pi * date.weekday() / 7)
            
            # Monthly seasonality
            monthly_seasonal = 0.1 * np.sin(2 * np.pi * date.month / 12)
            
            seasonal[i] = annual_seasonal + weekly_seasonal + monthly_seasonal
        
        # Create cyclical patterns
        cycle_length = random.randint(30, 90)
        cyclical = 0.2 * np.sin(2 * np.pi * np.arange(n_days) / cycle_length)
        
        # Combine all components
        demand = base_level * (1 + trend + seasonal + cyclical)
        
        # Add random noise
        noise = np.random.normal(0, 0.1, n_days)
        demand = demand * (1 + noise)
        
        return demand
    
    def _apply_special_events(self, base_demand: float, date: datetime, business_type: str) -> float:
        """Apply special events that affect demand"""
        # Holiday effects
        if date.month == 12:  # December (Christmas)
            base_demand *= random.uniform(1.5, 2.5)
        elif date.month == 11:  # November (Black Friday)
            base_demand *= random.uniform(1.3, 2.0)
        elif date.month == 2:  # February (Valentine's Day)
            if business_type == 'fashion' or business_type == 'beauty':
                base_demand *= random.uniform(1.2, 1.8)
        
        # Weekend effects
        if date.weekday() >= 5:  # Weekend
            if business_type == 'electronics':
                base_demand *= random.uniform(1.1, 1.4)
            elif business_type == 'fashion':
                base_demand *= random.uniform(1.2, 1.6)
        
        # End of month effects
        if date.day >= 25:
            base_demand *= random.uniform(0.8, 1.1)
        
        # Random promotional events
        if random.random() < 0.05:  # 5% chance of promotion
            base_demand *= random.uniform(1.5, 3.0)
        
        return base_demand
    
    def _generate_advanced_inventory_data(self, days: int) -> pd.DataFrame:
        """Generate sophisticated inventory data with realistic fluctuations"""
        print("  🔄 Generating inventory data with stock movements and alerts...")
        
        inventory_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for product in self.products:
            # Get initial stock
            initial_stock = random.randint(50, 200)
            current_stock = initial_stock
            
            for date in date_range:
                # Simulate stock movements
                stock_change = self._simulate_stock_movement(date, product)
                current_stock = max(0, current_stock + stock_change)
                
                # Check if reorder is needed
                reorder_point = random.randint(10, 50)
                is_low_stock = current_stock <= reorder_point
                
                # Simulate reorder if needed
                if is_low_stock and random.random() < 0.3:  # 30% chance of reorder
                    current_stock += random.randint(50, 200)
                
                inventory_data.append({
                    'date': date.date(),
                    'tenant_id': product['tenant_id'],
                    'tenant_name': product['tenant_name'],
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'product_sku': product['sku'],
                    'warehouse_id': random.choice(self.warehouses)['id'],
                    'warehouse_name': random.choice(self.warehouses)['name'],
                    'stock_level': current_stock,
                    'reserved_quantity': random.randint(0, min(10, current_stock)),
                    'available_quantity': current_stock - random.randint(0, min(10, current_stock)),
                    'reorder_point': reorder_point,
                    'reorder_quantity': random.randint(50, 200),
                    'is_low_stock': is_low_stock,
                    'cost_price': product['cost_price'],
                    'selling_price': product['selling_price'],
                    'inventory_value': current_stock * product['cost_price'],
                    'demand_pattern': product['demand_pattern'],
                    'business_type': product['business_type']
                })
        
        return pd.DataFrame(inventory_data)
    
    def _simulate_stock_movement(self, date: datetime, product: Dict) -> int:
        """Simulate realistic stock movements"""
        # Base movement (mostly negative due to sales)
        base_movement = -random.randint(0, 5)
        
        # Seasonal adjustments
        if date.month in [11, 12]:  # Holiday season
            base_movement += random.randint(0, 3)  # More restocking
        
        # Random restocking events
        if random.random() < 0.02:  # 2% chance of large restock
            base_movement += random.randint(20, 100)
        
        # Random stock adjustments
        if random.random() < 0.01:  # 1% chance of stock adjustment
            base_movement += random.randint(-10, 10)
        
        return base_movement
    
    def _generate_advanced_transactions(self, days: int) -> pd.DataFrame:
        """Generate comprehensive stock transaction data"""
        print("  🔄 Generating stock transactions with complex patterns...")
        
        transactions_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for product in self.products:
            # Generate transactions based on sales data
            sales_data = self._get_sales_for_product(product, start_date, end_date)
            
            for sale in sales_data:
                # Create outbound transaction for sale
                transactions_data.append({
                    'date': sale['date'],
                    'tenant_id': product['tenant_id'],
                    'product_id': product['id'],
                    'warehouse_id': random.choice(self.warehouses)['id'],
                    'transaction_type': 'out',
                    'quantity': -sale['quantity'],
                    'reason': 'sale',
                    'reference_id': sale['order_id'],
                    'reference_type': 'order',
                    'notes': f"Sale transaction for order {sale['order_number']}",
                    'cost_price': product['cost_price'],
                    'total_value': product['cost_price'] * sale['quantity']
                })
                
                # Create inbound transaction for restocking
                if random.random() < 0.1:  # 10% chance of restocking
                    restock_quantity = random.randint(20, 100)
                    transactions_data.append({
                        'date': sale['date'] + timedelta(days=random.randint(1, 7)),
                        'tenant_id': product['tenant_id'],
                        'product_id': product['id'],
                        'warehouse_id': random.choice(self.warehouses)['id'],
                        'transaction_type': 'in',
                        'quantity': restock_quantity,
                        'reason': 'restock',
                        'reference_id': f"PO-{random.randint(1000, 9999)}",
                        'reference_type': 'purchase_order',
                        'notes': f"Restock transaction for {product['name']}",
                        'cost_price': product['cost_price'],
                        'total_value': product['cost_price'] * restock_quantity
                    })
        
        return pd.DataFrame(transactions_data)
    
    def _get_sales_for_product(self, product: Dict, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get sales data for a specific product"""
        sales = []
        current_date = start_date
        
        while current_date <= end_date:
            if random.random() < 0.3:  # 30% chance of sale on any given day
                quantity = random.randint(1, 10)
                sales.append({
                    'date': current_date.date(),
                    'quantity': quantity,
                    'order_id': f"order-{random.randint(1000, 9999)}",
                    'order_number': f"SO-{current_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                })
            current_date += timedelta(days=1)
        
        return sales
    
    def _generate_advanced_external_factors(self, days: int) -> pd.DataFrame:
        """Generate sophisticated external factors with realistic correlations"""
        print("  🔄 Generating external factors with market correlations...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        factors_data = []
        
        for date in date_range:
            # Economic indicators
            economic_index = 100 + 0.1 * (date - start_date).days + np.random.normal(0, 2)
            
            # Weather data (affects certain product categories)
            temperature = 20 + 10 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365) + np.random.normal(0, 3)
            precipitation = max(0, 5 + 3 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365 + np.pi) + np.random.normal(0, 2))
            
            # Marketing spend (correlated with sales)
            base_marketing = 1000
            if date.month in [11, 12]:  # Holiday season
                base_marketing *= 2
            marketing_spend = base_marketing + np.random.normal(0, 200)
            
            # Competitor activity
            competitor_activity = 0.5 + 0.3 * np.sin(2 * np.pi * date.month / 12) + np.random.normal(0, 0.1)
            
            # Social media sentiment
            sentiment = 0.5 + 0.2 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365) + np.random.normal(0, 0.1)
            
            # Supply chain disruptions
            disruption_factor = 1.0
            if random.random() < 0.02:  # 2% chance of disruption
                disruption_factor = random.uniform(0.7, 0.9)
            
            factors_data.append({
                'date': date.date(),
                'temperature': round(temperature, 1),
                'precipitation': round(precipitation, 1),
                'economic_index': round(economic_index, 1),
                'marketing_spend': round(marketing_spend, 0),
                'competitor_activity': round(competitor_activity, 2),
                'social_sentiment': round(sentiment, 2),
                'supply_disruption': round(disruption_factor, 2),
                'is_weekend': date.weekday() >= 5,
                'is_holiday': date.month in [12, 1, 7],
                'is_month_end': date.day >= 25,
                'is_quarter_end': date.month in [3, 6, 9, 12] and date.day >= 25
            })
        
        return pd.DataFrame(factors_data)
    
    def _generate_tenant_metrics(self) -> pd.DataFrame:
        """Generate tenant performance metrics"""
        print("  🔄 Generating tenant performance metrics...")
        
        metrics_data = []
        
        for tenant in self.tenants:
            # Calculate metrics for this tenant
            total_revenue = random.uniform(100000, 1000000)
            total_orders = random.randint(500, 5000)
            avg_order_value = total_revenue / total_orders
            
            metrics_data.append({
                'tenant_id': tenant['id'],
                'tenant_name': tenant['name'],
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'avg_order_value': avg_order_value,
                'customer_count': random.randint(100, 1000),
                'product_count': len([p for p in self.products if p['tenant_id'] == tenant['id']]),
                'inventory_value': random.uniform(50000, 500000),
                'profit_margin': random.uniform(0.15, 0.35),
                'customer_satisfaction': random.uniform(3.5, 5.0),
                'order_fulfillment_rate': random.uniform(0.85, 0.98),
                'inventory_turnover': random.uniform(4, 12),
                'days_sales_outstanding': random.uniform(15, 45)
            })
        
        return pd.DataFrame(metrics_data)
    
    def _generate_product_analytics(self) -> pd.DataFrame:
        """Generate product performance analytics"""
        print("  🔄 Generating product performance analytics...")
        
        analytics_data = []
        
        for product in self.products:
            # Calculate product metrics
            total_sold = random.randint(100, 5000)
            total_revenue = total_sold * product['selling_price']
            profit_margin = (product['selling_price'] - product['cost_price']) / product['selling_price']
            
            analytics_data.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'product_sku': product['sku'],
                'tenant_id': product['tenant_id'],
                'tenant_name': product['tenant_name'],
                'category': product['category'],
                'total_sold': total_sold,
                'total_revenue': total_revenue,
                'avg_daily_sales': total_sold / 365,
                'profit_margin': profit_margin,
                'total_profit': total_sold * (product['selling_price'] - product['cost_price']),
                'price_elasticity': random.uniform(-1.5, -0.5),
                'market_share': random.uniform(0.01, 0.15),
                'customer_rating': random.uniform(3.0, 5.0),
                'return_rate': random.uniform(0.01, 0.05),
                'demand_pattern': product['demand_pattern'],
                'business_type': product['business_type']
            })
        
        return pd.DataFrame(analytics_data)
    
    def _generate_demand_patterns(self, days: int) -> pd.DataFrame:
        """Generate detailed demand patterns for ML training"""
        print("  🔄 Generating demand patterns with seasonality and trends...")
        
        patterns_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for product in self.products:
            # Generate sophisticated demand pattern
            demand_series = self._generate_demand_pattern(date_range, product['demand_pattern'], product['business_type'])
            
            for i, date in enumerate(date_range):
                patterns_data.append({
                    'date': date.date(),
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'tenant_id': product['tenant_id'],
                    'demand': max(0, int(demand_series[i])),
                    'demand_pattern': product['demand_pattern'],
                    'business_type': product['business_type'],
                    'price': product['selling_price'],
                    'cost': product['cost_price'],
                    'profit_margin': (product['selling_price'] - product['cost_price']) / product['selling_price'],
                    'day_of_week': date.weekday(),
                    'month': date.month,
                    'quarter': date.quarter,
                    'is_weekend': date.weekday() >= 5,
                    'is_holiday': date.month in [12, 1, 7],
                    'is_month_end': date.day >= 25
                })
        
        return pd.DataFrame(patterns_data)
    
    def save_datasets(self, datasets: Dict[str, pd.DataFrame], output_dir: str = "ml/data") -> Dict[str, str]:
        """Save all datasets to files"""
        print("💾 Saving datasets to files...")
        
        os.makedirs(output_dir, exist_ok=True)
        saved_files = {}
        
        for name, df in datasets.items():
            filename = f"{name}_dataset.csv"
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False)
            saved_files[name] = filepath
            print(f"  ✅ Saved {name}: {len(df)} records -> {filepath}")
        
        # Create comprehensive summary
        summary = {
            'generated_at': datetime.now().isoformat(),
            'datasets': {},
            'total_records': 0,
            'date_range': {
                'start': min([df['date'].min() for df in datasets.values() if 'date' in df.columns]).isoformat(),
                'end': max([df['date'].max() for df in datasets.values() if 'date' in df.columns]).isoformat()
            },
            'tenants': len(self.tenants),
            'products': len(self.products),
            'categories': len(self.categories),
            'suppliers': len(self.suppliers),
            'warehouses': len(self.warehouses)
        }
        
        for name, df in datasets.items():
            summary['datasets'][name] = {
                'records': len(df),
                'columns': list(df.columns),
                'file_path': saved_files[name]
            }
            summary['total_records'] += len(df)
        
        summary_file = os.path.join(output_dir, 'dataset_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Dataset summary saved: {summary_file}")
        print(f"🎯 Total records generated: {summary['total_records']:,}")
        
        return saved_files


def main():
    """Main function to generate comprehensive dataset"""
    print("🚀 Starting Standalone Dataset Generation for ML Training")
    print("=" * 60)
    
    # Initialize generator
    generator = StandaloneDatasetGenerator()
    
    # Generate comprehensive dataset
    datasets = generator.generate_comprehensive_dataset(
        num_tenants=5,  # Generate 5 tenants
        days=730        # 2 years of data
    )
    
    # Save datasets
    saved_files = generator.save_datasets(datasets)
    
    print("\n" + "=" * 60)
    print("✅ Dataset Generation Completed Successfully!")
    print("\n📁 Generated Files:")
    for name, filepath in saved_files.items():
        print(f"  • {name}: {filepath}")
    
    print(f"\n🎯 Dataset Statistics:")
    print(f"  • Total Records: {sum(len(df) for df in datasets.values()):,}")
    print(f"  • Tenants: {len(generator.tenants)}")
    print(f"  • Products: {len(generator.products)}")
    print(f"  • Date Range: {datasets['sales']['date'].min()} to {datasets['sales']['date'].max()}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Run ML training: python ml/scripts/train_standalone_models.py")
    print(f"  2. Test predictions: python ml/scripts/test_standalone_predictions.py")
    print(f"  3. Start ML service: uvicorn ml.main:app --reload --port 8001")


if __name__ == '__main__':
    main()
