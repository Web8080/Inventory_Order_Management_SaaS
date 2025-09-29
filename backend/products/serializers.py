from rest_framework import serializers
from .models import Category, Supplier, Product, ProductVariant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    children = serializers.SerializerMethodField()
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'parent', 'children',
            'is_active', 'sort_order', 'full_path', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """Get child categories"""
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone',
            'address', 'website', 'is_active', 'payment_terms',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'is_primary',
            'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model"""
    current_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'sku', 'name', 'cost_price',
            'selling_price', 'reorder_point', 'reorder_quantity',
            'is_active', 'current_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    current_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    stock_value = serializers.ReadOnlyField()
    margin_percentage = serializers.ReadOnlyField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'category_name',
            'supplier', 'supplier_name', 'cost_price', 'selling_price',
            'margin_percentage', 'unit', 'reorder_point', 'reorder_quantity',
            'max_stock_level', 'weight', 'dimensions', 'barcode',
            'is_active', 'is_tracked', 'image', 'current_stock',
            'is_low_stock', 'stock_value', 'images', 'variants',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'margin_percentage',
            'current_stock', 'is_low_stock', 'stock_value'
        ]
    
    def validate_sku(self, value):
        """Validate SKU uniqueness within tenant"""
        if self.instance:
            # For updates, exclude current instance
            if Product.objects.filter(
                tenant=self.context['request'].user.tenant,
                sku=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("SKU already exists")
        else:
            # For creates
            if Product.objects.filter(
                tenant=self.context['request'].user.tenant,
                sku=value
            ).exists():
                raise serializers.ValidationError("SKU already exists")
        return value
    
    def validate_barcode(self, value):
        """Validate barcode uniqueness"""
        if value:
            if self.instance:
                if Product.objects.filter(
                    barcode=value
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Barcode already exists")
            else:
                if Product.objects.filter(barcode=value).exists():
                    raise serializers.ValidationError("Barcode already exists")
        return value
    
    def validate(self, data):
        """Validate product data"""
        # Ensure selling price is greater than cost price
        if data.get('selling_price', 0) <= data.get('cost_price', 0):
            raise serializers.ValidationError(
                "Selling price must be greater than cost price"
            )
        
        # Ensure reorder point is positive
        if data.get('reorder_point', 0) < 0:
            raise serializers.ValidationError(
                "Reorder point must be non-negative"
            )
        
        # Ensure reorder quantity is positive
        if data.get('reorder_quantity', 0) <= 0:
            raise serializers.ValidationError(
                "Reorder quantity must be positive"
            )
        
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    current_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'category_name', 'supplier_name',
            'cost_price', 'selling_price', 'current_stock',
            'is_low_stock', 'is_active', 'created_at'
        ]

