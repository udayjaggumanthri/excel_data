import re
from django.shortcuts import render
from decimal import Decimal, ROUND_DOWN, getcontext

# Decimal precision setup
getcontext().prec = 30

# Mappings
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
    return total + current

def parse_number(text):
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
    s = s.strip()
    if s.startswith('$'):
        s = s[1:].strip()
    m = re.match(
        r"^(.*)\s+dollars\s+and\s+(.*)\s+cents$",
        s,
        flags=re.IGNORECASE
    )
    if not m:
        raise ValueError("Input must be of the form '<…> dollars and <…> cents'")
    dollars_text = m.group(1).strip()
    cents_text = m.group(2).strip()
    dollars = parse_number(dollars_text)
    cents = parse_number(cents_text)
    return Decimal(dollars) + (Decimal(cents) / Decimal(100))

def truncate_two_decimals(d: Decimal) -> Decimal:
    return d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def format_with_commas(d: Decimal) -> str:
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
    processed_text4 = ''
    if request.method == 'POST':
        user_input1 = request.POST.get('input_text1', '')
        user_input2 = request.POST.get('input_text2', '')
        user_input3 = request.POST.get('input_text3', '')
        user_input4 = request.POST.get('input_text4', '')
        
        # Process texts as per requirements
        processed_text1 = user_input1.strip().upper().replace(' ', '   ')
        processed_text2 = user_input2.strip().upper().replace(' ', '   ')
        processed_text3 = format_location(user_input3)
        try:
            original_amount = convert_alphanumeric_to_decimal(user_input4)
            reduction_input = request.POST.get('input_text5', '').strip() # Assuming a new input field for reduction percentage

            if not reduction_input:
                raise ValueError("Down Payment % cannot be empty.")

            down_payment_percentage = Decimal(reduction_input) / Decimal(100)
            down_payment_value = truncate_two_decimals(original_amount * down_payment_percentage)
            loan_amount = truncate_two_decimals(original_amount - down_payment_value)

            processed_text4 = {
                'original_amount': format_with_commas(original_amount),
                'down_payment_value': format_with_commas(down_payment_value),
                'loan_amount': format_with_commas(loan_amount)
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
