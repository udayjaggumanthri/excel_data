from django.db import models
from django.utils import timezone
from decimal import Decimal

class ProcessedData2(models.Model):
    # 1. Image Information
    image_number = models.CharField(max_length=50)
    serial_number = models.IntegerField()
    username = models.CharField(max_length=100, default='')  # New username field
    
    # 2. Customer Reference Number
    customer_reference_number = models.CharField(max_length=255, null=True, blank=True)
    
    # 3. Customer Information
    customer_name = models.TextField()
    city_state = models.TextField()
    
    # 4. Purchase Value and Down Payment
    purchase_value_excel = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    down_payment_percent = models.CharField(max_length=10, default='0')  # Changed to CharField to store exact format
    
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
    
    # 5. Loan Period and Interest
    loan_period_years = models.IntegerField(default=0)
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    @property
    def loan_period_and_interest(self):
        """Format loan period and interest rate as per requirement"""
        return f"{self.loan_period_years} YEARS AND {self.annual_interest_rate} %"
    
    # 6. Guarantor Information
    guarantor_name = models.TextField(default='')
    guarantor_reference_number = models.TextField(null=True, blank=True)
    
    # 7. Loan and Principal
    loan_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    final_principal = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    
    # 8. Total Interest
    total_interest_for_period = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    
    # 9. Insurance Information
    property_insurance_per_month = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    pmi_per_annum = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # 10. Property Tax Information
    assessment_reduction_rate = models.CharField(max_length=10, null=True, blank=True)  # Changed to CharField to handle 'NA'
    property_tax_per_annum = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    property_tax_for_period = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    @property
    def formatted_property_tax(self):
        """Format property tax for loan period with proper currency formatting"""
        if not self.assessment_reduction_rate or self.assessment_reduction_rate.upper() == 'NA':
            return "NA"
        return self.format_number_with_commas(self.property_tax_for_period)
    
    # Metadata
    entry_timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['image_number', 'serial_number', '-entry_timestamp']
        unique_together = ['image_number', 'serial_number']

    def __str__(self):
        return f"Image {self.image_number} - Serial {self.serial_number} - {self.customer_name}"

    @classmethod
    def get_next_serial_number(cls, image_number):
        """Get the next available serial number for a given image number"""
        latest = cls.objects.filter(image_number=image_number).order_by('-serial_number').first()
        return (latest.serial_number + 1) if latest else 1

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

    def save(self, *args, **kwargs):
        # Get down payment value
        down_payment_value = Decimal(self.down_payment_percent)
        
        # Calculate loan amount
        self.loan_amount = self.purchase_value_excel * (Decimal('100') - down_payment_value) / Decimal('100')
        
        # Calculate principal amounts
        raw_annual_principal = self.loan_amount / Decimal(self.loan_period_years)
        self.annual_principal = raw_annual_principal
        self.monthly_principal = self.annual_principal / Decimal('12')
        
        # Calculate final principal based on monthly principal reduction
        self.final_principal = self.monthly_principal
        
        # Calculate interest amounts
        raw_interest_per_annum = self.loan_amount * (self.annual_interest_rate / Decimal('100'))
        self.interest_per_annum = raw_interest_per_annum
        raw_total_interest = self.interest_per_annum * Decimal(self.loan_period_years)
        self.total_interest_for_period = raw_total_interest
        
        # Calculate property insurance and PMI
        property_insurance_rate = self.calculate_property_insurance_rate()
        self.property_insurance_per_month = (property_insurance_rate / Decimal('100')) * self.purchase_value_excel / Decimal('12')
        
        # Calculate PMI if applicable
        pmi_rate = self.calculate_pmi_rate()
        if pmi_rate is not None:
            self.pmi_per_annum = (pmi_rate / Decimal('100')) * self.purchase_value_excel
        else:
            self.pmi_per_annum = None
        
        super().save(*args, **kwargs)
