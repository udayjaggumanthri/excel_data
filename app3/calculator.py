from decimal import Decimal, ROUND_DOWN
import re

class LoanCalculator:
    def __init__(self):
        self.image_number = ''
        self.serial_number = 0
        self.username = ''
        self.customer_reference_number = ''
        self.customer_name = ''
        self.city_state = ''
        self.guarantor_name = ''
        self.guarantor_reference_number = ''
        self.purchase_value_excel = Decimal('0.00')
        self.down_payment_percent = '0'
        self.loan_period_years = 0
        self.annual_interest_rate = Decimal('0.00')
        self.property_insurance_per_month = Decimal('0.00')
        self.loan_amount = Decimal('0.00')
        self.final_principal = Decimal('0.00')
        self.total_interest_for_period = Decimal('0.00')
        self.pmi_per_annum = None

    def format_number_with_commas(self, value):
        """Format a number according to the specified rules"""
        if value is None:
            return "NA"
            
        # Convert to string and split into whole and decimal parts
        value_str = f"{value:.2f}"
        whole, decimal = value_str.split('.')
        
        # Handle different lengths
        length = len(whole)
        formatted = ""
        
        if length <= 3:  # 123.45
            formatted = f"$  {whole}.{decimal}"
        else:
            # Reverse the string to process from right to left
            whole = whole[::-1]
            groups = []
            
            # Group by 3 digits from right to left
            for i in range(0, len(whole), 3):
                group = whole[i:i+3][::-1]  # Reverse back each group
                groups.append(group)
            
            # Reverse the groups to get them in correct order
            groups = groups[::-1]
            
            # Join with proper spacing
            formatted = "$  " + "  ,  ".join(groups) + f".{decimal}"
        
        return formatted

    def format_purchase_value(self):
        """Format purchase value according to the specified rules"""
        return self.format_number_with_commas(self.purchase_value_excel)

    @property
    def purchase_value_and_down_payment(self):
        """Combine formatted purchase value and down payment"""
        formatted_purchase = self.format_purchase_value()
        return f"{formatted_purchase} AND {self.down_payment_percent} %"

    @property
    def loan_amount_and_principal(self):
        """Combine formatted loan amount and principal"""
        formatted_loan = self.format_number_with_commas(self.loan_amount)
        formatted_principal = self.format_number_with_commas(self.final_principal)
        return f"{formatted_loan} AND {formatted_principal}"

    @property
    def insurance_and_pmi(self):
        """Combine formatted property insurance and PMI"""
        formatted_insurance = self.format_number_with_commas(self.property_insurance_per_month)
        
        # Calculate if PMI is applicable - convert down_payment_percent to Decimal first
        try:
            down_payment_value = Decimal(self.down_payment_percent)
            loan_percent = Decimal('100') - down_payment_value
            if loan_percent <= 80:
                formatted_pmi = "NA"
            else:
                formatted_pmi = self.format_number_with_commas(self.pmi_per_annum)
        except:
            # If there's any error converting the down payment, default to NA
            formatted_pmi = "NA"
            
        return f"{formatted_insurance} AND {formatted_pmi}"

    @property
    def loan_period_and_interest(self):
        """Format loan period and interest rate as per requirement"""
        return f"{self.loan_period_years} YEARS AND {self.annual_interest_rate} %"

    def calculate_property_insurance_rate(self):
        """Calculate property insurance rate based on loan percentage and period"""
        try:
            down_payment_value = Decimal(self.down_payment_percent)
            loan_percent = 100 - down_payment_value
            period = self.loan_period_years

            if loan_percent <= Decimal('84.99'):
                return Decimal('0.32')
            elif loan_percent == Decimal('85'):
                return Decimal('0.21') if period <= 25 else Decimal('0.32')
            elif Decimal('85.01') <= loan_percent <= Decimal('90'):
                return Decimal('0.41') if period <= 25 else Decimal('0.52')
            elif Decimal('90.01') <= loan_percent <= Decimal('95'):
                return Decimal('0.67') if period <= 25 else Decimal('0.78')
            else:  # 95.01 to 100
                return Decimal('0.85') if period <= 25 else Decimal('0.96')
        except:
            return Decimal('0.32')  # Default to minimum rate if there's any error

    def calculate_pmi_rate(self):
        """Calculate PMI rate based on loan percentage and period"""
        try:
            down_payment_value = Decimal(self.down_payment_percent)
            loan_percent = 100 - down_payment_value
            period = self.loan_period_years

            if loan_percent <= 80:
                return None  # Always return None (will be displayed as "NA") for loan percentage <= 80%
            elif 80.01 <= loan_percent <= 85:
                return Decimal('0.19') if period <= 20 else Decimal('0.32')
            elif 85.01 <= loan_percent <= 90:
                return Decimal('0.23') if period <= 20 else Decimal('0.52')
            elif 90.01 <= loan_percent <= 95:
                return Decimal('0.26') if period <= 20 else Decimal('0.78')
            else:  # 95.01 to 100
                return Decimal('0.79') if period <= 20 else Decimal('0.90')
        except:
            return None  # Return None if there's any error converting the down payment

    def calculate(self, data):
        """Calculate all values based on input data"""
        # Set basic information
        self.image_number = data.get('image_number', '')
        self.username = data.get('username', '').strip()
        
        # Process text fields with proper formatting
        self.customer_reference_number = data.get('input_text_ref', '').strip().upper().replace(' ', '   ')
        self.customer_name = data.get('input_text1', '').strip().upper().replace(' ', '   ')
        self.guarantor_name = data.get('input_text2', '').strip().upper().replace(' ', '   ')
        
        # Process city_state with proper comma formatting
        city_state = data.get('input_text3', '').strip().upper()
        if ',' in city_state:
            left, right = city_state.split(',', 1)
            self.city_state = f"{left.strip()} , {right.strip()}"
        else:
            self.city_state = "Invalid format: no comma found"
            
        self.guarantor_reference_number = data.get('input_text_guarantor_ref', '').strip().upper().replace(' ', '   ')
        
        # Get and process numerical inputs
        purchase_value_reduction = Decimal(data.get('purchase_value_reduction', '0'))
        down_payment = Decimal(data.get('down_payment', '0'))
        self.down_payment_percent = f"{down_payment:.2f}" if '.' in str(down_payment) else str(int(down_payment))
        self.loan_period_years = int(data.get('loan_period', '0'))
        self.annual_interest_rate = Decimal(data.get('annual_interest', '0'))
        monthly_principal_reduction = Decimal(data.get('monthly_principal_reduction', '0'))
        total_interest_reduction = Decimal(data.get('total_interest_reduction', '0'))

        # Convert purchase value from text
        purchase_value_text = data.get('input_text4', '')
        original_amount = self.convert_text_to_decimal(purchase_value_text)

        # Calculate reduced value and purchase value for excel
        reduced_value = original_amount * (purchase_value_reduction / Decimal('100'))
        self.purchase_value_excel = original_amount - reduced_value

        # Calculate loan amount
        down_payment_value = self.purchase_value_excel * (Decimal(self.down_payment_percent) / Decimal('100'))
        self.loan_amount = self.purchase_value_excel - down_payment_value

        # Calculate principal amounts
        annual_principal = self.loan_amount / self.loan_period_years
        monthly_principal = annual_principal / Decimal('12')
        self.final_principal = monthly_principal * (monthly_principal_reduction / Decimal('100'))

        # Calculate interest amounts
        # Step 1: Calculate Interest per annum
        interest_per_annum = self.loan_amount * (self.annual_interest_rate / Decimal('100'))
        interest_per_annum = truncate_two_decimals(interest_per_annum)
        
        # Step 2: Calculate Total Interest for loan period
        total_interest_for_period = interest_per_annum * Decimal(self.loan_period_years)
        total_interest_for_period = truncate_two_decimals(total_interest_for_period)
        
        # Step 3: Apply Total Interest Reduction
        total_interest_for_period = total_interest_for_period * (total_interest_reduction / Decimal('100'))
        self.total_interest_for_period = truncate_two_decimals(total_interest_for_period)

        # Calculate property insurance and PMI
        property_insurance_rate = self.calculate_property_insurance_rate()
        self.property_insurance_per_month = (property_insurance_rate / Decimal('100')) * self.purchase_value_excel / Decimal('12')

        # Calculate PMI if applicable
        pmi_rate = self.calculate_pmi_rate()
        if pmi_rate is not None:
            self.pmi_per_annum = (pmi_rate / Decimal('100')) * self.purchase_value_excel
        else:
            self.pmi_per_annum = None

    def convert_text_to_decimal(self, text):
        """Convert text amount to Decimal"""
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
            "hundred": 10**2,
            "thousand": 10**3,
            "million": 10**6,
            "billion": 10**9,
            "trillion": 10**12
        }

        text = text.strip()
        if text.startswith('$'):
            text = text[1:].strip()

        match = re.match(r"^(.*)\s+dollars\s+and\s+(.*)\s+cents$", text, flags=re.IGNORECASE)
        if not match:
            raise ValueError("Input must be of the form '<…> dollars and <…> cents'.")

        dollars_text = match.group(1).strip()
        cents_text = match.group(2).strip()

        def parse_number(text):
            words = re.findall(r"[A-Za-z]+", text.lower())
            total = 0
            current = 0
            
            for word in words:
                if word in ONES:
                    current += ONES[word]
                elif word in TENS:
                    current += TENS[word]
                elif word in SCALES:
                    if word == "hundred":
                        current *= SCALES[word]
                    else:
                        current = (current or 1) * SCALES[word]
                        total += current
                        current = 0
            
            total += current
            return total

        dollars = parse_number(dollars_text)
        cents = parse_number(cents_text)
        
        return Decimal(dollars) + (Decimal(cents) / Decimal(100)) 