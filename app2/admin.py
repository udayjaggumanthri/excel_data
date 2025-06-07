from django.contrib import admin
from django.http import HttpResponse
import xlwt
from .models import ProcessedData2

@admin.register(ProcessedData2)
class ProcessedData2Admin(admin.ModelAdmin):
    list_display = ('image_number', 'serial_number', 'username', 'customer_name', 'city_state', 'entry_timestamp')
    list_filter = ('entry_timestamp', 'username', 'city_state')
    search_fields = ('image_number', 'serial_number', 'username', 'customer_name', 'customer_reference_number', 'guarantor_name')
    readonly_fields = ('entry_timestamp', 'reduced_value', 'down_payment_value', 'loan_amount', 'annual_principal',
                      'monthly_principal', 'final_principal', 'interest_per_annum', 'total_interest_for_period',
                      'final_total_interest', 'pmi_per_annum')
    actions = ['export_to_excel']

    def export_to_excel(self, request, queryset):
        """Export selected records to Excel"""
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="processed_data2.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Processed Data 2')

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
            'Total Interest for Loan Period',
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
                obj.format_number_with_commas(obj.total_interest_for_period),
                f"{obj.format_number_with_commas(obj.property_insurance_per_month)} AND {obj.format_number_with_commas(obj.pmi_per_annum) if obj.pmi_per_annum else 'NA'}"
            ]
            
            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, str(cell_value), font_style)
            row_num += 1

        wb.save(response)
        return response
    export_to_excel.short_description = "Export selected records to Excel"

    fieldsets = (
        ('Basic Information', {
            'fields': ('image_number', 'serial_number', 'username', 'customer_reference_number', 'customer_name', 'city_state')
        }),
        ('Guarantor Information', {
            'fields': ('guarantor_name', 'guarantor_reference_number')
        }),
        ('Financial Information', {
            'fields': ('purchase_value', 'down_payment_percent', 'loan_period_years', 'annual_interest_rate',
                      'property_insurance_per_month')
        }),
        ('Calculated Values', {
            'fields': ('reduced_value', 'down_payment_value', 'loan_amount', 'annual_principal',
                      'monthly_principal', 'final_principal', 'interest_per_annum',
                      'total_interest_for_period', 'final_total_interest', 'pmi_per_annum')
        }),
        ('Metadata', {
            'fields': ('entry_timestamp',)
        }),
    )
