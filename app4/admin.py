from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.http import HttpResponse
from rangefilter.filters import DateRangeFilter
from .models import CustomerData
import csv
import io
from datetime import datetime

# Register your models here.

@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name', 
        'customer_reference_number', 
        'emp_id', 
        'purchase_value', 
        'city_state',
        'formatted_created_date',
        'formatted_updated_date'
    ]
    
    list_filter = [
        ('created_at', DateRangeFilter),
        ('updated_at', DateRangeFilter),
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
        }
        
        response.context_data['summary'] = metrics
        return response
    
    # Add custom actions
    actions = ['export_to_excel', 'export_to_csv', 'mark_as_processed']
    
    def export_to_excel(self, request, queryset):
        """Export selected records to Excel"""
        try:
            # Try to use xlsxwriter if available
            import xlsxwriter
            return self._export_to_xlsx(queryset)
        except ImportError:
            # Fallback to CSV if xlsxwriter is not available
            self.message_user(request, "xlsxwriter not available, exporting as CSV instead.")
            return self.export_to_csv(request, queryset)
    
    def _export_to_xlsx(self, queryset):
        """Export to Excel using xlsxwriter"""
        # Create a new workbook and add a worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Customer Data')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd hh:mm',
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # Define headers
        headers = [
            'Emp ID', 'Image Number', 'Serial Number', 'Customer Reference Number',
            'Customer Name', 'City, State', 'Purchase Value', 'Purchase Value Reduction %',
            'Down Payment %', 'Loan Period (Years)', 'Annual Interest Rate %',
            'Monthly Principal Reduction %', 'Total Interest Reduction %',
            'Guarantor Name', 'Guarantor Reference Number', 'Assessment Reduction Rate %',
            'Created At', 'Updated At'
        ]
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        for row, obj in enumerate(queryset, start=1):
            worksheet.write(row, 0, obj.emp_id, cell_format)
            worksheet.write(row, 1, obj.image_number, cell_format)
            worksheet.write(row, 2, obj.serial_number, cell_format)
            worksheet.write(row, 3, obj.customer_reference_number, cell_format)
            worksheet.write(row, 4, obj.customer_name, cell_format)
            worksheet.write(row, 5, obj.city_state, cell_format)
            worksheet.write(row, 6, obj.purchase_value, cell_format)
            worksheet.write(row, 7, obj.purchase_value_reduction_percent, cell_format)
            worksheet.write(row, 8, obj.down_payment_percent, cell_format)
            worksheet.write(row, 9, obj.loan_period_years, cell_format)
            worksheet.write(row, 10, obj.annual_interest_rate_percent, cell_format)
            worksheet.write(row, 11, obj.monthly_principal_reduction_percent, cell_format)
            worksheet.write(row, 12, obj.total_interest_reduction_percent, cell_format)
            worksheet.write(row, 13, obj.guarantor_name, cell_format)
            worksheet.write(row, 14, obj.guarantor_reference_number, cell_format)
            worksheet.write(row, 15, obj.assessment_reduction_rate_percent, cell_format)
            worksheet.write(row, 16, obj.created_at, date_format)
            worksheet.write(row, 17, obj.updated_at, date_format)
        
        # Set column widths
        column_widths = [15, 15, 15, 25, 25, 20, 20, 25, 15, 20, 20, 25, 25, 25, 25, 25, 20, 20]
        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)
        
        workbook.close()
        output.seek(0)
        
        # Create the HTTP response
        filename = f"customer_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    export_to_excel.short_description = "Export selected records to Excel"
    
    def export_to_csv(self, request, queryset):
        """Export selected records to CSV"""
        response = HttpResponse(content_type='text/csv')
        filename = f"customer_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write headers
        headers = [
            'Emp ID', 'Image Number', 'Serial Number', 'Customer Reference Number',
            'Customer Name', 'City, State', 'Purchase Value', 'Purchase Value Reduction %',
            'Down Payment %', 'Loan Period (Years)', 'Annual Interest Rate %',
            'Monthly Principal Reduction %', 'Total Interest Reduction %',
            'Guarantor Name', 'Guarantor Reference Number', 'Assessment Reduction Rate %',
            'Created At', 'Updated At'
        ]
        writer.writerow(headers)
        
        # Write data
        for obj in queryset:
            writer.writerow([
                obj.emp_id, obj.image_number, obj.serial_number, obj.customer_reference_number,
                obj.customer_name, obj.city_state, obj.purchase_value, obj.purchase_value_reduction_percent,
                obj.down_payment_percent, obj.loan_period_years, obj.annual_interest_rate_percent,
                obj.monthly_principal_reduction_percent, obj.total_interest_reduction_percent,
                obj.guarantor_name, obj.guarantor_reference_number, obj.assessment_reduction_rate_percent,
                obj.created_at.strftime('%Y-%m-%d %H:%M:%S'), obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        self.message_user(request, f"Successfully exported {queryset.count()} records to CSV.")
        return response
    
    export_to_csv.short_description = "Export selected records to CSV"
    
    def mark_as_processed(self, request, queryset):
        """Mark selected records as processed"""
        # This is a placeholder - you can implement actual processing logic
        self.message_user(request, f"Marked {queryset.count()} records as processed.")
    mark_as_processed.short_description = "Mark as processed"
