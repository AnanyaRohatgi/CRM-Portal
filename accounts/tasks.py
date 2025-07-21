import csv
import io
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from .models import Account, AccountRecord
from datetime import datetime
from celery import shared_task

def parse_date(date_str):
    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y-%m-%dT%H:%M', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            continue
    return None

def format_phone(val):
    return ''.join(filter(str.isdigit, val or '')) or None

@shared_task
def process_csv_file(file_path, user_id):
    try:
        user = get_user_model().objects.get(id=user_id)
        file = default_storage.open(file_path, 'r', encoding='utf-8')
        reader = csv.DictReader(file)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        batch_contacts = []
        batch_accounts = []
        batch_size = 1000
        created = 0

        for row_num, raw_row in enumerate(reader, start=2):
            try:
                row = {k.strip(): (v.strip() if v else "") for k, v in raw_row.items()}
                if not any(row.values()):
                    continue

                # Contacts
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
                    mobile=format_phone(row.get('MobilePhone')),
                    other_phone=format_phone(row.get('AlternatePhone')),
                    email=row.get('Email', '') or None,
                    account_id=row.get('Account_Id', ''),
                    contact_id=row.get('Contact_Id') or str(1000000000 + row_num),
                    account_owner=row.get('Account Owner', ''),
                    account_name=row.get('Account_Name', ''),
                    industry=row.get('Industry', ''),
                    region=row.get('REGION', ''),
                    zone=row.get('Zone', ''),
                    created_by_user=user,
                    remarks=row.get('Remarks', ''),
                    created_date=parse_date(row['Contact_CreatedDate']) if row.get('Contact_CreatedDate') else timezone.now().date()
                )
                batch_contacts.append(contact)

                # Accounts
                if not AccountRecord.objects.filter(account_name__iexact=row.get('Account_Name')).exists():
                    account = AccountRecord(
                        account_id=row.get('Account_Id') or str(2000000000 + row_num),
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
                        created_by=user,
                    )
                    batch_accounts.append(account)

                if len(batch_contacts) >= batch_size:
                    Account.objects.bulk_create(batch_contacts)
                    batch_contacts.clear()
                if len(batch_accounts) >= batch_size:
                    AccountRecord.objects.bulk_create(batch_accounts)
                    batch_accounts.clear()

            except Exception as e:
                print(f"❌ Row {row_num} failed: {e}")

        if batch_contacts:
            Account.objects.bulk_create(batch_contacts)
        if batch_accounts:
            AccountRecord.objects.bulk_create(batch_accounts)

        file.close()
        default_storage.delete(file_path)
        print(f"✅ Finished processing CSV upload by {user.get_full_name()}")

    except Exception as e:
        print(f"❌ CSV Task failed: {e}")
