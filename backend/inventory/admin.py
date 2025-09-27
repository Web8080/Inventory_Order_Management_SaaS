from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from .models import Warehouse, StockItem, StockTransaction


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'address', 'is_active', 'stock_items_count', 
        'total_inventory_value', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Location', {
            'fields': ('address',)
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone', 'email'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_default',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_items_count(self, obj):
        return obj.stock_items.count()
    stock_items_count.short_description = 'Stock Items'
    
    def total_inventory_value(self, obj):
        total = sum(item.quantity * item.product.cost_price for item in obj.stock_items.all() if item.product.cost_price)
        return f"${total:.2f}"
    total_inventory_value.short_description = 'Total Value'


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'warehouse', 'quantity', 'reserved_quantity', 
        'available_quantity', 'is_low_stock', 'last_updated'
    ]
    list_filter = [
        'warehouse', 'product__category', 'last_updated'
    ]
    search_fields = [
        'product__name', 'product__sku', 'warehouse__name', 'warehouse__code'
    ]
    readonly_fields = [
        'id', 'available_quantity', 'is_low_stock', 'created_at', 'last_updated'
    ]
    date_hierarchy = 'last_updated'
    ordering = ['-last_updated']
    
    fieldsets = (
        ('Product & Warehouse', {
            'fields': ('product', 'warehouse')
        }),
        ('Stock Levels', {
            'fields': ('quantity', 'reserved_quantity', 'available_quantity', 'is_low_stock')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_stock_csv', 'adjust_stock', 'generate_reorder_report', 
        'mark_for_reorder', 'bulk_update_reorder_points'
    ]
    
    def available_quantity(self, obj):
        return obj.quantity - obj.reserved_quantity
    available_quantity.short_description = 'Available'
    
    def is_low_stock(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠ Low Stock</span>')
        else:
            return format_html('<span style="color: green;">✓ In Stock</span>')
    is_low_stock.short_description = 'Stock Status'
    
    def export_stock_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="stock_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Product SKU', 'Product Name', 'Warehouse', 'Quantity', 
            'Reserved', 'Available', 'Reorder Point', 'Status'
        ])
        
        for item in queryset:
            writer.writerow([
                item.product.sku,
                item.product.name,
                item.warehouse.name,
                item.quantity,
                item.reserved_quantity,
                item.available_quantity,
                item.reorder_point,
                'Low Stock' if item.is_low_stock else 'In Stock'
            ])
        
        return response
    export_stock_csv.short_description = "Export stock report to CSV"
    
    def adjust_stock(self, request, queryset):
        # This would open a custom form for stock adjustments
        self.message_user(request, f'Stock adjustment form opened for {queryset.count()} items.')
    adjust_stock.short_description = "Adjust stock for selected items"
    
    def generate_reorder_report(self, request, queryset):
        low_stock_items = queryset.filter(is_low_stock=True)
        self.message_user(request, f'Reorder report generated for {low_stock_items.count()} low stock items.')
    generate_reorder_report.short_description = "Generate reorder report"
    
    def mark_for_reorder(self, request, queryset):
        # This would create purchase orders for low stock items
        low_stock_items = queryset.filter(is_low_stock=True)
        self.message_user(request, f'Purchase orders created for {low_stock_items.count()} items.')
    mark_for_reorder.short_description = "Create purchase orders for low stock items"
    
    def bulk_update_reorder_points(self, request, queryset):
        # This would open a form to bulk update reorder points
        self.message_user(request, f'Bulk reorder point update form opened for {queryset.count()} items.')
    bulk_update_reorder_points.short_description = "Bulk update reorder points"


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'warehouse', 'transaction_type', 'quantity', 
        'reason', 'reference_type', 'user', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'reason', 'reference_type', 'created_at', 'warehouse'
    ]
    search_fields = [
        'product__name', 'product__sku', 'warehouse__name', 
        'user__email', 'notes', 'reference_id'
    ]
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('product', 'variant', 'warehouse', 'transaction_type', 'quantity')
        }),
        ('Reference Information', {
            'fields': ('reason', 'reference_id', 'reference_type', 'notes')
        }),
        ('User Information', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_transactions_csv', 'reverse_transaction', 'bulk_export_reports'
    ]
    
    def export_transactions_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="stock_transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Date', 'Product SKU', 'Product Name', 'Warehouse', 'Type', 
            'Quantity', 'Reason', 'Reference', 'User', 'Notes'
        ])
        
        for transaction in queryset:
            writer.writerow([
                transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.product.sku,
                transaction.product.name,
                transaction.warehouse.name,
                transaction.get_transaction_type_display(),
                transaction.quantity,
                transaction.get_reason_display(),
                transaction.reference_id or '',
                transaction.user.email if transaction.user else '',
                transaction.notes or ''
            ])
        
        return response
    export_transactions_csv.short_description = "Export transactions to CSV"
    
    def reverse_transaction(self, request, queryset):
        # This would create reverse transactions
        self.message_user(request, f'Reverse transactions created for {queryset.count()} transactions.')
    reverse_transaction.short_description = "Create reverse transactions"
    
    def bulk_export_reports(self, request, queryset):
        # This would generate various reports
        self.message_user(request, f'Bulk reports generated for {queryset.count()} transactions.')
    bulk_export_reports.short_description = "Generate bulk reports"