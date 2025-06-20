from django.db import models

# Create your models here.

class CustomerData(models.Model):
    emp_id = models.CharField(max_length=50, verbose_name="Emp ID")
    image_number = models.CharField(max_length=100, verbose_name="Image Number*")
    serial_number = models.CharField(max_length=50, verbose_name="Serial Number")
    customer_reference_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Customer Reference Number"
    )
    customer_name = models.CharField(max_length=200, verbose_name="Customer Name")
    city_state = models.CharField(max_length=200, verbose_name="City, State")
    purchase_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Purchase Value"
    )
    purchase_value_reduction_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Purchase Value Reduction %"
    )
    down_payment_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Down Payment %"
    )
    loan_period_years = models.IntegerField(verbose_name="Loan Period (Years)")
    annual_interest_rate_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Annual Interest Rate %"
    )
    monthly_principal_reduction_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Monthly Principal Reduction %"
    )
    total_interest_reduction_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Total Interest Reduction %"
    )
    guarantor_name = models.CharField(max_length=200, verbose_name="Guarantor Name")
    guarantor_reference_number = models.CharField(
        max_length=100, 
        verbose_name="Guarantor Reference Number"
    )
    assessment_reduction_rate_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Assessment Reduction Rate %"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Data"
        verbose_name_plural = "Customer Data"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.customer_reference_number}"
