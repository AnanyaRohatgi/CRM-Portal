from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Account
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import DownloadRequest
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q

import csv
import io

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if password == user.password:
                login(request, user)            
                return redirect('setup')
            else:
                messages.error(request, 'Incorrect password.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'accounts/index.html')

import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def setup_view(request):
    accounts = Account.objects.all()

    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            
            print(f"📁 Processing file: {csv_file.name}, Size: {csv_file.size} bytes")

            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect('preview')

            try:
                # Try multiple encodings to handle different file formats
                encodings_to_try = ['utf-8', 'utf-8-sig', 'windows-1252', 'iso-8859-1', 'cp1252']
                decoded_file = None
                encoding_used = None
                
                file_content = csv_file.read()
                
                for encoding in encodings_to_try:
                    try:
                        decoded_file = file_content.decode(encoding)
                        encoding_used = encoding
                        print(f"✅ Successfully decoded file using {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        print(f"❌ Failed to decode with {encoding}")
                        continue
                
                if decoded_file is None:
                    print("❌ Could not decode file with any supported encoding")
                    messages.error(request, "Could not read the file. Please save your CSV with UTF-8 encoding or try a different file format.")
                    return redirect('preview')
                
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]
                accounts_to_create = []
                
                # Enhanced counters and tracking
                processed_count = 0
                error_count = 0
                email_errors = 0
                date_errors = 0
                batch_size = 500  # Reduced batch size for better error isolation
                current_batch_start = 0

                print(f"🔄 Starting to process CSV rows...")

                # Email validation function
                def is_valid_email(email):
                    if not email or email.strip() == '':
                        return True  # Empty emails are allowed
                    try:
                        validate_email(email.strip())
                        return True
                    except ValidationError:
                        return False

                # Enhanced date parsing with better error handling
                def parse_date_flexible(date_str):
                    if not date_str or date_str.strip() == '':
                        return None
                    
                    date_str = date_str.strip()
                    date_formats = [
                        '%Y-%m-%d',    # 2024-05-03
                        '%d-%m-%Y',    # 03-05-2024
                        '%m/%d/%Y',    # 05/03/2024
                        '%d/%m/%Y',    # 03/05/2024
                        '%Y/%m/%d',    # 2024/05/03
                    ]
                    
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            # Validate reasonable year range (1900-2100)
                            if 1900 <= parsed_date.year <= 2100:
                                return parsed_date
                            else:
                                print(f"⚠️  Date {date_str} has unreasonable year {parsed_date.year}, skipping")
                                return None
                        except ValueError:
                            continue
                    
                    print(f"⚠️  Could not parse date: {date_str}")
                    return None

                for i, raw_row in enumerate(reader, start=1):
                    row = {k.strip().lower(): v.strip() for k, v in raw_row.items()}
                    try:
                        # Clean and validate email
                        email = row.get('email', '').strip()
                        if email and not is_valid_email(email):
                            print(f"⚠️  Row {i}: Invalid email '{email}', setting to None")
                            email = None
                            email_errors += 1
                        elif email == '':
                            email = None

                        # Parse dates with error tracking
                        account_created_date_str = row.get('account created date', '')
                        last_updated_str = row.get('last updated', '')
                        
                        account_created_date = parse_date_flexible(account_created_date_str)
                        last_updated = parse_date_flexible(last_updated_str)
                        
                        if account_created_date_str and not account_created_date:
                            date_errors += 1
                        if last_updated_str and not last_updated:
                            date_errors += 1

                        # Build account object with safe field access
                        account = Account(
                            salutation=row.get('salutation', '')[:50] if row.get('salutation', '') else '',  # Limit length
                            first_name=row.get('first name', '')[:50] if row.get('first name', '') else '',
                            last_name=row.get('last name', '')[:50] if row.get('last name', '') else '',
                            title=row.get('title', '')[:100] if row.get('title', '') else '',
                            mailing_street=row.get('mailing street', '')[:200] if row.get('mailing street', '') else '',
                            mailing_city=row.get('mailing city', '')[:50] if row.get('mailing city', '') else '',
                            mailing_state=row.get('mailing state/province', '')[:50] if row.get('mailing state/province', '') else '',
                            mailing_country=row.get('mailing country', '')[:50] if row.get('mailing country', '') else '',
                            mailing_zip=row.get('mailing zip/postal code', '')[:20] if row.get('mailing zip/postal code', '') else '',
                            phone=row.get('phone', '')[:20] if row.get('phone', '') else '',
                            account_phone=row.get('account phone', '')[:20] if row.get('account phone', '') else '',
                            mobile=row.get('mobile', '')[:20] if row.get('mobile', '') else '',
                            fax=row.get('fax', '')[:20] if row.get('fax', '') else '',
                            email=email,
                            account_id=row.get('account id', '')[:50] if row.get('account id', '') else '',
                            account_owner=row.get('account owner', '')[:100] if row.get('account owner', '') else '',
                            account_owner_alias=row.get('account owner alias', '')[:50] if row.get('account owner alias', '') else '',
                            account_name=row.get('account name', '')[:200] if row.get('account name', '') else '',
                            account_created_date=account_created_date,
                            salesperson_sf_id=row.get('salesperson sf id', '')[:50] if row.get('salesperson sf id', '') else '',
                            region=row.get('region', '')[:50] if row.get('region', '') else '',
                            last_updated=last_updated
                        )
                        accounts_to_create.append(account)
                        processed_count += 1
                        
                        # Process in smaller batches with individual record fallback
                        if len(accounts_to_create) >= batch_size:
                            success = False
                            try:
                                print(f"💾 Inserting batch of {len(accounts_to_create)} records (rows {current_batch_start + 1}-{current_batch_start + len(accounts_to_create)})...")
                                Account.objects.bulk_create(accounts_to_create, batch_size=batch_size)
                                print(f"✅ Successfully inserted batch. Total processed: {processed_count}")
                                success = True
                            except Exception as batch_error:
                                print(f"❌ BATCH INSERT ERROR: {str(batch_error)}")
                                print(f"🔄 Attempting to insert records individually...")
                                
                                # Fallback: insert records one by one to identify problematic records
                                individual_success = 0
                                for idx, account in enumerate(accounts_to_create):
                                    try:
                                        account.save()
                                        individual_success += 1
                                    except Exception as individual_error:
                                        error_count += 1
                                        row_number = current_batch_start + idx + 1
                                        print(f"❌ ROW {row_number} INDIVIDUAL ERROR: {str(individual_error)}")
                                        if error_count <= 20:  # Show first 20 individual errors
                                            messages.warning(request, f"Row {row_number} error: {str(individual_error)[:100]}...")
                                
                                print(f"✅ Individual insert: {individual_success}/{len(accounts_to_create)} successful")
                                success = True  # Continue processing even if some individual records fail
                            
                            if success:
                                current_batch_start += len(accounts_to_create)
                                accounts_to_create = []  # Clear the batch

                        # Progress logging for large files
                        if i % 5000 == 0:
                            print(f"📊 Processed {i} rows so far... (Errors: {error_count}, Email errors: {email_errors}, Date errors: {date_errors})")

                    except Exception as row_error:
                        error_count += 1
                        print(f"❌ ROW {i} ERROR: {str(row_error)}")
                        if error_count <= 20:
                            messages.warning(request, f"Row {i} error: {str(row_error)[:100]}...")
                        elif error_count == 21:
                            messages.info(request, "More than 20 errors found... check console for details")
                        continue

                # Insert remaining records
                if accounts_to_create:
                    try:
                        print(f"💾 Inserting final batch of {len(accounts_to_create)} records...")
                        Account.objects.bulk_create(accounts_to_create, batch_size=batch_size)
                        print(f"✅ Successfully inserted final batch.")
                    except Exception as final_error:
                        print(f"❌ FINAL BATCH ERROR: {str(final_error)}")
                        print(f"🔄 Attempting to insert final records individually...")
                        
                        # Fallback for final batch
                        individual_success = 0
                        for idx, account in enumerate(accounts_to_create):
                            try:
                                account.save()
                                individual_success += 1
                            except Exception as individual_error:
                                error_count += 1
                                row_number = current_batch_start + idx + 1
                                print(f"❌ ROW {row_number} FINAL INDIVIDUAL ERROR: {str(individual_error)}")
                        
                        print(f"✅ Final individual insert: {individual_success}/{len(accounts_to_create)} successful")

                # Enhanced final summary
                total_inserted = processed_count - error_count
                print(f"🎉 PROCESSING COMPLETE:")
                print(f"   📝 Total rows processed: {processed_count}")
                print(f"   ✅ Successfully inserted: {total_inserted}")
                print(f"   ❌ Total errors: {error_count}")
                print(f"   📧 Email validation errors: {email_errors}")
                print(f"   📅 Date parsing errors: {date_errors}")
                
                if total_inserted > 0:
                    messages.success(request, f"Successfully uploaded {total_inserted} accounts.")
                if error_count > 0:
                    messages.warning(request, f"{error_count} rows had errors and were skipped.")
                if email_errors > 0:
                    messages.info(request, f"{email_errors} invalid emails were cleaned/removed.")
                if date_errors > 0:
                    messages.info(request, f"{date_errors} dates could not be parsed and were left empty.")
                    
                return redirect('preview')

            except UnicodeDecodeError as decode_error:
                print(f"❌ FILE ENCODING ERROR: {str(decode_error)}")
                messages.error(request, f"File encoding error. Please save your CSV as UTF-8. Error: {str(decode_error)}")
                return redirect('preview')
            except MemoryError as mem_error:
                print(f"❌ MEMORY ERROR: {str(mem_error)}")
                messages.error(request, "File too large - insufficient memory. Try splitting your file into smaller chunks.")
                return redirect('preview')
            except Exception as general_error:
                print(f"❌ GENERAL ERROR: {str(general_error)}")
                print(f"❌ ERROR TYPE: {type(general_error).__name__}")
                messages.error(request, f"CSV Processing Error: {str(general_error)}")
                return redirect('preview')

        else:
    # FIXED MANUAL FORM ENTRY WITH CORRECT DATE PARSING
            try:
                print(f"🔍 DEBUG: Starting manual account creation...")
                print(f"🔍 DEBUG: POST data received: {request.POST}")
                
                # FIXED: Parse dates with multiple format support
                account_created_date = None
                last_updated = None
                
                def parse_date_from_form(date_string, field_name):
                    """Parse date from form with multiple format support"""
                    if not date_string:
                        return None
                        
                    # Try multiple formats
                    date_formats = [
                        '%Y-%m-%d',        # 2025-06-07 (HTML date input format)
                        '%d-%m-%Y',        # 07-06-2025 (your original format)
                        '%Y-%m-%dT%H:%M',  # 2025-06-15T16:56 (datetime-local input)
                        '%d/%m/%Y',        # 07/06/2025
                        '%m/%d/%Y',        # 06/07/2025
                    ]
                    
                    for fmt in date_formats:
                        try:
                            if 'T' in fmt:
                                # For datetime-local inputs, extract just the date part
                                parsed_datetime = datetime.strptime(date_string, fmt)
                                return parsed_datetime.date()
                            else:
                                return datetime.strptime(date_string, fmt).date()
                        except ValueError:
                            continue
                    
                    print(f"❌ DEBUG: Could not parse {field_name}: '{date_string}'")
                    return None

                # Parse account created date
                if request.POST.get('account_created_date'):
                    account_created_date = parse_date_from_form(
                        request.POST.get('account_created_date'), 
                        'account_created_date'
                    )
                    print(f"🔍 DEBUG: Parsed account_created_date: {account_created_date}")
                    
                    if request.POST.get('account_created_date') and not account_created_date:
                        messages.error(request, f"Invalid Account Created Date format: {request.POST.get('account_created_date')}")
                        return redirect('setup')

                # Parse last updated date
                if request.POST.get('last_updated'):
                    last_updated = parse_date_from_form(
                        request.POST.get('last_updated'), 
                        'last_updated'
                    )
                    print(f"🔍 DEBUG: Parsed last_updated: {last_updated}")
                    
                    if request.POST.get('last_updated') and not last_updated:
                        messages.error(request, f"Invalid Last Updated format: {request.POST.get('last_updated')}")
                        return redirect('setup')

                # Create the account object
                account_data = {
                    'salutation': request.POST.get('salutation', '').strip(),
                    'first_name': request.POST.get('first_name', '').strip(),
                    'last_name': request.POST.get('last_name', '').strip(),
                    'title': request.POST.get('title', '').strip(),
                    'mailing_street': request.POST.get('mailing_street', '').strip(),
                    'mailing_city': request.POST.get('mailing_city', '').strip(),
                    'mailing_state': request.POST.get('mailing_state', '').strip(),
                    'mailing_country': request.POST.get('mailing_country', '').strip(),
                    'mailing_zip': request.POST.get('mailing_zip', '').strip(),
                    'phone': request.POST.get('phone', '').strip(),
                    'account_phone': request.POST.get('account_phone', '').strip(),
                    'mobile': request.POST.get('mobile', '').strip(),
                    'fax': request.POST.get('fax', '').strip(),
                    'email': request.POST.get('email', '').strip() or None,
                    'account_id': request.POST.get('account_id', '').strip(),
                    'account_owner': request.POST.get('account_owner', '').strip(),
                    'account_owner_alias': request.POST.get('account_owner_alias', '').strip(),
                    'account_name': request.POST.get('account_name', '').strip(),
                    'account_created_date': account_created_date,
                    'salesperson_sf_id': request.POST.get('salesperson_sf_id', '').strip(),
                    'region': request.POST.get('region', '').strip(),
                    'last_updated': last_updated
                }
                
                print(f"🔍 DEBUG: Account data to be saved: {account_data}")
                
                account = Account(**account_data)
                
                # Validate before saving
                try:
                    account.full_clean()  # This will run model validation
                    print(f"🔍 DEBUG: Account validation passed")
                except ValidationError as validation_error:
                    print(f"❌ DEBUG: Validation error: {validation_error}")
                    messages.error(request, f"Validation error: {validation_error}")
                    return redirect('setup')
                
                # Save and verify
                print(f"🔍 DEBUG: About to save account...")
                account.save()
                print(f"✅ DEBUG: Account saved successfully with ID: {account.pk}")
                print(f"✅ DEBUG: Account contact_id: {getattr(account, 'contact_id', 'No contact_id field')}")
                
                # Verify the account was actually saved
                try:
                    saved_account = Account.objects.get(pk=account.pk)
                    print(f"✅ DEBUG: Verified account exists in database: {saved_account}")
                    print(f"✅ DEBUG: Account details: {saved_account.first_name} {saved_account.last_name}")
                except Account.DoesNotExist:
                    print(f"❌ DEBUG: Account was not found in database after save!")
                    messages.error(request, "Account was not saved properly")
                    return redirect('setup')
                
                # Check total count
                total_accounts = Account.objects.count()
                print(f"🔍 DEBUG: Total accounts in database: {total_accounts}")
                
                messages.success(request, f"Account '{account.first_name} {account.last_name}' added successfully! Total accounts: {total_accounts}")
                
                return redirect('preview')
                
            except Exception as e:
                print(f"❌ DEBUG: Exception in manual account creation: {str(e)}")
                print(f"❌ DEBUG: Exception type: {type(e).__name__}")
                import traceback
                print(f"❌ DEBUG: Full traceback:\n{traceback.format_exc()}")
                messages.error(request, f"Error saving account: {str(e)}")
                return redirect('setup')


    return render(request, "accounts/setup.html", {'accounts': accounts})

def delete_all_accounts(request):
    if request.method == 'POST':
        Account.objects.all().delete()
        messages.success(request, "All accounts have been deleted.")
    return redirect('preview')  # redirect back to preview page

def delete_account(request, contact_id):
    if request.method == 'POST':
        account = get_object_or_404(Account, contact_id=contact_id)
        account.delete()
        messages.success(request, "Account deleted successfully.")
    return redirect('preview')

def update_account(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == 'POST':
        account.salutation = request.POST.get('salutation', '')
        account.first_name = request.POST.get('first_name', '')
        account.last_name = request.POST.get('last_name', '')
        account.title = request.POST.get('title', '')
        account.mailing_street = request.POST.get('mailing_street', '')
        account.mailing_city = request.POST.get('mailing_city', '')
        account.mailing_state = request.POST.get('mailing_state', '')
        account.mailing_zip = request.POST.get('mailing_zip', '')
        account.mailing_country = request.POST.get('mailing_country', '')
        account.phone = request.POST.get('phone', '')
        account.account_phone = request.POST.get('account_phone', '')
        account.mobile = request.POST.get('mobile', '')
        account.fax = request.POST.get('fax', '')
        account.email = request.POST.get('email', '')
        account.account_id = request.POST.get('account_id', '')
        account.account_name = request.POST.get('account_name', '')
        account.account_owner = request.POST.get('account_owner', '')
        account.account_owner_alias = request.POST.get('account_owner_alias', '')
        account.salesperson_sf_id = request.POST.get('salesperson_sf_id', '')
        account.region = request.POST.get('region', '')
        account.account_created_date = request.POST.get('account_created_date') or None

        account.save()
        return redirect('preview')

    return render(request, 'accounts/update_account.html', {'account': account})

from django.core.paginator import Paginator

def preview_view(request):
    search_query = request.GET.get('search', '')
    accounts = Account.objects.all().order_by('contact_id')  # Default ordering
    
    if search_query:
        accounts = accounts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(account_id__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(mobile__icontains=search_query)
        )
    
    paginator = Paginator(accounts, 100)  # Show 100 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'accounts': page_obj,
        'search_query': search_query,
        'total_accounts': paginator.count,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else 1,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else paginator.num_pages,
    }
    
    # Calculate page range for pagination (show 5 pages around current)
    page_range = []
    for i in range(max(1, page_obj.number - 2), min(paginator.num_pages + 1, page_obj.number + 3)):
        page_range.append(i)
    context['page_range'] = page_range
    
    return render(request, "accounts/preview.html", context)

def download_accounts_csv(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Missing token.")

    try:
        download_request = DownloadRequest.objects.get(token=token)
    except DownloadRequest.DoesNotExist:
        return HttpResponse("Invalid token.")

    if download_request.status != "approved":
        return HttpResponse("Download not approved yet.")

    # CSV download logic below
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Contact ID', 'Salutation', 'First Name', 'Last Name', 'Title',
        'Mailing Street', 'Mailing City', 'Mailing State', 'Mailing Zip',
        'Mailing Country', 'Phone', 'Account Phone', 'Mobile', 'Fax',
        'Email', 'Account ID', 'Account Name', 'Account Owner',
        'Account Owner Alias', 'Salesperson SF ID', 'Account Created Date',
        'Region', 'Last Updated'
    ])

    for account in Account.objects.all():
        writer.writerow([
            account.contact_id, account.salutation, account.first_name,
            account.last_name, account.title, account.mailing_street,
            account.mailing_city, account.mailing_state, account.mailing_zip,
            account.mailing_country, account.phone, account.account_phone,
            account.mobile, account.fax, account.email, account.account_id,
            account.account_name, account.account_owner, account.account_owner_alias,
            account.salesperson_sf_id, account.account_created_date,
            account.region, account.last_updated
        ])

    return response

def request_download(request):
    if request.method == "POST":
        try:
            download_request = DownloadRequest.objects.create(requested_by=request.user.email)

            approve_link = request.build_absolute_uri(reverse("approve_download", args=[download_request.token]))
            reject_link = request.build_absolute_uri(reverse("reject_download", args=[download_request.token]))

            email_body = render_to_string("accounts/approval_email.html", {
                "approve_link": approve_link,
                "reject_link": reject_link,
                "user_email": request.user.email
            })

            send_mail(
                subject="Approval Needed: CSV Download Request",
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["ananya.r@iconresources.com"],
                html_message=email_body
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, "Your download request has been sent for approval. You will receive an email with the download link once approved.")
            return redirect('preview')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            messages.error(request, f"Error submitting request: {str(e)}")
            return redirect('preview')

    return redirect('preview')


def approve_download(request, token):
    download_req = get_object_or_404(DownloadRequest, token=token)
    download_req.status = "approved"
    download_req.save()
    
    # Send download link to the user who requested it
    download_link = request.build_absolute_uri(reverse("download_accounts_csv")) + f"?token={token}"
    
    try:
        send_mail(
            subject="CSV Download Approved - Download Link Inside",
            message=f"""
Hello,

Your CSV download request has been approved!

Click the link below to download your data:
{download_link}

This link is valid for this download session.

Best regards,
System Admin
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[download_req.requested_by],
        )
        
        return HttpResponse("✅ Download Approved. The user has been notified via email with the download link.")
    except Exception as e:
        return HttpResponse(f"✅ Download Approved, but failed to send email to user: {str(e)}")

def reject_download(request, token):
    download_req = get_object_or_404(DownloadRequest, token=token)
    download_req.status = "rejected"
    download_req.save()
    
    # Optionally notify the user about rejection
    try:
        send_mail(
            subject="CSV Download Request Rejected",
            message=f"""
Hello,

Your CSV download request has been rejected.

If you believe this was an error, please contact your administrator.

Best regards,
System Admin
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[download_req.requested_by],
        )
        
        return HttpResponse("❌ Download Rejected. The user has been notified via email.")
    except Exception as e:
        return HttpResponse(f"❌ Download Rejected, but failed to send email to user: {str(e)}")
    
def home_view(request):
    return render(request, "accounts/home.html")