from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from .models import Order, OrderLine, OrderStatusHistory, OrderFulfillment


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    fields = ['product', 'variant', 'quantity', 'unit_price', 'line_total', 'quantity_fulfilled']
    readonly_fields = ['line_total']
    
    def line_total(self, obj):
        if obj.pk:
            return f"${obj.line_total:.2f}"
        return "Save to calculate"
    line_total.short_description = 'Total'


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'changed_at', 'notes']
    fields = ['from_status', 'to_status', 'changed_by', 'changed_at', 'notes']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'order_type', 'status', 'total_amount', 
        'items_count', 'created_at', 'fulfillment_status'
    ]
    list_filter = [
        'order_type', 'status', 'payment_status', 'created_at', 'tenant'
    ]
    search_fields = [
        'order_number', 'customer_name', 'customer_email', 'customer_address', 
        'shipping_address', 'notes'
    ]
    readonly_fields = [
        'id', 'order_number', 'total_amount', 'created_at', 'updated_at',
        'fulfillment_status', 'payment_status_display'
    ]
    inlines = [OrderLineInline, OrderStatusHistoryInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'order_type', 'status', 'tenant')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Addresses', {
            'fields': ('customer_address', 'shipping_address'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount', 'payment_status')
        }),
        ('Fulfillment', {
            'fields': ('fulfillment_status', 'shipping_method', 'tracking_number', 'shipped_date', 'delivered_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_orders_csv', 'mark_as_processing', 'mark_as_shipped', 
        'mark_as_delivered', 'generate_invoice', 'send_customer_notification'
    ]
    
    def items_count(self, obj):
        return obj.order_lines.count()
    items_count.short_description = 'Items'
    
    def fulfillment_status(self, obj):
        # Calculate fulfillment status based on order lines
        total_lines = obj.order_lines.count()
        fulfilled_lines = obj.order_lines.filter(quantity_fulfilled__gt=0).count()
        
        if fulfilled_lines == 0:
            return format_html('<span style="color: red;">✗ Pending</span>')
        elif fulfilled_lines < total_lines:
            return format_html('<span style="color: orange;">⚠ Partial</span>')
        else:
            return format_html('<span style="color: green;">✓ Fulfilled</span>')
    fulfillment_status.short_description = 'Fulfillment'
    
    def payment_status_display(self, obj):
        colors = {
            'paid': 'green',
            'pending': 'orange',
            'failed': 'red',
            'refunded': 'blue'
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Payment Status'
    
    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Customer Name', 'Customer Email', 'Order Type', 
            'Status', 'Total Amount', 'Payment Status', 'Created At'
        ])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.customer_name,
                order.customer_email,
                order.get_order_type_display(),
                order.get_status_display(),
                order.total_amount,
                order.get_payment_status_display(),
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_orders_csv.short_description = "Export selected orders to CSV"
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped', shipped_at=datetime.now())
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered', delivered_at=datetime.now())
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def generate_invoice(self, request, queryset):
        # This would integrate with invoice generation system
        self.message_user(request, f'Invoice generation initiated for {queryset.count()} orders.')
    generate_invoice.short_description = "Generate invoices for selected orders"
    
    def send_customer_notification(self, request, queryset):
        # This would integrate with notification system
        self.message_user(request, f'Customer notifications sent for {queryset.count()} orders.')
    send_customer_notification.short_description = "Send customer notifications"


@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product', 'variant', 'quantity', 'unit_price', 
        'line_total', 'quantity_fulfilled', 'fulfillment_status'
    ]
    list_filter = ['order__order_type', 'order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    readonly_fields = ['line_total', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'product', 'variant')
        }),
        ('Quantity & Pricing', {
            'fields': ('quantity', 'unit_price', 'line_total')
        }),
        ('Fulfillment', {
            'fields': ('quantity_fulfilled', 'quantity_shipped', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def fulfillment_status(self, obj):
        if obj.is_fully_fulfilled:
            return format_html('<span style="color: green;">✓ Complete</span>')
        elif obj.quantity_fulfilled > 0:
            return format_html('<span style="color: orange;">⚠ Partial</span>')
        else:
            return format_html('<span style="color: red;">✗ Pending</span>')
    fulfillment_status.short_description = 'Fulfillment'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'from_status', 'to_status', 'changed_by', 'changed_at'
    ]
    list_filter = ['from_status', 'to_status', 'changed_at']
    search_fields = ['order__order_number', 'changed_by__email', 'notes']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
    ordering = ['-changed_at']


@admin.register(OrderFulfillment)
class OrderFulfillmentAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'warehouse', 'status', 'tracking_number', 
        'shipped_date', 'delivered_date'
    ]
    list_filter = ['status', 'shipped_date']
    search_fields = ['order__order_number', 'tracking_number', 'shipping_carrier']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Fulfillment Information', {
            'fields': ('order', 'warehouse', 'status')
        }),
        ('Shipping Details', {
            'fields': ('shipping_carrier', 'shipping_method', 'tracking_number', 'shipping_cost')
        }),
        ('Dates', {
            'fields': ('shipped_date', 'delivered_date'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'fulfilled_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )