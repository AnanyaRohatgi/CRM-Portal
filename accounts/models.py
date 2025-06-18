from django.db import models
import uuid

class DownloadRequest(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    requested_by = models.EmailField()
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class UserRegion(models.Model):
    """
    Stores which regions each account owner can access
    """
    account_owner_name = models.CharField(max_length=100, unique=True)
    account_owner_alias = models.CharField(max_length=50)
    regions = models.CharField(max_length=100)  # Comma-separated values like "India,Singapore"
    
    def get_region_list(self):
        return [r.strip().lower() for r in self.regions.split(',')]
    
    def __str__(self):
        return f"{self.account_owner_name} - {self.regions}"
    
    class Meta:
        db_table = 'user_regions'

class Account(models.Model):
    contact_id = models.AutoField(primary_key=True)
    salutation = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    mailing_street = models.TextField(blank=True, null=True)
    account_id = models.CharField(max_length=18, blank=True, null=True)
    mailing_city = models.TextField(blank=True, null=True)
    mailing_state = models.TextField(blank=True, null=True)
    mailing_zip = models.TextField(blank=True, null=True)
    mailing_country = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    account_phone = models.TextField(blank=True, null=True)
    mobile = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    account_owner = models.CharField(max_length=100, blank=True, null=True)
    account_owner_alias = models.CharField(max_length=50, blank=True, null=True)
    salesperson_sf_id = models.CharField(max_length=18, blank=True, null=True)
    account_created_date = models.DateField(blank=True, null=True)
    account_name = models.TextField(blank=True, null=True)
    region = models.CharField(max_length=20)  # not null, so required
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['email']),
            models.Index(fields=['account_id']),
            models.Index(fields=['phone', 'mobile']),
            models.Index(fields=['region']),  # Added for performance
        ]
