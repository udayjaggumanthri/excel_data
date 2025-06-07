from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import ProcessedData2

def home2(request):
    if request.method == 'POST':
        try:
            # Get form data
            image_number = request.POST.get('image_number', '')
            username = request.POST.get('username', '')
            input_text_ref = request.POST.get('input_text_ref', '')
            input_text1 = request.POST.get('input_text1', '')
            input_text2 = request.POST.get('input_text2', '')
            input_text3 = request.POST.get('input_text3', '')
            input_text4 = request.POST.get('input_text4', '')
            input_text_guarantor_ref = request.POST.get('input_text_guarantor_ref', '')
            
            # Get and validate financial data
            purchase_value_reduction = Decimal(request.POST.get('purchase_value_reduction', '0'))
            down_payment = Decimal(request.POST.get('down_payment', '0'))
            loan_period = int(request.POST.get('loan_period', '0'))
            annual_interest = Decimal(request.POST.get('annual_interest', '0'))
            monthly_principal_reduction = Decimal(request.POST.get('monthly_principal_reduction', '0'))
            total_interest_reduction = Decimal(request.POST.get('total_interest_reduction', '0'))

            # Process the purchase value text to get numeric value
            # This is where you'd implement the text-to-number conversion
            # For now, let's assume a simple conversion
            purchase_value = Decimal('100000')  # Replace with actual conversion

            # Create and save the processed data
            processed_data = ProcessedData2(
                image_number=image_number,
                username=username,
                customer_reference_number=input_text_ref,
                customer_name=input_text1,
                city_state=input_text3,
                guarantor_name=input_text2,
                guarantor_reference_number=input_text_guarantor_ref,
                purchase_value=purchase_value,
                down_payment_percent=str(down_payment),
                loan_period_years=loan_period,
                annual_interest_rate=annual_interest,
                property_insurance_per_month=Decimal('100')  # Replace with actual calculation
            )
            processed_data.save()

            # Prepare context for results page
            context = {
                'image_number': processed_data.image_number,
                'username': processed_data.username,
                'processed_text_ref': processed_data.customer_reference_number,
                'processed_text1': processed_data.customer_name,
                'processed_text2': processed_data.guarantor_name,
                'processed_text3': processed_data.city_state,
                'processed_text_guarantor_ref': processed_data.guarantor_reference_number,
                'financial_data': processed_data
            }
            
            messages.success(request, 'Data processed successfully!')
            return render(request, 'app2/results.html', context)

        except Exception as e:
            messages.error(request, f'Error processing data: {str(e)}')
            return redirect('home2')

    return render(request, 'app2/home.html')
