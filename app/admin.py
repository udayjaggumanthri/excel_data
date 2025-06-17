from django.contrib import admin
from .models import ProcessedData
from django.http import HttpResponse
import xlwt
from datetime import datetime
from django.utils import timezone
from rangefilter.filters import DateRangeFilter

@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('image_number', 'serial_number', 'username', 'customer_name', 'city_state', 
                   'purchase_value_and_down_payment', 'loan_period_and_interest', 
                   'loan_amount_and_principal', 'insurance_and_pmi', 'formatted_property_tax', 'entry_timestamp')
    list_filter = (('entry_timestamp', DateRangeFilter), 'image_number', 'username')
    search_fields = ('image_number', 'username', 'customer_name', 'customer_reference_number', 'guarantor_name')
    readonly_fields = ('entry_timestamp', 'loan_period_and_interest', 
                      'purchase_value_and_down_payment', 'loan_amount_and_principal',
                      'insurance_and_pmi', 'formatted_property_tax')
    actions = ['export_to_excel']
    
    def export_to_excel(self, request, queryset):
        """Export selected records to Excel"""
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="processed_data.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Processed Data')

        # Write headers
        headers = [
            'Image Number',
            'Serial Number',
            'Username',
            'Customer Reference Number',
            'Customer Name',
            'City, State',
            'Purchase Value and Down Payment',
            'Loan Period and Annual Interest',
            'Guarantor Name',
            'Guarantor Reference Number',
            'Loan Amount and Principal',
            'Total Interest for Loan Period and Property Tax for Loan Period',
            'Property Insurance per Month and PMI per Annum'
        ]
        
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        for col_num, header in enumerate(headers):
            ws.write(0, col_num, header, font_style)

        # Write data rows
        font_style = xlwt.XFStyle()
        row_num = 1
        
        for obj in queryset:
            row = [
                obj.image_number,
                obj.serial_number,
                obj.username,
                obj.customer_reference_number,
                obj.customer_name,
                obj.city_state,
                f"{obj.format_purchase_value()} AND {obj.down_payment_percent} %",
                f"{obj.loan_period_years} YEARS AND {obj.annual_interest_rate} %",
                obj.guarantor_name,
                obj.guarantor_reference_number or '',
                f"{obj.format_number_with_commas(obj.loan_amount)} AND {obj.format_number_with_commas(obj.final_principal)}",
                f"{obj.format_number_with_commas(obj.total_interest_for_period)} AND {obj.formatted_property_tax}",
                f"{obj.format_number_with_commas(obj.property_insurance_per_month)} AND {obj.format_number_with_commas(obj.pmi_per_annum) if obj.pmi_per_annum else 'NA'}"
            ]
            
            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, str(cell_value), font_style)
            row_num += 1

        wb.save(response)
        return response
    export_to_excel.short_description = "Export selected records to Excel"
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image_number', 'serial_number', 'customer_reference_number')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'city_state')
        }),
        ('Purchase Value and Down Payment', {
            'fields': ('purchase_value_excel', 'down_payment_percent', 'purchase_value_and_down_payment')
        }),
        ('Loan Period and Interest', {
            'fields': ('loan_period_years', 'annual_interest_rate', 'loan_period_and_interest')
        }),
        ('Loan Amount and Principal', {
            'fields': ('loan_amount', 'final_principal', 'loan_amount_and_principal')
        }),
        ('Insurance Information', {
            'fields': ('property_insurance_per_month', 'pmi_per_annum', 'insurance_and_pmi')
        }),
        ('Total Interest', {
            'fields': ('total_interest_for_period',)
        }),
        ('Property Tax Information', {
            'fields': ('assessment_reduction_rate', 'property_tax_per_annum', 'property_tax_for_period', 'formatted_property_tax')
        }),
        ('Guarantor Information', {
            'fields': ('guarantor_name', 'guarantor_reference_number')
        }),
        ('Metadata', {
            'fields': ('entry_timestamp',)
        }),
    )
    
    list_per_page = 20
    save_on_top = True
    ordering = ('-entry_timestamp',)

    def save_model(self, request, obj, form, change):
        if obj.customer_reference_number:
            obj.customer_reference_number = obj.customer_reference_number.strip().upper().replace(' ', '   ')
        super().save_model(request, obj, form, change)
