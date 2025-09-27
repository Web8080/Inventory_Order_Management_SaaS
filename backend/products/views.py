from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Category, Supplier, Product, ProductVariant, ProductImage
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    ProductVariantSerializer, ProductImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    @extend_schema(
        summary="Get category tree",
        description="Get hierarchical category structure"
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_tracked', 'category', 'supplier']
    search_fields = ['sku', 'name', 'description', 'barcode']
    ordering_fields = ['name', 'sku', 'created_at', 'selling_price']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter products by tenant and add stock information"""
        queryset = super().get_queryset()
        
        # Add current stock information
        for product in queryset:
            if product.is_tracked:
                product.current_stock = product.current_stock
                product.is_low_stock = product.is_low_stock
                product.stock_value = product.stock_value
        
        return queryset
    
    @extend_schema(
        summary="Get low stock products",
        description="Get products that are below reorder point"
    )
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = self.get_queryset().filter(is_tracked=True)
        low_stock_products = []
        
        for product in products:
            if product.is_low_stock:
                low_stock_products.append(product)
        
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get product analytics",
        description="Get analytics data for a product"
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get product analytics"""
        product = self.get_object()
        
        # Mock analytics data - in real implementation, this would query actual data
        analytics_data = {
            'product_id': product.id,
            'product_name': product.name,
            'total_sold': 150,  # Mock data
            'total_revenue': float(product.selling_price * 150),
            'avg_daily_sales': 5.2,
            'stock_turnover': 12.5,
            'profit_margin': float(product.margin_percentage),
            'last_30_days_sales': [
                {'date': '2024-01-01', 'quantity': 3},
                {'date': '2024-01-02', 'quantity': 7},
                # ... more mock data
            ]
        }
        
        return Response(analytics_data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variants"""
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['sku', 'name']


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product images"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'is_primary']
    
    @extend_schema(
        summary="Set primary image",
        description="Set an image as the primary image for a product"
    )
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set image as primary"""
        image = self.get_object()
        
        # Remove primary flag from other images of the same product
        ProductImage.objects.filter(
            product=image.product,
            is_primary=True
        ).update(is_primary=False)
        
        # Set this image as primary
        image.is_primary = True
        image.save()
        
        return Response({'message': 'Primary image updated successfully'})