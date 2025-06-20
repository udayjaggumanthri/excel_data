from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from rangefilter.filters import DateRangeFilter, NumericRangeFilter
from .models import CustomerData

# Register your models here.

@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name', 
        'customer_reference_number', 
        'emp_id', 
        'formatted_purchase_value', 
        'city_state',
        'formatted_created_date',
        'formatted_updated_date'
    ]
    
    list_filter = [
        ('created_at', DateRangeFilter),
        ('updated_at', DateRangeFilter),
        ('purchase_value', NumericRangeFilter),
        ('loan_period_years', NumericRangeFilter),
        'city_state', 
        'emp_id'
    ]
    
    search_fields = [
        'customer_name', 
        'customer_reference_number', 
        'emp_id', 
        'guarantor_name',
        'city_state'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    # Enable list editable for quick editing
    list_editable = ['city_state']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('emp_id', 'image_number', 'serial_number', 'customer_reference_number')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'city_state')
        }),
        ('Financial Information', {
            'fields': (
                'purchase_value', 
                'purchase_value_reduction_percent', 
                'down_payment_percent',
                'loan_period_years',
                'annual_interest_rate_percent'
            )
        }),
        ('Reduction Rates', {
            'fields': (
                'monthly_principal_reduction_percent',
                'total_interest_reduction_percent',
                'assessment_reduction_rate_percent'
            )
        }),
        ('Guarantor Information', {
            'fields': ('guarantor_name', 'guarantor_reference_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_created_date(self, obj):
        """Format created date for better display"""
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    formatted_created_date.short_description = 'Created Date'
    formatted_created_date.admin_order_field = 'created_at'
    
    def formatted_updated_date(self, obj):
        """Format updated date for better display"""
        if obj.updated_at:
            return obj.updated_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    formatted_updated_date.short_description = 'Updated Date'
    formatted_updated_date.admin_order_field = 'updated_at'
    
    def formatted_purchase_value(self, obj):
        """Format purchase value with currency symbol"""
        if obj.purchase_value:
            return f"₹{obj.purchase_value:,.2f}"
        return '-'
    formatted_purchase_value.short_description = 'Purchase Value'
    formatted_purchase_value.admin_order_field = 'purchase_value'
    
    def get_queryset(self, request):
        """Custom queryset with optimized queries"""
        return super().get_queryset(request).select_related()
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view with additional context"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        # Add summary statistics
        metrics = {
            'total_records': qs.count(),
            'total_purchase_value': sum(qs.values_list('purchase_value', flat=True)) or 0,
            'avg_loan_period': qs.aggregate(avg=models.Avg('loan_period_years'))['avg'] or 0,
            'avg_interest_rate': qs.aggregate(avg=models.Avg('annual_interest_rate_percent'))['avg'] or 0,
        }
        
        response.context_data['summary'] = metrics
        return response
    
    # Add custom actions
    actions = ['export_selected', 'mark_as_processed']
    
    def export_selected(self, request, queryset):
        """Export selected records"""
        # This is a placeholder - you can implement actual export logic
        self.message_user(request, f"Export functionality for {queryset.count()} records would be implemented here.")
    export_selected.short_description = "Export selected records"
    
    def mark_as_processed(self, request, queryset):
        """Mark selected records as processed"""
        # This is a placeholder - you can implement actual processing logic
        self.message_user(request, f"Marked {queryset.count()} records as processed.")
    mark_as_processed.short_description = "Mark as processed"
