from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import OuterRef, Subquery, Max
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Count, Q, F
from django.db.models.functions import Lower
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from .models import AccountRecord
from .utils import get_user_allowed_regions
from django.db.models import Value
from django.db.models.functions import Concat
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_str
from urllib.parse import unquote
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import csv
import io
from django.http import HttpResponse
import csv
from uuid import UUID
from .models import DownloadRequest, Account  # Make sure to import your models
import logging
import re
from functools import lru_cache
from datetime import datetime
from .models import Account, AccountRecord, DownloadRequest, UserRegion
from .decorators import staff_approved_required
from .utils import get_user_allowed_regions

logger = logging.getLogger(__name__)

def get_user_allowed_regions(user):
    print(f"🔍 GET_REGIONS DEBUG: Processing user: '{user.username}'")
    print(f"🔍 GET_REGIONS DEBUG: User is_staff: {user.is_staff}")

    if user.is_staff:
        all_regions = set()
        for entry in UserRegion.objects.all():
            if entry.regions:
                all_regions.update(r.strip() for r in entry.regions.split(',') if r.strip())
        result = sorted(all_regions)
        print(f"✅ Staff user, all regions: {result}")
        return result

    full_name = f"{user.first_name.strip()} {user.last_name.strip()}".strip().lower()
    username = user.username.strip().lower()

    print(f"🔍 Attempting match by full name: '{full_name}' or alias: '{username}'")

    try:
        matching_region = next(
            (ur for ur in UserRegion.objects.all()
             if ur.account_owner_name.strip().lower() == full_name or
                ur.account_owner_alias.strip().lower() == username),
            None
        )
        if matching_region:
            regions = [r.strip() for r in matching_region.regions.split(',') if r.strip()]
            print(f"✅ Region match found: {regions}")
            return regions
        else:
            print("❌ No UserRegion match found for full name or alias.")
    except Exception as e:
        print(f"❌ Error while fetching UserRegion: {e}")

    return []

