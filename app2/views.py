import re
from django.shortcuts import render, redirect
from decimal import Decimal, ROUND_DOWN, getcontext
from .models import ProcessedData2
from datetime import datetime
from django.utils import timezone
from django.contrib import messages

# Decimal precision setup
# ——— Decimal Setup ———
getcontext().prec = 30  # high precision to avoid intermediate rounding

# ——— Mappings for Word‐to‐Number Conversion ———
ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90
}
SCALES = {
    "hundred":   10**2,
    "thousand":  10**3,
    "million":   10**6,
    "billion":   10**9,
    "trillion":  10**12
}

def parse_hundreds(words):
    """
    Convert up to three‐word phrases (e.g. "Five Hundred Twenty Three") → integer 523.
    """
    total = 0
    current = 0
    for w in words:
        lw = w.lower()
        if lw in ONES:
            current += ONES[lw]
        elif lw in TENS:
            current += TENS[lw]
        elif lw == "hundred":
            current *= SCALES[lw]
        # ignore any unknown tokens
    return total + current

def parse_number(text):
    """
    Parse a large spelled‐out integer with scales:
      "Four Hundred Seventy Three Billion Five Hundred Six Million ..."
    → returns a Python int.
    """
    tokens = re.findall(r"[A-Za-z]+", text)
    total = 0
    group = []
    for w in tokens:
        lw = w.lower()
        if lw in SCALES and lw != "hundred":
            group_value = parse_hundreds(group)
            total += group_value * SCALES[lw]
            group = []
        else:
            group.append(w)
    if group:
        total += parse_hundreds(group)
    return total

def convert_alphanumeric_to_decimal(s):
    """
    Convert strings like:
      "$ Four Hundred ... dollars and Twenty ... cents"
    into Decimal("XXXXXXXXX.YY").
    """
    s = s.strip()
    if s.startswith('$'):
        s = s[1:].strip()

    m = re.match(
        r"^(.*)\s+dollars\s+and\s+(.*)\s+cents$",
        s,
        flags=re.IGNORECASE
    )
    if not m:
        raise ValueError(
            "Input must be of the form '<…> dollars and <…> cents'."
        )

    dollars_text = m.group(1).strip()
    cents_text   = m.group(2).strip()

    dollars_int = parse_number(dollars_text)
    cents_int   = parse_number(cents_text)

    return Decimal(dollars_int) + (Decimal(cents_int) / Decimal(100))

def truncate_two_decimals(d: Decimal) -> Decimal:
    """
    Truncate a Decimal to exactly two decimal places (ROUND_DOWN).
    """
    return d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def format_with_commas(d: Decimal) -> str:
    """
    Format a Decimal with commas and exactly two decimal digits.
    """
    return f"{d:,.2f}"

def format_location(text):
    # Step 1: Strip and uppercase
    text = text.strip().upper()

    # Step 2: Split on comma
    if ',' not in text:
        return "Invalid format: no comma found"

    left, right = text.split(',', 1)
    left = left.strip()
    right = right.strip()

    # Step 3: Always add exactly one space before and after the comma
    formatted = f"{left} , {right}"
    return formatted

