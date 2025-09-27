// API Types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  tenant: string;
  tenant_name: string;
  role: 'owner' | 'manager' | 'clerk';
  phone?: string;
  avatar?: string;
  is_tenant_admin: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: 'free' | 'basic' | 'premium' | 'enterprise';
  is_active: boolean;
  user_count: number;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  subscription_status: string;
  timezone: string;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  category?: string;
  supplier?: string;
  cost_price: number;
  selling_price: number;
  margin_percentage: number;
  unit: string;
  reorder_point: number;
  reorder_quantity: number;
  max_stock_level?: number;
  weight?: number;
  dimensions?: string;
  barcode?: string;
  is_active: boolean;
  is_tracked: boolean;
  image?: string;
  current_stock?: number;
  is_low_stock?: boolean;
  stock_value?: number;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: string;
  order_number: string;
  order_type: 'sale' | 'purchase' | 'return' | 'transfer';
  status: 'draft' | 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'completed';
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  customer_address?: string;
  supplier?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_amount: number;
  total_amount: number;
  payment_status: 'pending' | 'partial' | 'paid' | 'refunded' | 'failed';
  payment_method?: string;
  payment_reference?: string;
  shipping_address?: string;
  shipping_method?: string;
  tracking_number?: string;
  order_date: string;
  required_date?: string;
  shipped_date?: string;
  delivered_date?: string;
  notes?: string;
  internal_notes?: string;
  created_by?: string;
  updated_by?: string;
  line_count: number;
  total_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface OrderLine {
  id: string;
  order: string;
  product: string;
  variant?: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  discount_amount: number;
  line_total: number;
  quantity_fulfilled: number;
  quantity_shipped: number;
  notes?: string;
  remaining_quantity: number;
  is_fully_fulfilled: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockItem {
  id: string;
  product: string;
  variant?: string;
  warehouse: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  is_low_stock: boolean;
  last_updated: string;
  created_at: string;
}

export interface Warehouse {
  id: string;
  name: string;
  code: string;
  address?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockAlert {
  id: string;
  product: string;
  variant?: string;
  warehouse: string;
  alert_type: 'low_stock' | 'out_of_stock' | 'overstock' | 'reorder';
  status: 'active' | 'acknowledged' | 'resolved';
  current_quantity: number;
  threshold_quantity: number;
  message: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
}

export interface Forecast {
  product_id: string;
  product_name: string;
  forecasts: Array<{
    date: string;
    forecast: number;
    day: number;
  }>;
  confidence_intervals: Array<{
    date: string;
    lower: number;
    upper: number;
  }>;
  model_metrics: {
    mae: number;
    rmse: number;
    r2: number;
  };
}

export interface Integration {
  id: string;
  name: string;
  integration_type: 'shopify' | 'woocommerce' | 'amazon' | 'ebay' | 'quickbooks' | 'xero';
  status: 'inactive' | 'active' | 'error' | 'pending';
  api_key?: string;
  base_url?: string;
  config: Record<string, any>;
  is_enabled: boolean;
  auto_sync_products: boolean;
  auto_sync_orders: boolean;
  auto_sync_inventory: boolean;
  sync_frequency_minutes: number;
  last_sync_at?: string;
  last_sync_status?: string;
  last_sync_error?: string;
  created_at: string;
  updated_at: string;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm_password: string;
  tenant_name: string;
  tenant_slug: string;
  phone?: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    refresh: string;
    access: string;
  };
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Form Types
export interface ProductFormData {
  sku: string;
  name: string;
  description?: string;
  category?: string;
  supplier?: string;
  cost_price: number;
  selling_price: number;
  unit: string;
  reorder_point: number;
  reorder_quantity: number;
  max_stock_level?: number;
  weight?: number;
  dimensions?: string;
  barcode?: string;
  is_active: boolean;
  is_tracked: boolean;
}

export interface OrderFormData {
  order_type: 'sale' | 'purchase' | 'return' | 'transfer';
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  customer_address?: string;
  supplier?: string;
  notes?: string;
  internal_notes?: string;
  order_lines: Array<{
    product: string;
    variant?: string;
    quantity: number;
    unit_price: number;
    discount_percentage?: number;
    notes?: string;
  }>;
}

// Dashboard Types
export interface DashboardStats {
  total_products: number;
  total_orders: number;
  total_revenue: number;
  low_stock_items: number;
  pending_orders: number;
  top_products: Array<{
    product_id: string;
    product_name: string;
    quantity_sold: number;
    revenue: number;
  }>;
  recent_orders: Order[];
  stock_alerts: StockAlert[];
}

// Chart Types
export interface ChartData {
  name: string;
  value: number;
  date?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  label?: string;
}
