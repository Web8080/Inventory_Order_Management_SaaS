from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Supplier, Product, ProductVariant, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['sku', 'name', 'cost_price', 'selling_price', 'reorder_point', 'reorder_quantity', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['sort_order', 'name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Business Details', {
            'fields': ('payment_terms', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'name', 'category', 'supplier', 'current_stock', 
        'cost_price', 'selling_price', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'is_tracked', 'category', 'supplier', 'created_at']
    search_fields = ['sku', 'name', 'description', 'barcode']
    readonly_fields = ['id', 'margin_percentage', 'created_at', 'updated_at']
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'name', 'description', 'category', 'supplier', 'is_active')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'margin_percentage')
        }),
        ('Inventory Settings', {
            'fields': ('unit', 'reorder_point', 'reorder_quantity', 'max_stock_level', 'is_tracked')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions', 'barcode', 'image')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_stock(self, obj):
        stock = obj.current_stock
        if stock is None:
            return "N/A"
        color = 'red' if obj.is_low_stock else 'green'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            stock
        )
    current_stock.short_description = 'Current Stock'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'name', 'cost_price', 'selling_price', 'current_stock', 'is_active']
    list_filter = ['is_active', 'product__category', 'created_at']
    search_fields = ['sku', 'name', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def current_stock(self, obj):
        return obj.current_stock
    current_stock.short_description = 'Current Stock'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['id', 'created_at']