def signup_view(request):
    if request.method == 'POST':
        print("📥 POST received for signup")
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        print(f"📝 Signup data received:")
        print(f"   - Username: '{username}'")
        print(f"   - Email: '{email}'")
        print(f"   - First name: '{first_name}'")
        print(f"   - Last name: '{last_name}'")
        print(f"   - Password length: {len(password) if password else 'None'}")

        # Check for existing username
        if User.objects.filter(username=username).exists():
            print(f"❌ Username already exists: '{username}'")
            messages.error(request, 'Username already exists.')
            return redirect('signup')

        # Check for existing email
        if User.objects.filter(email=email).exists():
            print(f"❌ Email already exists: '{email}'")
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        try:
            # Create user
            print(f"🔄 Creating user with create_user()...")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            print(f"✅ User created successfully!")
            print(f"   - User ID: {user.id}")
            print(f"   - Username: '{user.username}'")
            print(f"   - Password hash: {user.password[:20]}...")
            print(f"   - Is active: {user.is_active}")
            
            # Test the password immediately after creation
            from django.contrib.auth.hashers import check_password
            password_test = check_password(password, user.password)
            print(f"🔍 Immediate password test: {password_test}")
            
            # Check if UserRegion exists for this user
            full_name = f"{first_name} {last_name}".strip()
            print(f"🔍 Checking UserRegion for full name: '{full_name}'")
            
            try:
                user_region = UserRegion.objects.get(account_owner_name=full_name)
                print(f"✅ UserRegion found: {user_region.regions}")
            except UserRegion.DoesNotExist:
                print(f"⚠️ No UserRegion found for '{full_name}'")
                print("Available UserRegions:")
                for ur in UserRegion.objects.all()[:5]:  # Show first 5
                    print(f"   - '{ur.account_owner_name}' -> {ur.regions}")
                
            
        except Exception as e:
            print(f"❌ ERROR while creating user: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, 'An error occurred while creating the user.')
            return redirect('signup')

        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')

    return render(request, 'accounts/signup.html')
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from accounts.models import UserRegion

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user exists in UserRegion
            full_name = f"{user.first_name.strip()} {user.last_name.strip()}".strip().lower()
            alias = user.username.strip().lower()

            region_exists = UserRegion.objects.filter(
                account_owner_name__iexact=full_name
            ).exists() or UserRegion.objects.filter(
                account_owner_alias__iexact=alias
            ).exists()

            if not region_exists:
                # Block access if not authorized
                logout(request)
                messages.error(request, "You don’t have access to this application.")
                return redirect('no_access')

            # Allow login
            login(request, user)
            return redirect('setup')

        messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/index.html')

def no_access_view(request):
    return render(request, 'accounts/no_access.html', status=403)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
import csv
import io
from .models import Account, AccountRecord
def setup_view(request):
    account_list = Account.objects.only(
        "id", "first_name", "last_name", "full_name", "title",
        "organization_level", "department", "email", "mobile", "other_phone",
        "account_name", "contacts_city", "contacts_state", "contacts_country",
        "region", "zone", "account_owner", "remarks", "created_by_user",
        "created_date", "last_modified_by", "last_modified"
    )
    paginator = Paginator(account_list, 100)
    page_number = request.GET.get("page")
    accounts = paginator.get_page(page_number)
    account_records = AccountRecord.objects.only('id', 'account_id', 'account_name').order_by('account_name')
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$')

    def parse_date(date_str):
        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y-%m-%dT%H:%M', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except:
                continue
        return None

    def format_phone(val):
        return ''.join(filter(str.isdigit, val or '')) or None

    def is_exact_duplicate(model, field_map, row_data):
        filters = {}
        for model_field, form_field in field_map.items():
            value = (row_data.get(form_field) or "").strip()
            if not value:
                return False
            if model_field in ['mobile', 'other_phone', 'phone']:
                filters[model_field] = format_phone(value)
            elif model_field.endswith('date'):
                filters[model_field] = parse_date(value)
            else:
                filters[f"{model_field}__iexact"] = value
        return model.objects.filter(**filters).exists()

    def save_contact(row, row_num, existing_contact_keys=None):
        contact_field_map = {
            'full_name': 'Full Name',
            'email': 'Email',
            'mobile': 'MobilePhone',
            'other_phone': 'AlternatePhone',
            'account_name': 'Account_Name',
            'industry': 'Industry',
            'contacts_city': 'City',
            'state': 'State',
            'country': 'Country',
            'region': 'REGION',
            'zone': 'Zone',
            'account_owner': 'Account Owner'
        }
        email = row.get('Email', '').strip()
        if email and not email_pattern.match(email):
            return False, f"Invalid email format: {email}"
        if is_exact_duplicate(Account, contact_field_map, row):
            return False, f"Duplicate contact: {row.get('Full Name') or row.get('Email')} (all fields match existing record)"
        try:
            contact_id = row.get('Contact_Id') or str(1000000000 + row_num)
            account = Account(
                first_name=None,
                last_name=None,
                full_name=row.get('Full Name'),
                title=row.get('Title', ''),
                organization_level=row.get('OrganizationLevel', ''),
                department=row.get('Department', ''),
                city=row.get('City', ''),
                state=row.get('State', ''),
                country=row.get('Country', ''),
                contacts_city=row.get('contacts_city', ''),
                contacts_state=row.get('contacts_state', ''),
                contacts_country=row.get('contacts_country', ''),
                mobile=format_phone(row.get('MobilePhone')),
                other_phone=format_phone(row.get('AlternatePhone')),
                email=row.get('Email', '') or None,
                account_id=row.get('Account_Id', ''),
                contact_id=contact_id,
                account_owner=row.get('Account Owner', ''),
                account_name=row.get('Account_Name', ''),
                industry=row.get('Industry', ''),
                region=row.get('REGION', ''),
                zone=row.get('Zone', ''),
                created_by_user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                remarks=row.get('Remarks', ''),
                created_date=parse_date(row['Contact_CreatedDate']) if row.get('Contact_CreatedDate') else timezone.now().date()
            )
            account.save()
            return True, "Contact saved"
        except Exception as e:
            return False, f"Error saving contact: {str(e)}"

    def save_account(data, row_num, user):
        try:
            account_name = data.get("Account_Name", "").strip()
            industry = data.get("Industry", "").strip()
            account_owner = data.get("Account Owner", "").strip()
            region = data.get("REGION", "").strip()
            zone = data.get("Zone", "").strip()
            mailing_city = data.get("City", "").strip() or data.get("MailingCity", "").strip()
            mailing_state = data.get("State", "").strip() or data.get("MailingState", "").strip()
            mailing_country = data.get("Country", "").strip() or data.get("MailingCountry", "").strip()
            contacts_city = data.get("contacts_city", "").strip()
            contacts_state = data.get("contacts_state", "").strip()
            contacts_country = data.get("contacts_country", "").strip()
            created_by = user
            created_date = timezone.now().date()
            AccountRecord.objects.create(
                account_name=account_name,
                industry=industry,
                account_owner=account_owner,
                region=region,
                zone=zone,
                city=mailing_city,
                state=mailing_state,
                country=mailing_country,
                created_by=created_by,
                created_date=created_date
            )
            return True, "Account record saved successfully"
        except Exception as e:
            return False, f"Error saving account record (row {row_num}): {str(e)}"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            form_data = {
                'Full Name': request.POST.get('Fullname') or request.POST.get('Full Name'),
                'Title': request.POST.get('Title'),
                'OrganizationLevel': request.POST.get('OrganizationLevel'),
                'Department': request.POST.get('Department'),
                'Email': request.POST.get('Email'),
                'MobilePhone': request.POST.get('MobilePhone'),
                'AlternatePhone': request.POST.get('AlternatePhone'),
                'Account_Name': request.POST.get('Account_Name'),
                'Industry': request.POST.get('Industry'),
                'Description': request.POST.get('Description'),
                'Account Owner': request.POST.get('Account Owner'),
                'REGION': request.POST.get('REGION'),
                'Zone': request.POST.get('Zone'),
                'City': request.POST.get('City'),
                'State': request.POST.get('State'),
                'Country': request.POST.get('Country'),
                'contacts_city': request.POST.get('contacts_city'),
                'contacts_state': request.POST.get('contacts_state'),
                'contacts_country': request.POST.get('contacts_country'),
                'Remarks': request.POST.get('Remarks'),
                'CreatedByName': request.POST.get('CreatedByName'),
                'CreatedDate': request.POST.get('CreatedDate'),
            }
            contact_success, contact_msg = save_contact(form_data, 0, request.user)
            account_success, account_msg = save_account(form_data, 0, request.user)
            if not contact_success or not account_success:
                return JsonResponse({
                    'status': 'error',
                    'message': contact_msg or account_msg or "Record already exists"
                })
            return JsonResponse({'status': 'success', 'message': 'Record added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"Error processing form: {str(e)}"})

    elif 'form_type' in request.POST and request.POST['form_type'] == 'unified':
        try:
            form_data = {
                'Full Name': request.POST.get('Fullname'),
                'Title': request.POST.get('Title'),
                'OrganizationLevel': request.POST.get('OrganizationLevel'),
                'Department': request.POST.get('Department'),
                'Email': request.POST.get('Email'),
                'MobilePhone': request.POST.get('MobilePhone'),
                'AlternatePhone': request.POST.get('AlternatePhone'),
                'Account_Name': request.POST.get('Account_Name'),
                'Industry': request.POST.get('Industry'),
                'Description': request.POST.get('Description'),
                'Account Owner': request.POST.get('Account Owner'),
                'REGION': request.POST.get('REGION'),
                'Zone': request.POST.get('Zone'),
                'City': request.POST.get('MailingCity'),
                'State': request.POST.get('MailingState'),
                'Country': request.POST.get('MailingCountry'),
                'Remarks': request.POST.get('Remarks'),
                'CreatedByName': request.POST.get('CreatedByName'),
                'CreatedDate': request.POST.get('CreatedDate'),
            }
            contact_success, contact_msg = save_contact(form_data, 0)
            account_success, account_msg = save_account(form_data, 0, request.user)
            if contact_success and account_success:
                messages.success(request, "Record added successfully!")
            else:
                if "Duplicate" in contact_msg or "Duplicate" in account_msg:
                    messages.warning(request, contact_msg or account_msg)
                else:
                    messages.error(request, contact_msg or account_msg)
            return redirect('setup')
        except Exception as e:
            messages.error(request, f"Error processing form: {str(e)}")
            return redirect('setup')

    elif 'csv_file' in request.FILES:
        try:
            content = request.FILES['csv_file'].read()
            for enc in ['utf-8-sig', 'utf-8', 'cp1252']:
                try:
                    decoded = content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                messages.error(request, "Encoding error. Try saving CSV as UTF-8.")
                return redirect('setup')

            reader = csv.DictReader(io.StringIO(decoded))
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            batch_contacts = []
            batch_accounts = []
            batch_size = 1000
            created = contact_count = account_count = duplicate_count = error_count = 0
            errors = []
            duplicates = []
            existing_account_names = set(AccountRecord.objects.values_list('account_name', flat=True))
            existing_contact_keys = set(
                (
                    a.full_name.lower() if a.full_name else '',
                    a.email.lower() if a.email else ''
                )
                for a in Account.objects.only('full_name', 'email')
            )
            for row_num, raw_row in enumerate(reader, start=2):
                try:
                    row = {k.strip(): v.strip() for k, v in raw_row.items() if k}
                    if not any(row.values()):
                        continue
                    email = row.get('Email', '')
                    if email and not email_pattern.match(email):
                        error_count += 1
                        errors.append(f"Row {row_num} (Contact): Invalid email format: {email}")
                        continue
                    contact_key = (
                        row.get('Full Name', '').lower(),
                        row.get('Email', '').lower() if row.get('Email') else ''
                    )
                    if contact_key in existing_contact_keys:
                        duplicate_count += 1
                        duplicates.append(f"Row {row_num} (Contact): Duplicate contact")
                    else:
                        existing_contact_keys.add(contact_key)
                        contact_id = row.get('Contact_Id') or str(1000000000 + row_num)
                        contact = Account(
                            first_name=None,
                            last_name=None,
                            full_name=row.get('Full Name'),
                            title=row.get('Title', ''),
                            organization_level=row.get('OrganizationLevel', ''),
                            department=row.get('Department', ''),
                            city=row.get('City', ''),
                            state=row.get('State', ''),
                            country=row.get('Country', ''),
                            contacts_city=row.get('contacts_city', ''),
                            contacts_state=row.get('contacts_state', ''),
                            contacts_country=row.get('contacts_country', ''),
                            mobile=format_phone(row.get('MobilePhone')),
                            other_phone=format_phone(row.get('AlternatePhone')),
                            email=row.get('Email', '') or None,
                            account_id=row.get('Account_Id', ''),
                            contact_id=contact_id,
                            account_owner=row.get('Account Owner', ''),
                            account_name=row.get('Account_Name', ''),
                            industry=row.get('Industry', ''),
                            region=row.get('REGION', ''),
                            zone=row.get('Zone', ''),
                            created_by_user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                            remarks=row.get('Remarks', ''),
                            created_date=parse_date(row['Contact_CreatedDate']) if row.get('Contact_CreatedDate') else timezone.now().date()
                        )
                        batch_contacts.append(contact)

                    account_name = row.get('Account_Name', '').strip()
                    if account_name in existing_account_names:
                        duplicate_count += 1
                        duplicates.append(f"Row {row_num} (Account): Duplicate account '{account_name}'")
                    else:
                        existing_account_names.add(account_name)
                        account_id = row.get('Account_Id') or str(2000000000 + row_num)
                        account = AccountRecord(
                            account_id=account_id,
                            account_name=row.get('Account_Name', ''),
                            city=row.get('City', ''),
                            state=row.get('State', ''),
                            country=row.get('Country', ''),
                            industry=row.get('Industry', ''),
                            account_owner=row.get('Account Owner', ''),
                            created_date=parse_date(row.get('Account_CreatedDate', '')),
                            zone=row.get('Zone', ''),
                            region=row.get('REGION', ''),
                            description=row.get('Description', ''),
                            created_by=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                        )
                        batch_accounts.append(account)

                    if len(batch_contacts) >= batch_size:
                        Account.objects.bulk_create(batch_contacts)
                        contact_count += len(batch_contacts)
                        created += len(batch_contacts)
                        batch_contacts.clear()

                    if len(batch_accounts) >= batch_size:
                        AccountRecord.objects.bulk_create(batch_accounts)
                        account_count += len(batch_accounts)
                        created += len(batch_accounts)
                        batch_accounts.clear()
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")

            if batch_contacts:
                Account.objects.bulk_create(batch_contacts)
                contact_count += len(batch_contacts)
                created += len(batch_contacts)
            if batch_accounts:
                AccountRecord.objects.bulk_create(batch_accounts)
                account_count += len(batch_accounts)
                created += len(batch_accounts)

            if created:
                messages.success(request, f"Successfully processed {created} records ({contact_count} contacts, {account_count} accounts)")
            if duplicate_count:
                messages.warning(request, f"Skipped {duplicate_count} duplicate records")
            if error_count:
                messages.error(request, f"Encountered {error_count} errors. First error: {errors[0] if errors else 'Unknown'}")
            if not created and not duplicate_count and not error_count:
                messages.info(request, "No valid data found in the file")

            return redirect('preview')

        except Exception as e:
            messages.error(request, f"Error uploading CSV: {str(e)}")
            return redirect('setup')

    return render(request, 'accounts/setup.html', {
        'accounts': accounts,
        'account_records': account_records,
        'is_staff': request.user.is_staff,
        'user_full_name': request.user.get_full_name()
    })

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Account, AccountRecord

@login_required
def delete_account(request, **kwargs):
    account_id = kwargs.get('account_id') or kwargs.get('pk')
    source = request.GET.get('source')
    account_name = request.GET.get('account_name')

    if not account_id:
        messages.error(request, "No account ID provided")
        return redirect('preview')

    if request.method == 'POST':
        try:
            account = get_object_or_404(Account, pk=account_id)
            account_name_actual = account.account_name

            # Count how many contacts exist for this account name
            contact_count = Account.objects.filter(account_name=account_name_actual).count()

            # Restrict regular users from deleting the last remaining contact
            if contact_count <= 1 and not request.user.is_staff:
                messages.error(request, f"Cannot delete the last remaining contact for account '{account_name_actual}'.")
                if source == 'contacts_for_accounts' and account_name:
                    return redirect('contacts_for_account', account_name=account_name)
                return redirect('preview')

            # Proceed with deletion
            account.delete()
            messages.success(request, f"Contact for account '{account_name_actual}' deleted successfully.")

            # Check if any contacts remain; if none, delete the AccountRecord
            remaining_contacts = Account.objects.filter(account_name=account_name_actual).exists()
            if not remaining_contacts:
                deleted_record_count, _ = AccountRecord.objects.filter(account_name=account_name_actual).delete()
                if deleted_record_count:
                    messages.info(request, f"Account record '{account_name_actual}' was also deleted.")

        except Exception as e:
            messages.error(request, f"Error deleting contact: {str(e)}")

    if source == 'contacts_for_accounts' and account_name:
        return redirect('contacts_for_account', account_name=account_name)
    return redirect('preview')


@staff_approved_required
def delete_account_record(request, contact_id):
    if request.method == 'POST':
        try:
            source = request.GET.get('source', 'preview-accounts')
            account_name = request.GET.get('account_name', '')

            # Get AccountRecord
            record = get_object_or_404(AccountRecord, pk=contact_id)
            record_name = getattr(record, 'account_name', str(record))

            # 🔥 Delete all related Accounts (contacts and contacts_for_accounts)
            deleted_count, _ = Account.objects.filter(account_name=record.account_name).delete()

            # Then delete the AccountRecord
            record.delete()

            messages.success(request, f"Account record '{record_name}' and {deleted_count} related contact(s) deleted successfully.")

            if source == 'contacts_for_accounts' and account_name:
                return redirect('contacts_for_account', account_name=account_name)
            return redirect('preview-accounts')

        except Exception as e:
            messages.error(request, f"Error deleting account record: {str(e)}")
            return redirect('preview-accounts')

    return redirect('preview-accounts')

@staff_approved_required
def delete_all_accounts(request):
    if request.method == 'POST':
        # Use truncate which resets sequences automatically in PostgreSQL
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE accounts_account RESTART IDENTITY CASCADE;")
        
        messages.success(request, "All accounts have been deleted and IDs reset.")
    return redirect('preview')

def debug_user_regions(request):
    """
    Debug function to check what's happening with user regions
    Call this from a temporary URL to see the data
    """
    user = request.user
    print(f"🔍 DEBUG: Current user: {user.username}")
    print(f"🔍 DEBUG: User full name: '{user.first_name} {user.last_name}'")
    print(f"🔍 DEBUG: User is_staff: {user.is_staff}")
    
    # Check UserRegion entries
    from .models import UserRegion
    all_user_regions = UserRegion.objects.all()
    print(f"🔍 DEBUG: Total UserRegion entries: {all_user_regions.count()}")
    
    for ur in all_user_regions:
        print(f"🔍 DEBUG: UserRegion - account_owner_name: '{ur.account_owner_name}', regions: '{ur.regions}'")
    
    # Test the get_user_allowed_regions function
    allowed_regions = get_user_allowed_regions(user)
    print(f"🔍 DEBUG: User's allowed regions: {allowed_regions}")
    
    # Check Account regions
    from .models import Account
    unique_regions = Account.objects.values_list('region', flat=True).distinct()
    print(f"🔍 DEBUG: Unique regions in Account table: {list(unique_regions)}")
    
    # Check how many accounts match each region
    for region in unique_regions:
        count = Account.objects.filter(region=region).count()
        print(f"🔍 DEBUG: Accounts with region '{region}': {count}")
    
    # Test the filtering logic
    if not user.is_staff and allowed_regions:
        filtered_accounts = Account.objects.filter(region__in=allowed_regions)
        print(f"🔍 DEBUG: Filtered accounts count: {filtered_accounts.count()}")
        
        # Show some sample filtered accounts
        sample_accounts = filtered_accounts[:5]
        for acc in sample_accounts:
            print(f"🔍 DEBUG: Sample account - Name: {acc.first_name} {acc.last_name}, Region: '{acc.region}'")
    
    return HttpResponse("Debug info printed to console. Check your server logs.")

def preview_view(request):
    search_query = request.GET.get("search", "")
    allowed_regions = get_user_allowed_regions(request.user) if not request.user.is_staff else None

    # Base queryset with early filtering
    accounts = Account.objects.all()


    if allowed_regions:
        allowed_regions = [r.lower() for r in allowed_regions]
        accounts = accounts.annotate(region_lower=Lower('region')).filter(region_lower__in=allowed_regions)

    # Apply search filter
    if search_query:
        accounts = accounts.filter(
            Q(account_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Build active filters from GET
    active_filters = {}
    filter_fields = [
    "account_name", "first_name",  # <- keep this for Full Name column
    "title", "organization_level", "department", "industry", "email",
    "mobile", "other_phone", "contacts_city", "contacts_state", "contacts_country",
    "region", "zone", "account_owner", "created_by_user", "created_date",
    ]
    for field in filter_fields:
        value = request.GET.get(field)
        if value:
            if ',' in value:
                values = value.split(',')
                accounts = accounts.filter(**{f"{field}__in": values})
                active_filters[field] = values
            else:
                accounts = accounts.filter(**{f"{field}": value})
                active_filters[field] = [value]

    # Paginate
    paginator = Paginator(accounts.order_by("account_name"), 25)  # page size = 25
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # # Generate dropdown options only for paginated queryset (light version)
    # filter_options = {}
    # for field in filter_fields:
    #     qs = accounts.values(field).annotate(count=Count("id")).order_by("-count")[:25]
    #     filter_options[field] = [(entry[field], entry["count"]) for entry in qs if entry[field]]

    context = {
        "accounts": page_obj,
        # "filter_options": filter_options,
        "active_filters": active_filters,
        "search_query": search_query,
        "total_accounts": accounts.count(),
        "field_names": [
    "account_name", "full_name", "title", "organization_level",
    "department", "industry", "email", "mobile", "other_phone",
    "contacts_city", "contacts_state", "contacts_country",
    "region", "zone", "account_owner", "created_by_user", "created_date",
    "last_modified_by", "timestamp", "remarks"
],
        "allowed_regions": allowed_regions if allowed_regions else ["All Regions"],
        "user_full_name": request.user.get_full_name(),
    }
    print(f"✅ Showing {accounts.count()} accounts")

    

    return render(request, "accounts/preview.html", context)
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import Lower
from .models import Account, AccountRecord
from .utils import get_user_allowed_regions
from collections import Counter

def get_filter_options_ajax(request):
    field = request.GET.get("field")
    model = request.GET.get("model", "account").lower()

    if not field:
        return JsonResponse({"error": "Missing field"}, status=400)

    # Allowed fields
    account_fields = [
        'contact_id', 'account_id', 'account_name', 'account_phone', 'full_name',
        'first_name', 'last_name', 'title', 'organization_level',
        'department', 'email', 'mobile', 'phone', 'other_phone',
        'industry', 'country', 'city', 'state', 'contacts_city',
        'contacts_state', 'contacts_country', 'website', 'region',
        'zone', 'account_owner', 'created_by_user', 'last_modified_by',
        'created_date', 'remarks', 'timestamp'
    ]

    accountrecord_fields = [
        'account_id', 'account_name', 'city', 'state', 'country',
        'created_by', 'last_modified_by', 'created_date',
        'last_modified', 'industry', 'phone', 'region',
        'website', 'zone', 'account_owner'
    ]

    if model == "accountrecord":
        allowed_fields = accountrecord_fields
        base_queryset = AccountRecord.objects.all()
    else:
        allowed_fields = account_fields
        base_queryset = Account.objects.all()

        if not request.user.is_staff:
            allowed_regions = get_user_allowed_regions(request.user)
            if allowed_regions:
                base_queryset = base_queryset.annotate(region_lower=Lower('region')).filter(
                    region_lower__in=[r.lower() for r in allowed_regions]
                )

    # Validate field
    if field not in allowed_fields:
        return JsonResponse({'error': 'Invalid field'}, status=400)

    # Filter params (used if any in future — currently unused in dropdown loads)
    filter_kwargs = {}
    for k, v in request.GET.items():
        if k not in {"field", "model"} and v.strip():
            filter_kwargs[f"{k}__in"] = [val.strip() for val in v.split(',') if val.strip()]
    queryset = base_queryset.filter(**filter_kwargs)

    # Special handling
    if field == "full_name":
        values = (
            queryset.exclude(full_name__isnull=True)
                    .exclude(full_name__exact="")
                    .values("full_name")
                    .annotate(count=Count("id"))
                    .order_by("-count")
        )
        options = [{"value": v["full_name"], "count": v["count"]} for v in values]
        return JsonResponse({"options": options})


    elif field in ["created_by_user", "created_by", "last_modified_by"]:
        user_field = field
        values = (
            queryset.exclude(**{f"{user_field}__isnull": True})
            .values(f"{user_field}__id", f"{user_field}__first_name", f"{user_field}__last_name", f"{user_field}__username")
            .annotate(count=Count("id"))
        )

        options = []
        for v in values:
            user_id = v[f"{user_field}__id"]
            name = f'{v.get(f"{user_field}__first_name", "")} {v.get(f"{user_field}__last_name", "")}'.strip()
            if not name:
                name = v.get(f"{user_field}__username", "Unknown")
            options.append({
                "value": user_id,
                "count": v["count"],
                "label": name,
            })

        return JsonResponse({
            "options": [{"value": opt["value"], "count": opt["count"], "label": opt["label"]} for opt in options]
        })

    elif field in ['created_date', 'last_modified', 'timestamp']:
        dates = queryset.exclude(**{f"{field}__isnull": True}).values_list(field, flat=True).distinct()
        formatted = sorted({d.strftime("%Y-%m-%d") for d in dates if d})
        return JsonResponse({"options": [{"value": d, "count": "-"} for d in formatted]})

    # Default string/enum/int fields
    values = (
        queryset.exclude(**{f"{field}__isnull": True})
        .values(field)
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    options = [{"value": v[field] if v[field] else "—", "count": v["count"]} for v in values]
    return JsonResponse({"options": options})


from django.db.models import Q
from .models import AccountRecord

def get_filter_options(model="account", search_query=None):
    from .models import Account, AccountRecord
    from django.db.models import Q

    if model == "accountrecord":
        queryset = AccountRecord.objects.all()
        fields = [
            'account_id', 'account_name', 'street', 'city', 'state','country', 'phone', 'website', 'industry','region', 'zone', 'account_owner', 'created_date', 'created_by_id', 'created_by_user', 'timestamp'
        ]
    else:  # Default to Account (contacts)
        queryset = Account.objects.all()
        fields = [
        'contact_id', 'account_id', 'account_name', 'account_phone',
        'first_name', 'last_name', 'title', 'organization_level',
        'department', 'email', 'mobile', 'phone', 'other_phone',
        'industry', 'country', 'state', 'city', 'contacts_city',
        'contacts_state', 'contacts_country', 'website', 'region', 
        'zone', 'account_owner', 'created_by_id','created_by_user', 'created_date', 
        'remarks', 'timestamp'
    ]

        if search_query:
            queryset = queryset.filter(
                Q(account_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

    filter_options = {}

    for field in fields:
        if field.endswith('date') or field == 'timestamp':
            dates = queryset.values_list(field, flat=True).distinct()
            formatted = [d.strftime('%Y-%m-%d') if d else '—' for d in dates if d]
            filter_options[field] = sorted(set(formatted)) or ['—']
        else:
            values = queryset.values_list(field, flat=True).distinct()
            processed = [str(v) if v not in [None, ''] else '—' for v in values]
            filter_options[field] = sorted(set(processed))

    return filter_options

def download_accounts_csv(request):
    # Token validation (same as before)
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Missing token.", status=400)

    try:
        token_uuid = UUID(token)
        download_request = DownloadRequest.objects.get(token=token_uuid)
    except (ValueError, TypeError):
        return HttpResponse("Invalid token format.", status=400)
    except DownloadRequest.DoesNotExist:
        return HttpResponse("Invalid token.", status=404)

    if download_request.status != "approved":
        return HttpResponse("Download not approved yet.", status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

    writer = csv.writer(response)
    # Write header row with your exact column names
    writer.writerow([
        'Account_Id', 'Account_Name', 'AccountPhone', 'Contact_Id',
        'FirstName', 'LastName', 'Title', 'OrganizationLevel',
        'Department', 'Email', 'MobilePhone', 'Phone', 'OtherPhone',
        'Industry', 'MailingCountry', 'MailingPostalCode', 'MailingState',
        'MailingCity', 'Website', 'REGION', 'Zone', 'Account Owner',
        'CreatedById', 'CreatedDate', 'Remarks', 'timestamp'
    ])

    accounts = Account.objects.all()

    for account in accounts:
        writer.writerow([
            account.account_id,
            account.account_name,
            account.account_phone,
            account.contact_id,
            account.first_name,
            account.last_name,
            account.title,
            account.organization_level,
            account.department,
            account.email,
            account.mobile,
            account.phone,
            account.other_phone,
            account.industry,
            account.mailing_country,
            account.mailing_zip,
            account.mailing_state,
            account.mailing_city,
            account.website,
            account.region,
            account.zone,
            account.account_owner,
            account.created_by_user,
            account.created_date.strftime('%Y-%m-%d') if account.created_date else '',
            account.remarks,
            account.timestamp.strftime('%Y-%m-%d %H:%M:%S') if account.timestamp else ''
        ])

    return response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.urls import reverse

def request_download(request):
    if request.method == 'POST':
        # Get data type and context from form
        data_type = request.POST.get('data_type', 'contacts')
        page_context = request.POST.get('page_context', '')
        
        # Store filter parameters for later use
        filter_params = {}
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'data_type', 'page_context']:
                filter_params[key] = value
        
        download_request = DownloadRequest.objects.create(
            requested_by=request.user.email,
            status='pending',
            data_type=data_type,
            page_context=page_context,
            filter_parameters=filter_params  # Use your existing field name
        )
        
        # Build approval URLs with SITE_URL from settings
        approval_url = settings.SITE_URL + reverse('approve_download', args=[download_request.token])
        rejection_url = settings.SITE_URL + reverse('reject_download', args=[download_request.token])
        
        # Send email to admin
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        
        # Determine data description for email
        data_descriptions = {
            'contacts': 'Contact Data',
            'accounts': 'Account Records Data',
            'contacts_for_account': f'Contacts for Account: {filter_params.get("account_name", "Unknown")}'
        }
        data_description = data_descriptions.get(data_type, 'Data')
        
        # Use HTML email template
        html_message = render_to_string('accounts/download_request_email.html', {
            'user_email': request.user.email,
            'token': download_request.token,
            'timestamp': download_request.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'approval_url': approval_url,
            'rejection_url': rejection_url,
            'data_type': data_description,
            'page_context': page_context
        })
        
        send_mail(
            subject=f"Download Request for {data_description} from {request.user.email}",
            message="",  # Leave empty for HTML-only email
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False,
        )
        
        return HttpResponse(status=204)  # No content response
    
    return HttpResponseBadRequest('Invalid request method')

def approve_download(request, request_id):
    try:
        download_req = get_object_or_404(DownloadRequest, token=request_id)
        download_req.status = "approved"
        download_req.save()
        
        # Send download link to user using SITE_URL
        download_url = f"{settings.SITE_URL}/download/accounts/?token={request_id}"  # default

        if download_req.data_type == 'contacts':
            download_url = f"{settings.SITE_URL}/download/contacts/?token={request_id}"
        elif download_req.data_type == 'contacts_for_account':
            download_url = f"{settings.SITE_URL}/download/contacts-for-account/?token={request_id}"

        
        # Determine what data will be downloaded
        data_descriptions = {
            'contacts': 'Contact Data',
            'accounts': 'Account Records Data',
            'contacts_for_account': 'Contacts for Account Data'
        }
        data_description = data_descriptions.get(download_req.data_type, 'Data')
        
        send_mail(
            subject=f"Your {data_description} Download Request Was Approved",
            message=f"Download your data here: {download_url}",
            html_message=f"""
                <h3>Download Ready - {data_description}</h3>
                <p>Your request for {data_description} has been approved. Click below to download:</p>
                <a href="{download_url}" style="display:inline-block; padding:10px 20px; background:#4CAF50; color:white; text-decoration:none; border-radius:4px;">
                    Download CSV
                </a>
                <p>Or copy this link: {download_url}</p>
                <p>This link will expire in 24 hours.</p>
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[download_req.requested_by],
            fail_silently=False,
        )
        
        logger.info(f"Approved download request {request_id} for {download_req.requested_by} - Data type: {download_req.data_type}")
        return HttpResponse(f"Download approved and user notified - {data_description}")
    
    except Exception as e:
        logger.error(f"Error approving download {request_id}: {str(e)}")
        return HttpResponseBadRequest("Error processing approval")
    
def reject_download(request, request_id):
    try:
        download_req = get_object_or_404(DownloadRequest, token=request_id)
        download_req.status = "rejected"
        download_req.save()

        send_mail(
            subject=f"Download Request Rejected",
            message=f"Your download request for {download_req.data_type} has been rejected.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[download_req.requested_by],
            fail_silently=False,
        )

        return HttpResponse(f"Download request {request_id} rejected.")
    except Exception as e:
        logger.error(f"Error rejecting download {request_id}: {str(e)}")
        return HttpResponseBadRequest("Error processing rejection.")


def download_accounts_csv(request):
    """Generate and serve CSV based on the download request type"""
    token = request.GET.get('token')
    if not token:
        return HttpResponseBadRequest('Token required')
    
    try:
        download_req = get_object_or_404(DownloadRequest, token=token, status='approved')
        
        # Check if request is still valid (24 hours)
        if timezone.now() - download_req.timestamp > timezone.timedelta(hours=24):
            return HttpResponseBadRequest('Download link has expired')
        
        # Generate CSV based on data type
        if download_req.data_type == 'contacts':
            return generate_contacts_csv(download_req)
        elif download_req.data_type == 'accounts':
            return generate_accounts_csv(download_req)
        elif download_req.data_type == 'contacts_for_account':
            return generate_contacts_for_account_csv(download_req)
        else:
            return HttpResponseBadRequest('Invalid data type')
            
    except Exception as e:
        logger.error(f"Error generating CSV for token {token}: {str(e)}")
        return HttpResponseBadRequest('Error generating download')

def generate_contacts_csv(download_req):
    import csv
    from django.http import HttpResponse
    from django.db.models import Q
    from datetime import datetime

    contacts = Account.objects.all()
    filter_params = download_req.filter_parameters or {}

    for key, value in filter_params.items():
        if not value:
            continue

        if key == 'search':
            contacts = contacts.filter(
                Q(account_name__icontains=value) |
                Q(phone__icontains=value) |
                Q(industry__icontains=value) |
                Q(account_owner__icontains=value) |
                Q(first_name__icontains=value) |
                Q(last_name__icontains=value) |
                Q(email__icontains=value) |
                Q(mobile__icontains=value)
            )
        elif key in ['created_date', 'timestamp']:
            try:
                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                contacts = contacts.filter(**{f"{key}__date": date_val})
            except ValueError:
                continue
        elif ',' in value:
            filters = value.split(',')
            q = Q()
            for item in filters:
                if item != '—':
                    q |= Q(**{f"{key}__icontains": item})
            contacts = contacts.filter(q)
        else:
            if value != '—':
                contacts = contacts.filter(**{f"{key}__icontains": value})

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    writer = csv.writer(response)

    headers = [
        'Account ID', 'Account Name', 'Account Phone', 'First Name', 'Last Name',
        'Title', 'Organization Level', 'Department', 'Email', 'Mobile', 'Phone',
        'Other Phone', 'Industry', 'Country', 'State', 'City', 'Region',
        'Contact ID', 'Zone', 'Account Owner', 'Created By Name',
        'Created Date', 'Remarks'
    ]
    writer.writerow(headers)

    for contact in contacts:
        writer.writerow([
            contact.account_id, contact.account_name, contact.account_phone,
            contact.first_name, contact.last_name, contact.title,
            contact.organization_level, contact.department, contact.email,
            contact.mobile, contact.phone, contact.other_phone, contact.industry,
            contact.country, contact.state, contact.city, contact.region,
            contact.contact_id, contact.zone, contact.account_owner,
            contact.created_by_user.get_full_name() if contact.created_by_user else "",
            contact.created_date, contact.remarks
        ])

    return response

def generate_accounts_csv(download_req):
    import csv
    from django.http import HttpResponse
    from django.db.models import Q

    accounts = AccountRecord.objects.all()
    filter_params = download_req.filter_parameters or {}

    for key, value in filter_params.items():
        if value and key != 'account_name':
            if hasattr(AccountRecord, key):
                accounts = accounts.filter(**{f'{key}__icontains': value})

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="account_records.csv"'
    writer = csv.writer(response)

    headers = [
        'Account ID', 'Account Name', 'City', 'State', 'Country',
        'Industry', 'Description', 'Zone', 'Region', 'Account Owner',
        'Created By Name', 'Created Date'
    ]
    writer.writerow(headers)

    for account in accounts:
        writer.writerow([
            account.account_id, account.account_name, account.city,
            account.state, account.country, account.industry,
            account.description, account.zone, account.region,
            account.account_owner,
            account.created_by.get_full_name() if account.created_by else "",
            account.created_date
        ])

    return response
def generate_contacts_for_account_csv(download_req):
    import csv
    from django.http import HttpResponse, HttpResponseBadRequest
    from django.db.models import Q

    filter_params = download_req.filter_parameters or {}
    account_name = filter_params.get('account_name')

    if not account_name:
        return HttpResponseBadRequest('Account name is required')

    contacts = Account.objects.filter(account_name=account_name)
    ignored_keys = {'csrfmiddlewaretoken', 'data_type', 'page_context', 'account_name'}

    for key, value in filter_params.items():
        if key in ignored_keys:
            continue
        if isinstance(value, list):
            filter_q = Q()
            for val in value:
                if val and val != '—':
                    filter_q |= Q(**{f"{key}__icontains": val})
            contacts = contacts.filter(filter_q)
        elif value and value != '—':
            contacts = contacts.filter(**{f"{key}__icontains": value})

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contacts_for_{account_name}.csv"'
    writer = csv.writer(response)

    headers = [
        'Account ID', 'Account Name', 'Account Phone', 'First Name', 'Last Name',
        'Title', 'Organization Level', 'Department', 'Email', 'Mobile', 'Phone',
        'Other Phone', 'Industry', 'Country', 'State', 'City',
        'Region', 'Contact ID', 'Zone', 'Account Owner',
        'Created By Name', 'Created Date', 'Remarks'
    ]
    writer.writerow(headers)

    for contact in contacts:
        writer.writerow([
            contact.account_id, contact.account_name, contact.account_phone,
            contact.first_name, contact.last_name, contact.title,
            contact.organization_level, contact.department, contact.email,
            contact.mobile, contact.phone, contact.other_phone, contact.industry,
            contact.country, contact.state, contact.city, contact.region,
            contact.contact_id, contact.zone, contact.account_owner,
            contact.created_by_user.get_full_name() if contact.created_by_user else "",
            contact.created_date, contact.remarks
        ])

    return response

def home_view(request):
    return render(request, "accounts/home.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import AccountRecord

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AccountRecord
import io
import csv
from datetime import datetime

def setup_accounts_view(request):
    if request.method == 'POST':
        try:
            # Create AccountRecord with proper field mapping
            account = AccountRecord(
            account_id=request.POST.get('Account_Id', '').strip(),
            account_name=request.POST.get('Account_Name', '').strip(),
            city=request.POST.get('City', '').strip(),
            state=request.POST.get('State', '').strip(),
            country=request.POST.get('Country', '').strip(),
            phone=request.POST.get('Phone', '').strip(),
            website=request.POST.get('Website', '').strip(),
            industry=request.POST.get('Industry', '').strip(),  # Required
            description=request.POST.get('Description', '').strip(),
            region=request.POST.get('REGION', '').strip(),
            zone=request.POST.get('Zone', '').strip(),
            account_owner=request.POST.get('Account Owner', '').strip(),
            created_by_id=request.POST.get('CreatedById', '').strip(),
        )

            
            # Handle date field
            created_date = request.POST.get('CreatedDate', '').strip()
            if created_date:
                try:
                    account.created_date = datetime.strptime(created_date, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid date format for CreatedDate")
            
            account.save()
            messages.success(request, "Account created successfully!")
            return redirect('preview-accounts')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('setup')
    
    return redirect('setup')

def accounts_preview_view(request):
    print("🔍 accounts_preview_view called")

    filterable_fields = [
    'account_name', 'city', 'state', 'country',
    'industry', 'region', 'zone', 'account_owner',
    'description', 'created_by__username', 'created_date',
    'last_modified_by__username', 'last_modified'
]


    search_query = request.GET.get('search', '').strip()

    # Get allowed regions
    if request.user.is_staff:
        allowed_regions = ["all"]
    else:
        allowed_regions = [r.lower() for r in get_user_allowed_regions(request.user)]

    # OPTIMIZATION 1: Get latest records in a single efficient query
    latest_records = AccountRecord.objects.filter(
        id__in=AccountRecord.objects.values('account_name').annotate(
            latest_id=Max('id')
        ).values('latest_id')
    )

    # Region filtering for non-staff
    if not request.user.is_staff:
        latest_records = latest_records.annotate(
            region_lower=Lower('region')
        ).filter(region_lower__in=allowed_regions)

    # Filter logic
    filter_query = Q()
    active_filters = {}

    for field in filterable_fields:
        values = request.GET.getlist(field)
        if values:
            filter_query &= Q(**{f"{field}__in": values})
            active_filters[field] = values

    if filter_query:
        latest_records = latest_records.filter(filter_query)

    # Search logic
    if search_query:
        latest_records = latest_records.filter(
            Q(account_name__icontains=search_query) |
            Q(account_owner__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(country__icontains=search_query) |
            Q(industry__icontains=search_query)
        )

    # OPTIMIZATION 2: Prefetch all related data
    latest_records = latest_records.select_related(
    'created_by', 'last_modified_by', 'linked_account__created_by_user', 'linked_account__last_modified_by'
)


    # OPTIMIZATION 3: Cache filter options to avoid multiple queries
    filter_options = {}
    if not search_query:  # Only calculate filter options if no search is active
        for field in filterable_fields:
            # Use the base queryset without search filters
            base_qs = AccountRecord.objects.filter(
                id__in=AccountRecord.objects.values('account_name').annotate(
                    latest_id=Max('id')
                ).values('latest_id')
            )
            if not request.user.is_staff:
                base_qs = base_qs.annotate(
                    region_lower=Lower('region')
                ).filter(region_lower__in=allowed_regions)
            
            if field in ['created_by__username', 'last_modified_by__username']:
                options = base_qs.values(field).annotate(count=Count('id')).order_by(field)
            else:
                options = base_qs.values(field).annotate(count=Count('id')).order_by(field)

            filter_options[field] = [
                (item[field], item['count']) 
                for item in options if item[field]
            ]

    # Pagination
    paginator = Paginator(latest_records, 25)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'accounts/accounts_preview.html', {
        'accounts': page_obj,
        'total_accounts': paginator.count,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'user_full_name': request.user.get_full_name() or request.user.username,
        'page_range': paginator.get_elided_page_range(number=page_obj.number, on_each_side=3, on_ends=1),
        'search_query': search_query,
        'filterable_fields': filterable_fields,
        'filter_options': filter_options,
        'active_filters': active_filters,
        'allowed_regions': allowed_regions,
    })

def format_phone_number(phone_str):
    if not phone_str:
        return ''
    try:
        # Handle scientific notation
        if 'E+' in phone_str:
            phone_num = int(float(phone_str))
        else:
            phone_num = int(phone_str.replace('.', ''))
        return str(phone_num)
    except (ValueError, TypeError):
        return phone_str
    
@login_required
def contacts_for_account(request, account_name):
    allowed_regions = [r.lower() for r in get_user_allowed_regions(request.user)]
    search_query = request.GET.get('search', '').strip()

    base_queryset = Account.objects.filter(account_name=account_name).select_related(
        'last_modified_by', 'created_by_user'
    )

    # Apply search
    if search_query:
        base_queryset = base_queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(region__icontains=search_query) |
            Q(full_name__icontains=search_query)  # Changed from FullName to full_name
        )

    # Filterable fields - updated to use correct field names
    filterable_fields = [
        'full_name', 'account_name', 'title', 'organization_level', 'department',
        'industry', 'email', 'mobile', 'other_phone', 'contacts_city', 'contacts_state', 'contacts_country',
        'region', 'zone', 'account_owner',
        'created_by_user', 'created_date', 'last_modified_by',
        'last_modified', 'remarks'
    ]

    active_filters = {}
    for field in filterable_fields:
        values = request.GET.getlist(field)
        if values:
            normalized = [v.strip() for v in values if v and v != "—"]
            if normalized:
                active_filters[field] = normalized
                q = Q()
                for val in normalized:
                    q |= Q(**{f"{field}__icontains": val})
                base_queryset = base_queryset.filter(q)


    # Add computed full_name attribute to each contact if not already set
    contacts = list(base_queryset)
    for contact in contacts:
        if not contact.full_name:
            contact.full_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()

    # Filter options - use actual DB fields
    filter_options = {}
    for field in filterable_fields:
        values = base_queryset.values(field).annotate(count=Count('id')).order_by(field)
        filter_options[field] = [(v[field] or "—", v['count']) for v in values]

    # Field display labels
    field_labels = [
        ('account_name', 'Account Name'),
        ('full_name', 'Full Name'),
        ('title', 'Title'),
        ('organization_level', 'Organisational Level'),
        ('department', 'Department'),
        ('industry', 'Industry'),
        ('email', 'Email ID'),
        ('mobile', 'Mobile Phone'),
        ('other_phone', 'Alternate Phone'),
        ('contacts_city', 'Contacts City'),
        ('contacts_state', 'Contacts State'),
        ('contacts_country', 'Contacts Country'),
        ('region', 'Region'),
        ('zone', 'Zone'),
        ('account_owner', 'Account Owner'),
        ('created_by_user', 'Created by Name'),
        ('created_date', 'Created Date Timestamp'),
        ('last_modified_by', 'Last Modified by Name'),
        ('last_modified', 'Last Modified Timestamp'),
        ('remarks', 'Remarks'),
    ]

    context = {
        'account_name': account_name,
        'contacts': contacts,
        'allowed_regions': allowed_regions,
        'user_full_name': request.user.get_full_name() or request.user.username,
        'field_labels': field_labels,
        'filter_options': filter_options,
        'active_filters': active_filters,
        'search_query': search_query,
    }

    return render(request, 'accounts/contacts_for_account.html', context)
  
def setup_accounts(request):
    if request.method == 'POST':
        # Process the submitted Account form
        print(request.POST)  # Debug
        return redirect('setup')  # Redirect after successful POST
    return redirect('setup')  # Redirect if GET request

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import AccountRecord # Make sure to import AccountRecord
from django.db.models.functions import Upper
from django.db.models import Value as V

@require_GET
def get_account_details(request):
    account_name = request.GET.get('account_name', '').strip()

    if not account_name:
        return JsonResponse({'error': 'No account name provided'}, status=400)

    account = Account.objects.annotate(
        name_upper=Upper('account_name')
    ).filter(
        name_upper=account_name.upper()
    ).first()

    if not account:
        return JsonResponse({'error': 'Account not found'}, status=404)

    data = {
        'zone': account.zone or '',
        'account_owner': account.account_owner or '',
        'account_phone': account.account_phone or '',
        'account_id': account.account_id or '',
        'industry': account.industry or '',
        'website': account.website or '',
        'region': account.region or '',
    }
    return JsonResponse({'success': True, 'data': data})

@require_GET
def get_account_record_details(request):
    print("🔍 Hit get_account_record_details view")
    name = request.GET.get("name", "").strip()

    if not name:
        return JsonResponse({"error": "Missing name parameter"}, status=400)

    account = AccountRecord.objects.filter(account_name__iexact=name).first()
    if not account:
        return JsonResponse({"error": "Account not found"}, status=404)

    data = {
        "industry": account.industry,
        "billing_city": account.billing_city,
        "billing_state": account.billing_state,
        "billing_country": account.billing_country,
        "billing_zip": account.billing_postal_code,
        "billing_street": account.billing_street,
        "region": account.region,
        "zone": account.zone,
        "description": account.description,
        "account_owner": account.account_owner,
        "phone": account.phone,
        "created_date": account.created_date.strftime('%Y-%m-%d') if account.created_date else "",
        "created_by_id": account.created_by_id,
        "website": account.website,
        "account_id": account.account_id,

    }
    return JsonResponse({"success": True, "data": data})


def setup(request):
    if request.method == 'POST':
        account = Account(
            salutation=request.POST.get('salutation', ''),
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            title=request.POST.get('title', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            mailing_zip=request.POST.get('mailing_zip', ''),
            country=request.POST.get('country', ''),
            phone=request.POST.get('phone', ''),
            account_phone=request.POST.get('account_phone', ''),
            mobile=request.POST.get('mobile', ''),
            fax=request.POST.get('fax', ''),
            email=request.POST.get('email', ''),
            account_id=request.POST.get('account_id', ''),
            account_name=request.POST.get('account_name', ''),
            account_owner=request.POST.get('account_owner', ''),
            account_owner_alias=request.POST.get('account_owner_alias', ''),
            website=request.POST.get('website', ''),
            industry=request.POST.get('industry', ''),
            account_final_id=request.POST.get('account_final_id', ''),
            salesperson_sf_id=request.POST.get('salesperson_sf_id', ''),
            region=request.POST.get('region', ''),
            account_created_date=request.POST.get('account_created_date') or None,
            last_updated=request.POST.get('last_updated') or None,
            remarks=request.POST.get('remarks', ''),
            zone=request.POST.get('zone', ''),
            created_by=request.user  # ✅ use the actual User object
        )
        account.save()

        messages.success(request, 'Account created successfully!')
        return redirect('setup')


    accounts = Account.objects.all()

    return render(request, 'accounts/setup.html', {'accounts': accounts})

def get_account_by_name(request):
    account_name = request.GET.get('account_name', '').strip()

    if not account_name:
        return JsonResponse({'error': 'Account name required'}, status=400)

    try:
        # New (partial match fallback)
        account = AccountRecord.objects.filter(account_name__icontains=account_name).order_by('-created_date').first()


        if not account:
            return JsonResponse({'error': 'Account not found'}, status=404)

        return JsonResponse({
            'data': {
                'region': account.region or '',
                'zone': account.zone or '',
                'account_owner': account.account_owner or '',
                'industry': account.industry or ''
            }
        })

    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
def update_account(request, pk):
    try:
        account = get_object_or_404(Account, pk=pk)
        source = request.GET.get('source', 'contacts')

        if request.method == 'POST':
            fields_to_update = [
                'first_name', 'last_name', 'full_name', 'title', 'email', 'phone',
                'account_phone', 'mobile', 'other_phone', 'organization_level',
                'department', 'industry', 'city', 'state', 'country',
                'account_id', 'account_name', 'account_owner', 'region',
                'zone'
            ]

            email = request.POST.get('email', '').strip()
            mobile = request.POST.get('mobile', '').strip()

            # Require at least one of email or mobile
            # Prepare context in case of re-render
            context = {
                'account': account,
                'now': datetime.now().strftime('%Y-%m-%d'),
                'source': source
            }

            # Require at least one of email or mobile
            if not email and not mobile:
                context['email_error'] = 'Please provide at least a valid email address or mobile number.'
                return render(request, 'accounts/update_account.html', context)

            # Validate email format if provided
            if email:
                try:
                    validate_email(email)
                except ValidationError:
                    context['email_error'] = 'Please enter a valid email address.'
                    return render(request, 'accounts/update_account.html', context)


            updated_data = {}
            for field in fields_to_update:
                new_value = request.POST.get(field, '').strip()
                setattr(account, field, new_value)
                if field in ['industry', 'description', 'zone', 'region', 'account_owner', 'city', 'state', 'country']:
                    updated_data[field] = new_value

            # ✅ Always set contact-specific fields (even if blank)
            account.contacts_city = request.POST.get('contacts_city', '').strip()
            account.contacts_state = request.POST.get('contacts_state', '').strip()
            account.contacts_country = request.POST.get('contacts_country', '').strip()

            # ✅ Handle remarks
            remarks = request.POST.get('remarks', '').strip()
            account.remarks = remarks
            # updated_data['remarks'] = remarks

            # Set last modified by
            account.last_modified_by = request.user
            account.save()

            # ✅ Update other Account entries with same account_name
            if account.account_name and updated_data:
                Account.objects.filter(account_name=account.account_name).exclude(pk=account.pk).update(**updated_data)

            # ✅ Update AccountRecords with same account_name
            if account.account_name and updated_data:
                account_records = AccountRecord.objects.filter(account_name=account.account_name)
                for record in account_records:
                    for field in ['industry', 'description', 'zone', 'region', 'account_owner',
                                  'city', 'state', 'country', 'remarks']:
                        if field in updated_data:
                            setattr(record, field, updated_data[field])
                    record.last_modified_by = request.user
                    record.save()

            messages.success(request, 'Contact updated successfully!')

            if source == 'contacts_for_accounts' and account.account_name:
                return redirect('contacts_for_account', account_name=account.account_name)
            return redirect('preview')

        return render(request, 'accounts/update_account.html', {
            'account': account,
            'now': datetime.now().strftime('%Y-%m-%d'),
            'source': source
        })

    except Exception as e:
        print(f"❌ Error in update_account: {str(e)}")
        messages.error(request, 'Error updating contact')
        return redirect('preview')

def update_account_record(request, pk):
    account_record = get_object_or_404(AccountRecord, pk=pk)
    source = request.GET.get('source', 'preview-accounts')

    if request.method == 'POST':
        fields = [
            'account_name', 'industry', 'description',
            'zone', 'region', 'account_owner',
            'city', 'state', 'country', 'phone'
        ]

        updated_data = {}
        for field in fields:
            new_value = request.POST.get(field, '').strip()
            setattr(account_record, field, new_value)
            if field in ['industry', 'zone', 'region', 'account_owner', 'city', 'state', 'country']:
                updated_data[field] = new_value


        account_record.last_modified_by = request.user
        account_record.save()

        # 🟢 Update all Accounts with same account_name
        if account_record.account_name and updated_data:
            Account.objects.filter(account_name=account_record.account_name).update(**updated_data)

        messages.success(request, 'Account record updated successfully!')

        if source == 'contacts_for_accounts':
            return redirect('contacts_for_account', account_name=account_record.account_name)
        else:
            return redirect('preview-accounts')

    initial_data = {
        'industry': account_record.industry,
        'region': account_record.region,
        'zone': account_record.zone,
        'account_owner': account_record.account_owner
    }

    return render(request, 'accounts/update_account.html', {
        'account': account_record,
        'source': source,
        'initial_data': initial_data
    })

from django.http import JsonResponse

def autocomplete_contacts(request):
    term = request.GET.get('q', '')
    results = []

    if term:
        accounts = Account.objects.filter(account_name__icontains=term).order_by('account_name')[:25]
        results = [{
            'label': acc.account_name,
            'value': acc.account_name,
            'text': acc.account_name  # for frontend compatibility
        } for acc in accounts if acc.account_name]

    return JsonResponse(results, safe=False)

from django.db.models import Count
@require_GET

def autocomplete_accounts(request):
    term = request.GET.get("q", "")
    if not term:
        return JsonResponse([], safe=False)

    matches = (
        AccountRecord.objects
        .filter(account_name__icontains=term)
        .values('account_name')
        .annotate(total=Count('id'))  # optional: for uniqueness assurance
        .order_by('account_name')[:1000]
    )

    results = [{"id": m["account_name"], "text": m["account_name"]} for m in matches]
    return JsonResponse(results, safe=False)


from django.http import JsonResponse
from .models import Account, AccountRecord
from django.db.models import Q

def search_contacts(request):
    query = request.GET.get('q', '').strip()

    if query:
        qs = Account.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(account_name__icontains=query) |
            Q(contact_id__icontains=query)
        ).values('id', 'first_name', 'last_name', 'full_name', 'account_name', 'contact_id')[:1000]
    else:
        # Default: return first 1000 records
        qs = Account.objects.all().values('id', 'first_name', 'last_name', 'full_name', 'account_name', 'contact_id')[:1000]

    return JsonResponse({'results': list(qs)})


def search_accounts(request):
    query = request.GET.get('q', '').strip()

    if query:
        qs = AccountRecord.objects.filter(
            Q(account_name__icontains=query) |
            Q(account_id__icontains=query)
        ).values('id', 'account_name', 'account_id')[:1000]
    else:
        # Default: first 1000 records
        qs = AccountRecord.objects.all().values('id', 'account_name', 'account_id')[:1000]

    return JsonResponse({'results': list(qs)})

def logout_view(request):
    logout(request)
    return redirect('login') 
