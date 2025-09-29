import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '../store/authStore';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const { refreshToken, setTokens, logout } = useAuthStore.getState();
      
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/refresh/`,
            { refresh: refreshToken }
          );
          
          const { access, refresh } = response.data;
          setTokens(access, refresh);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          logout();
          return Promise.reject(refreshError);
        }
      } else {
        logout();
      }
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const apiClient = {
  // Auth
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  
  register: (data: any) =>
    api.post('/auth/register/', data),
  
  refreshToken: (refresh: string) =>
    api.post('/auth/refresh/', { refresh }),
  
  getProfile: () =>
    api.get('/auth/profile/'),
  
  updateProfile: (data: any) =>
    api.put('/auth/profile/', data),
  
  changePassword: (data: any) =>
    api.post('/auth/profile/', data),
  
  // Tenants
  getCurrentTenant: () =>
    api.get('/tenants/current/'),
  
  getTenantSettings: (tenantId: string) =>
    api.get(`/tenants/${tenantId}/settings/`),
  
  updateTenantSettings: (tenantId: string, data: any) =>
    api.patch(`/tenants/${tenantId}/update_settings/`, data),
  
  // Products
  getProducts: (params?: any) =>
    api.get('/products/products/', { params }),
  
  getProduct: (id: string) =>
    api.get(`/products/products/${id}/`),
  
  createProduct: (data: any) =>
    api.post('/products/products/', data),
  
  updateProduct: (id: string, data: any) =>
    api.patch(`/products/products/${id}/`, data),
  
  deleteProduct: (id: string) =>
    api.delete(`/products/products/${id}/`),
  
  getCategories: () =>
    api.get('/products/categories/'),
  
  getSuppliers: () =>
    api.get('/products/suppliers/'),
  
  // Orders
  getOrders: (params?: any) =>
    api.get('/orders/orders/', { params }),
  
  getOrder: (id: string) =>
    api.get(`/orders/orders/${id}/`),
  
  createOrder: (data: any) =>
    api.post('/orders/orders/', data),
  
  updateOrder: (id: string, data: any) =>
    api.patch(`/orders/orders/${id}/`, data),
  
  deleteOrder: (id: string) =>
    api.delete(`/orders/orders/${id}/`),
  
  fulfillOrder: (id: string, data: any) =>
    api.post(`/orders/orders/${id}/fulfill/`, data),
  
  // Inventory
  getStockItems: (params?: any) =>
    api.get('/inventory/stock-items/', { params }),
  
  getStockItem: (id: string) =>
    api.get(`/inventory/stock-items/${id}/`),
  
  adjustStock: (data: any) =>
    api.post('/inventory/adjust/', data),
  
  getLowStock: () =>
    api.get('/inventory/low-stock/'),
  
  getStockAlerts: (params?: any) =>
    api.get('/inventory/stock-alerts/', { params }),
  
  getWarehouses: () =>
    api.get('/inventory/warehouses/'),
  
  // Integrations
  getIntegrations: () =>
    api.get('/integrations/integrations/'),
  
  getIntegration: (id: string) =>
    api.get(`/integrations/integrations/${id}/`),
  
  createIntegration: (data: any) =>
    api.post('/integrations/integrations/', data),
  
  updateIntegration: (id: string, data: any) =>
    api.patch(`/integrations/integrations/${id}/`, data),
  
  deleteIntegration: (id: string) =>
    api.delete(`/integrations/integrations/${id}/`),
  
  syncIntegration: (id: string, data: any) =>
    api.post(`/integrations/integrations/${id}/sync/`, data),
  
  // ML/Forecasting
  getForecasts: (data: any) =>
    api.post('http://localhost:8001/forecast', data),
  
  getOptimizations: (data: any) =>
    api.post('http://localhost:8001/optimize', data),
  
  trainModels: (data: any) =>
    api.post('http://localhost:8001/train', data),
};

export default api;

