import re
from django.shortcuts import render
from decimal import Decimal, ROUND_DOWN, getcontext

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

def home(request):
    processed_text1 = ''
    processed_text2 = ''
    processed_text3 = ''
    processed_text4 = {}
    if request.method == 'POST':
        user_input1 = request.POST.get('input_text1', '')
        user_input2 = request.POST.get('input_text2', '')
        user_input3 = request.POST.get('input_text3', '')
        user_input4 = request.POST.get('input_text4', '') # Alphanumeric Purchase Value
        user_input5 = request.POST.get('input_text5', '') # Purchase Value Reduction %
        user_input6 = request.POST.get('input_text6', '') # Down Payment %
        user_input7 = request.POST.get('input_text7', '') # Loan Period (years)
        user_input8 = request.POST.get('input_text8', '') # Monthly Principal Reduction %

        # Process texts as per requirements
        processed_text1 = user_input1.strip().upper().replace(' ', '   ')
        processed_text2 = user_input2.strip().upper().replace(' ', '   ')
        processed_text3 = format_location(user_input3)

        try:
            # 1) Convert spelled-out to Decimal
            original_amount = convert_alphanumeric_to_decimal(user_input4)

            # 2) Compute Reduced Purchase Value
            if not user_input5:
                raise ValueError("Purchase Value Reduction % cannot be empty.")
            pv_reduction_frac = Decimal(user_input5) / Decimal(100)
            raw_reduced = original_amount * pv_reduction_frac
            reduced_value = truncate_two_decimals(raw_reduced)
            pv_enter_excel = truncate_two_decimals(original_amount - reduced_value)

            # 3) Down Payment & Loan Amount
            if not user_input6:
                raise ValueError("Down Payment % cannot be empty.")
            dp_frac = Decimal(user_input6) / Decimal(100)
            raw_dp_value = pv_enter_excel * dp_frac
            dp_value = truncate_two_decimals(raw_dp_value)
            loan_amount = truncate_two_decimals(pv_enter_excel - dp_value)

            # 4) Loan Period & Monthly Principal Reduction
            if not user_input7:
                raise ValueError("Loan Period cannot be empty.")
            loan_period_years = int(user_input7)
            if loan_period_years <= 0:
                raise ValueError("Loan Period must be a positive integer.")

            if not user_input8:
                raise ValueError("Monthly Principal Reduction % cannot be empty.")
            mpr_frac = Decimal(user_input8) / Decimal(100)

            # 5) Compute Annual Principal (truncated), Monthly Principal (truncated), and Final Principal
            raw_annual_principal = loan_amount / Decimal(loan_period_years)
            annual_principal = truncate_two_decimals(raw_annual_principal)
            monthly_principal = truncate_two_decimals(annual_principal / Decimal(12))
            final_principal = truncate_two_decimals(monthly_principal * mpr_frac)

            processed_text4 = {
                'original_amount': format_with_commas(original_amount),
                'pv_reduction_input': user_input5,
                'reduced_value': format_with_commas(reduced_value),
                'pv_enter_excel': format_with_commas(pv_enter_excel),
                'down_payment_input': user_input6,
                'dp_value': format_with_commas(dp_value),
                'loan_amount': format_with_commas(loan_amount),
                'loan_period_input': user_input7,
                'mpr_input': user_input8,
                'annual_principal': format_with_commas(annual_principal),
                'monthly_principal': format_with_commas(monthly_principal),
                'final_principal': format_with_commas(final_principal)
            }
        except ValueError as e:
            processed_text4 = f"Error: {e}"
        except Exception as e:
            processed_text4 = f"An unexpected error occurred: {e}"
    
    return render(request, 'app/home.html', {
        'processed_text1': processed_text1,
        'processed_text2': processed_text2,
        'processed_text3': processed_text3,
        'processed_text4': processed_text4
    })
