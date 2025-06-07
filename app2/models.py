from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import locale

class ProcessedData2(models.Model):
    image_number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    customer_reference_number = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=200)
    city_state = models.CharField(max_length=200)
    guarantor_name = models.CharField(max_length=200)
    guarantor_reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial fields
    purchase_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)])
    down_payment_percent = models.CharField(max_length=10)
    loan_period_years = models.IntegerField(validators=[MinValueValidator(1)])
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    property_insurance_per_month = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Calculated fields
    reduced_value = models.DecimalField(max_digits=20, decimal_places=2)
    down_payment_value = models.DecimalField(max_digits=20, decimal_places=2)
    loan_amount = models.DecimalField(max_digits=20, decimal_places=2)
    annual_principal = models.DecimalField(max_digits=20, decimal_places=2)
    monthly_principal = models.DecimalField(max_digits=20, decimal_places=2)
    final_principal = models.DecimalField(max_digits=20, decimal_places=2)
    interest_per_annum = models.DecimalField(max_digits=20, decimal_places=2)
    total_interest_for_period = models.DecimalField(max_digits=20, decimal_places=2)
    final_total_interest = models.DecimalField(max_digits=20, decimal_places=2)
    pmi_per_annum = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Metadata
    entry_timestamp = models.DateTimeField(auto_now_add=True)
    
    def format_number_with_commas(self, number):
        try:
            locale.setlocale(locale.LC_ALL, '')
            return locale.format_string("%.2f", float(number), grouping=True)
        except:
            return str(number)
    
    def format_purchase_value(self):
        return self.format_number_with_commas(self.purchase_value)
    
    def calculate_pmi(self):
        loan_percentage = (self.loan_amount / self.purchase_value) * 100
        if loan_percentage > 80:
            return Decimal('0.01') * self.purchase_value  # 1% of purchase value
        return None
    
    def save(self, *args, **kwargs):
        # Calculate reduced value (5% less than purchase value)
        self.reduced_value = self.purchase_value * Decimal('0.95')
        
        # Calculate down payment value
        down_payment_decimal = Decimal(self.down_payment_percent.strip(' %'))
        self.down_payment_value = (down_payment_decimal / 100) * self.purchase_value
        
        # Calculate loan amount
        self.loan_amount = self.purchase_value - self.down_payment_value
        
        # Calculate principal amounts
        self.annual_principal = self.loan_amount / self.loan_period_years
        self.monthly_principal = self.annual_principal / 12
        self.final_principal = self.loan_amount
        
        # Calculate interest amounts
        self.interest_per_annum = (self.annual_interest_rate / 100) * self.loan_amount
        self.total_interest_for_period = self.interest_per_annum * self.loan_period_years
        self.final_total_interest = self.total_interest_for_period
        
        # Calculate PMI if applicable
        pmi = self.calculate_pmi()
        self.pmi_per_annum = pmi if pmi is not None else None
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_name} - {self.serial_number}"
    
    class Meta:
        verbose_name = "Processed Data 2"
        verbose_name_plural = "Processed Data 2"
