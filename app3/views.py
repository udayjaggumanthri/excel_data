from django.shortcuts import render, redirect
from django.contrib import messages
from .calculator import LoanCalculator

def home3(request):
    if request.method == 'POST':
        try:
            # Create calculator instance
            calculator = LoanCalculator()
            
            # Calculate all values
            calculator.calculate(request.POST)
            
            # Prepare context for results page
            context = {
                'image_number': calculator.image_number,
                'username': calculator.username,
                'customer_reference_number': calculator.customer_reference_number,
                'customer_name': calculator.customer_name,
                'city_state': calculator.city_state,
                'guarantor_name': calculator.guarantor_name,
                'guarantor_reference_number': calculator.guarantor_reference_number,
                'purchase_value_and_down_payment': calculator.purchase_value_and_down_payment,
                'loan_period_and_interest': calculator.loan_period_and_interest,
                'loan_amount_and_principal': calculator.loan_amount_and_principal,
                'total_interest_for_period': calculator.format_number_with_commas(calculator.total_interest_for_period),
                'insurance_and_pmi': calculator.insurance_and_pmi
            }
            
            messages.success(request, 'Calculations completed successfully!')
            return render(request, 'app3/results.html', context)

        except Exception as e:
            messages.error(request, f'Error processing data: {str(e)}')
            return redirect('app3:home3')

    return render(request, 'app3/home.html')