def home2(request):
    if request.method == 'POST':
        # Get image information
        image_number = request.POST.get('image_number', '')
        
        if not image_number:
            messages.error(request, "Image number is required!")
            return redirect('home2')

        # Get all form inputs
        user_input_ref = request.POST.get('input_text_ref', '')
        username = request.POST.get('username', '').strip()
        
        if not user_input_ref:
            messages.error(request, "Customer Reference Number is required!")
            return redirect('home2')

        # Process the reference number first to check uniqueness
        processed_text_ref = user_input_ref.strip().upper().replace(' ', '   ')
        
        # Check if customer reference number already exists
        if ProcessedData2.objects.filter(customer_reference_number=processed_text_ref).exists():
            messages.error(request, "This Customer Reference Number already exists!")
            return redirect('home2')

        # Get remaining form inputs
        user_input1 = request.POST.get('input_text1', '')  # Customer Name
        user_input2 = request.POST.get('input_text2', '')  # Guarantor Name
        user_input3 = request.POST.get('input_text3', '')  # City, State
        user_input4 = request.POST.get('input_text4', '')  # Purchase Value
        
        # Get numerical inputs
        try:
            purchase_value_reduction = Decimal(request.POST.get('purchase_value_reduction', '0'))
            
            # Handle down payment to preserve exact format
            down_payment_str = request.POST.get('down_payment', '0')
            down_payment = Decimal(down_payment_str)
            # Store whether original had decimal points
            has_decimal = '.' in down_payment_str
            
            loan_period = int(request.POST.get('loan_period', '0'))
            annual_interest = Decimal(request.POST.get('annual_interest', '0'))
            monthly_principal_reduction = Decimal(request.POST.get('monthly_principal_reduction', '0'))
            total_interest_reduction = Decimal(request.POST.get('total_interest_reduction', '0'))
        except (ValueError, TypeError, InvalidOperation) as e:
            messages.error(request, f"Invalid numerical input: {str(e)}")
            return redirect('home2')

        # Process texts
        processed_text1 = user_input1.strip().upper().replace(' ', '   ')
        processed_text2 = user_input2.strip().upper().replace(' ', '   ')
        processed_text3 = format_location(user_input3)
        processed_text_guarantor_ref = request.POST.get('input_text_guarantor_ref', '').strip().upper().replace(' ', '   ')

        try:
            # Get next serial number
            serial_number = ProcessedData2.get_next_serial_number(image_number)

            # 1. Purchase Value Calculations
            original_amount = convert_alphanumeric_to_decimal(user_input4)

            # Calculate Reduced Value
            raw_reduced = original_amount * (purchase_value_reduction / Decimal('100'))
            reduced_value = truncate_two_decimals(raw_reduced)
            
            # Calculate Purchase Value for Excel
            pv_enter_excel = truncate_two_decimals(original_amount - reduced_value)

            # 2. Loan Amount Calculations
            raw_dp_value = pv_enter_excel * (down_payment / Decimal('100'))
            dp_value = truncate_two_decimals(raw_dp_value)
            loan_amount = truncate_two_decimals(pv_enter_excel - dp_value)

            # Store the down payment value in its original format for display
            down_payment_display = f"{down_payment:.2f}" if has_decimal else f"{int(down_payment)}"

            # 3. Principal Calculations
            raw_annual_principal = loan_amount / Decimal(loan_period)
            annual_principal = truncate_two_decimals(raw_annual_principal)
            monthly_principal = truncate_two_decimals(annual_principal / Decimal('12'))
            final_principal = truncate_two_decimals(monthly_principal * (monthly_principal_reduction / Decimal('100')))

            # 4. Interest Calculations
            # Calculate Interest per annum
            interest_per_annum = loan_amount * (annual_interest / Decimal('100'))
            interest_per_annum = truncate_two_decimals(interest_per_annum)
            
            # Calculate Total Interest for loan period
            total_interest_for_period = interest_per_annum * Decimal(loan_period)
            total_interest_for_period = truncate_two_decimals(total_interest_for_period)
            
            # Step 3: Apply Total Interest Reduction
            total_interest_for_period = total_interest_for_period * (total_interest_reduction / Decimal('100'))
            total_interest_for_period = truncate_two_decimals(total_interest_for_period)

            # 5. Insurance Calculations
            loan_percentage = Decimal('100') - down_payment

            # Calculate Property Insurance Rate based on loan percentage and period
            if loan_percentage <= Decimal('84.99'):
                property_insurance_rate = Decimal('0.32')
            elif loan_percentage == Decimal('85'):
                property_insurance_rate = Decimal('0.21') if loan_period <= 25 else Decimal('0.32')
            elif Decimal('85.01') <= loan_percentage <= Decimal('90'):
                property_insurance_rate = Decimal('0.41') if loan_period <= 25 else Decimal('0.52')
            elif Decimal('90.01') <= loan_percentage <= Decimal('95'):
                property_insurance_rate = Decimal('0.67') if loan_period <= 25 else Decimal('0.78')
            else:  # 95.01 to 100
                property_insurance_rate = Decimal('0.85') if loan_period <= 25 else Decimal('0.96')

            # Calculate Property Insurance
            raw_property_insurance_per_annum = loan_amount * (property_insurance_rate / Decimal('100'))
            property_insurance_per_annum = truncate_two_decimals(raw_property_insurance_per_annum)
            property_insurance_per_month = truncate_two_decimals(property_insurance_per_annum / Decimal('12'))

            # Calculate PMI Rate based on loan percentage and period
            pmi_per_annum = None  # Default to None (will be displayed as "NA")
            if loan_percentage > Decimal('80'):  # Only calculate PMI if loan percentage is greater than 80%
                if Decimal('80.01') <= loan_percentage <= Decimal('85'):
                    pmi_rate = Decimal('0.19') if loan_period <= 20 else Decimal('0.32')
            elif Decimal('85.01') <= loan_percentage <= Decimal('90'):
                pmi_rate = Decimal('0.23') if loan_period <= 20 else Decimal('0.52')

            # Property Tax Calculations
            try:
                assessment_reduction_rate = request.POST.get('assessment_reduction_rate', '').strip()
                
                # Skip property tax calculation if field is empty or NA
                if not assessment_reduction_rate or assessment_reduction_rate.upper() == 'NA':
                    property_tax_per_annum = None
                    property_tax_for_period = None
                else:
                    # Convert to Decimal only if it's a valid number
                    assessment_reduction_rate = Decimal(assessment_reduction_rate)
                    
                    # Calculate Reduced Value
                    raw_reduced_value = loan_amount * (assessment_reduction_rate / Decimal('100'))
                    reduced_value = truncate_two_decimals(raw_reduced_value)
                    
                    # Calculate Property Tax per annum (2% fixed rate)
                    raw_property_tax_per_annum = reduced_value * Decimal('0.02')
                    property_tax_per_annum = truncate_two_decimals(raw_property_tax_per_annum)
                    
                    # Calculate Property Tax for loan period
                    raw_property_tax_for_period = property_tax_per_annum * Decimal(loan_period)
                    property_tax_for_period = truncate_two_decimals(raw_property_tax_for_period)
            except (ValueError, TypeError, InvalidOperation) as e:
                messages.error(request, f"Invalid property tax calculation: {str(e)}")
                return redirect('home2')

            # Create and save the processed data
            processed_data = ProcessedData2(
                image_number=image_number,
                serial_number=serial_number,
                username=username,
                customer_reference_number=processed_text_ref,
                customer_name=processed_text1,
                city_state=processed_text3,
                purchase_value_excel=pv_enter_excel,
                down_payment_percent=down_payment_display,
                loan_period_years=loan_period,
                annual_interest_rate=annual_interest,
                guarantor_name=processed_text2,
                guarantor_reference_number=processed_text_guarantor_ref,
                loan_amount=loan_amount,
                final_principal=final_principal,
                total_interest_for_period=total_interest_for_period,
                property_insurance_per_month=property_insurance_per_month,
                pmi_per_annum=pmi_per_annum,
                assessment_reduction_rate=assessment_reduction_rate,
                property_tax_per_annum=property_tax_per_annum,
                property_tax_for_period=property_tax_for_period
            )

            # Save the processed data
            processed_data.save()
            
            # Prepare context for results page
            context = {
                'image_number': processed_data.image_number,
                'serial_number': processed_data.serial_number,
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

def results(request):
    # Get processed data from session
    processed_data = request.session.get('processed_data', None)
    if not processed_data:
        messages.error(request, "No processed data found!")
        return redirect('home')
    
    # Clear the session data after retrieving it
    del request.session['processed_data']
    
    return render(request, 'app/results.html', processed_data)


