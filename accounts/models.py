import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DownloadRequest(models.Model):
    """
    Tracks CSV download requests that require admin approval
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    data_type = models.CharField(max_length=50, default='contacts', blank=True, null=True)
    page_context = models.CharField(max_length=100, blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    requested_by = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    filter_parameters = models.JSONField(null=True, blank=True)  # Stores the filters used for the request
    requested_by_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Download request by {self.requested_by} - {self.status}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Download Request'
        verbose_name_plural = 'Download Requests'

class UserRegion(models.Model):
    """
    Stores which regions each account owner can access
    """
    account_owner_name = models.CharField(max_length=100, unique=True)
    account_owner_alias = models.CharField(max_length=50)
    regions = models.CharField(max_length=100)  # Comma-separated values like "India,Singapore"
    
    is_super_admin = models.BooleanField(default=False)
    
    def get_region_list(self):
        return [r.strip().lower() for r in self.regions.split(',')]
    
    def __str__(self):
        return f"{self.account_owner_name} - {self.regions}"
    
    class Meta:
        db_table = 'user_regions'
        verbose_name = 'User Region'
        verbose_name_plural = 'User Regions'

class Account(models.Model):
    id = models.AutoField(primary_key=True)

    account_id = models.CharField(max_length=58, db_column='Account_Id', blank=True, null=True)
    account_name = models.TextField(db_column='Account_Name', blank=True, null=True, verbose_name="Account Name")
    first_name = models.CharField(max_length=50, db_column='FirstName', blank=True, null=True)
    last_name = models.CharField(max_length=50, db_column='LastName', blank=True, null=True)
    full_name = models.CharField(max_length=200, db_column='FullName', blank=True, null=True, verbose_name="Full Name")
    title = models.TextField(db_column='Title', blank=True, null=True, verbose_name="Title")
    organization_level = models.CharField(max_length=100, db_column='OrganizationLevel', blank=True, null=True, verbose_name="Organisational Level")
    department = models.CharField(max_length=100, db_column='Department', blank=True, null=True, verbose_name="Department")
    email = models.CharField(max_length=200, db_column='Email', blank=True, null=True, verbose_name="Email ID")
    mobile = models.TextField(db_column='MobilePhone', blank=True, null=True, verbose_name="Mobile Phone")
    other_phone = models.TextField(db_column='OtherPhone', blank=True, null=True, verbose_name="Alternate Phone")
    industry = models.CharField(max_length=100, db_column='Industry', blank=True, null=True, verbose_name="Industry")
    city = models.CharField(max_length=100, db_column='City', blank=True, null=True, verbose_name="City")
    state = models.CharField(max_length=100, db_column='State', blank=True, null=True, verbose_name="State")
    country = models.CharField(max_length=100, db_column='Country', blank=True, null=True, verbose_name="Country")
    region = models.CharField(max_length=20, db_column='REGION', verbose_name="Region")
    zone = models.CharField(max_length=50, db_column='Zone', blank=True, null=True, verbose_name="Zone")
    account_owner = models.CharField(max_length=100, db_column='Account Owner', blank=True, null=True, verbose_name="Account Owner")
    contact_id = models.CharField(max_length=50, db_column='Contact_Id', blank=True, null=True)
    account_phone = models.TextField(db_column='AccountPhone', blank=True, null=True)
    phone = models.TextField(db_column='Phone', blank=True, null=True)
    contacts_city = models.CharField(max_length=100, db_column='Contacts_City', blank=True, null=True, verbose_name="Contacts City")
    contacts_state = models.CharField(max_length=100, db_column='Contacts_State', blank=True, null=True, verbose_name="Contacts State")
    contacts_country = models.CharField(max_length=100, db_column='Contacts_Country', blank=True, null=True, verbose_name="Contacts Country")
    remarks = models.TextField(db_column='Remarks', blank=True, null=True, verbose_name="Remarks")

    created_by_user = models.ForeignKey(
    User,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='account_created_by',
    verbose_name="Created By"
)

    created_date = models.DateField(db_column='CreatedDate', blank=True, null=True, verbose_name="Created Date Timestamp")
    timestamp = models.DateTimeField(db_column='timestamp', auto_now_add=True)

    # Track last modification
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Last Modified Timestamp")
    last_modified_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='account_last_modified', verbose_name="Last Modified by Name"
    )

    class Meta:
        db_table = 'accounts'
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['email']),
            models.Index(fields=['account_id']),
            models.Index(fields=['phone', 'mobile']),
            models.Index(fields=['region']),
            models.Index(fields=['account_name']),
        ]
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return f"{self.account_name} ({self.region})" if self.account_name else f"Unnamed Account ({self.region})"


class AccountRecord(models.Model):
    account_id = models.CharField(max_length=98, db_column='Account_Id', blank=True, null=True)
    account_name = models.CharField(max_length=400, db_column='Account_Name', verbose_name="Account Name")
    city = models.CharField(max_length=100, db_column='City', blank=True, null=True, verbose_name="City")
    state = models.CharField(max_length=100, db_column='State', blank=True, null=True, verbose_name="State")
    country = models.CharField(max_length=100, db_column='Country', blank=True, null=True, verbose_name="Country")
    industry = models.CharField(max_length=100, db_column='Industry', verbose_name="Industry")
    description = models.TextField(db_column='Description', blank=True, null=True, verbose_name="Description")
    zone = models.CharField(max_length=50, db_column='Zone', blank=True, null=True, verbose_name="Zone")
    region = models.CharField(max_length=100, db_column='REGION', blank=True, null=True, verbose_name="Region")
    account_owner = models.CharField(max_length=100, db_column='Account Owner', blank=True, null=True, verbose_name="Account Owner")

    created_by = models.ForeignKey(
    User,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='account_record_created_by',
    db_column='CreatedById',
    verbose_name="Created By"
)

    
    created_date = models.DateField(
        db_column='CreatedDate',
        blank=True,
        null=True,
        verbose_name="Created Date Timestamp"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_column='timestamp')

    linked_account = models.ForeignKey(
        'Account', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='records'
    )

    last_modified = models.DateTimeField(auto_now=True, verbose_name="Last Modified Timestamp")
    last_modified_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='account_record_last_modified',
        verbose_name="Last Modified by Name"
    )

    class Meta:
        db_table = 'account_records'
        indexes = [
            models.Index(fields=['account_id']),
            models.Index(fields=['account_name']),
            models.Index(fields=['industry']),
            models.Index(fields=['country']),
            models.Index(fields=['created_date']),
            models.Index(fields=['account_name', 'created_date']),
            models.Index(fields=['region']),
            models.Index(fields=['account_owner']),
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['last_modified']),
        ]
        verbose_name = 'Account Record'
        verbose_name_plural = 'Account Records'
        ordering = ['-created_date']

    def save(self, *args, **kwargs):
        if self.pk:
            # It's an update — preserve the original creator
            original = AccountRecord.objects.get(pk=self.pk)
            self.created_by = original.created_by
        else:
            # It's a new object — created_by must be set explicitly from view
            if not self.created_by:
                raise ValueError("created_by must be set for new AccountRecord")

            if not self.created_date:
                self.created_date = timezone.now().date()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.account_name or "Unnamed Account"
